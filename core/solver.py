"""Constraint programming solver for workplan feasibility analysis."""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from ortools.sat.python import cp_model

from .models import Project, Activity, ResourceCapacity, AnalysisResult, Occurrence


class WorkplanSolver:
    """CP-SAT solver for workplan feasibility analysis."""
    
    def __init__(self):
        self.model = None
        self.solver = None
        self.variables = {}
        self.constraints = []
        
        # Constants from specification
        self.SLOTS_PER_DAY = 4
        self.HOURS_PER_SLOT = 2
        self.TOTAL_DAYS = 60
        self.TOTAL_SLOTS = self.TOTAL_DAYS * self.SLOTS_PER_DAY  # 240 slots
        
        # Role names mapping
        self.ROLES = ["RangerCoordinator", "SeniorRanger", "Ranger"]
    
    def analyze_project(self, project: Project, time_limit_seconds: int = 30) -> AnalysisResult:
        """
        Analyze project feasibility using constraint programming.
        
        Args:
            project: Project to analyze
            time_limit_seconds: Maximum solve time
            
        Returns:
            AnalysisResult with feasibility verdict and metrics
        """
        start_time = time.time()
        
        try:
            # Expand activities into occurrences
            occurrences = self._expand_activities(project.activities)
            
            # Create CP-SAT model
            self.model = cp_model.CpModel()
            self.solver = cp_model.CpSolver()
            self.solver.parameters.max_time_in_seconds = time_limit_seconds
            
            # Create variables
            self._create_variables(occurrences)
            
            # Add constraints
            self._add_scheduling_constraints(occurrences)
            self._add_capacity_constraints(occurrences, project.current_resources)
            
            # Solve the model
            solve_start = time.time()
            status = self.solver.Solve(self.model)
            solve_time = time.time() - solve_start
            
            # Process results
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                # Feasible solution found
                utilization = self._calculate_utilization(occurrences, project.current_resources)
                
                return AnalysisResult(
                    timestamp=datetime.now(),
                    feasible=True,
                    utilization=utilization,
                    overloads=[],
                    solver_stats={
                        "status": "FEASIBLE" if status == cp_model.FEASIBLE else "OPTIMAL",
                        "solve_time": solve_time,
                        "num_variables": len(self.variables),
                        "num_constraints": len(self.constraints),
                        "wall_time": self.solver.WallTime(),
                        "user_time": self.solver.UserTime()
                    },
                    resource_capacity=project.current_resources
                )
            
            elif status == cp_model.INFEASIBLE:
                # Infeasible - run overload analysis
                overloads, utilization = self._analyze_overloads(occurrences, project.current_resources)
                
                return AnalysisResult(
                    timestamp=datetime.now(),
                    feasible=False,
                    utilization=utilization,
                    overloads=overloads,
                    solver_stats={
                        "status": "INFEASIBLE",
                        "solve_time": solve_time,
                        "num_variables": len(self.variables),
                        "num_constraints": len(self.constraints),
                        "wall_time": self.solver.WallTime(),
                        "user_time": self.solver.UserTime()
                    },
                    resource_capacity=project.current_resources
                )
            
            else:
                # Unknown or timeout
                status_name = {
                    cp_model.UNKNOWN: "UNKNOWN",
                    cp_model.MODEL_INVALID: "MODEL_INVALID"
                }.get(status, f"STATUS_{status}")
                
                return AnalysisResult(
                    timestamp=datetime.now(),
                    feasible=False,
                    utilization={},
                    overloads=[],
                    solver_stats={
                        "status": status_name,
                        "solve_time": solve_time,
                        "num_variables": len(self.variables),
                        "num_constraints": len(self.constraints),
                        "wall_time": self.solver.WallTime(),
                        "user_time": self.solver.UserTime()
                    },
                    resource_capacity=project.current_resources
                )
                
        except Exception as e:
            # Handle solver errors
            total_time = time.time() - start_time
            return AnalysisResult(
                timestamp=datetime.now(),
                feasible=False,
                utilization={},
                overloads=[],
                solver_stats={
                    "status": f"ERROR: {str(e)}",
                    "solve_time": total_time,
                    "num_variables": 0,
                    "num_constraints": 0
                },
                resource_capacity=project.current_resources
            )
    
    def _expand_activities(self, activities: List[Activity]) -> List[Occurrence]:
        """Expand activities into individual occurrences based on frequency."""
        occurrences = []
        
        for activity in activities:
            for i in range(activity.frequency):
                occurrence = Occurrence(
                    activity=activity,
                    occurrence_index=i
                )
                occurrences.append(occurrence)
        
        return occurrences
    
    def _create_variables(self, occurrences: List[Occurrence]):
        """Create CP-SAT variables for scheduling."""
        self.variables = {}
        
        # Boolean variables: start[occurrence_id, slot] = 1 if occurrence starts at slot
        for i, occurrence in enumerate(occurrences):
            occurrence_vars = {}
            duration_slots = occurrence.duration_slots
            
            # Can only start in slots that allow completion within the time horizon
            max_start_slot = self.TOTAL_SLOTS - duration_slots
            
            for slot in range(max_start_slot + 1):
                var_name = f"start_{i}_{slot}"
                occurrence_vars[slot] = self.model.NewBoolVar(var_name)
            
            self.variables[i] = occurrence_vars
    
    def _add_scheduling_constraints(self, occurrences: List[Occurrence]):
        """Add constraints ensuring each occurrence is scheduled exactly once."""
        for i, occurrence in enumerate(occurrences):
            # Each occurrence must start exactly once
            constraint = self.model.Add(
                sum(self.variables[i].values()) == 1
            )
            self.constraints.append(constraint)
    
    def _add_capacity_constraints(self, occurrences: List[Occurrence], resources: ResourceCapacity):
        """Add resource capacity constraints."""
        # Get capacity for each role
        capacities = {
            "RangerCoordinator": resources.ranger_coordinator,
            "SeniorRanger": resources.senior_ranger,
            "Ranger": resources.ranger
        }
        
        # For each slot and each role, ensure capacity is not exceeded
        for slot in range(self.TOTAL_SLOTS):
            # Skip public holidays
            if self._is_public_holiday(slot, resources.public_holidays):
                # Force no work on public holidays
                for i, occurrence in enumerate(occurrences):
                    duration_slots = occurrence.duration_slots
                    # If this occurrence would overlap with the holiday slot
                    for start_slot in range(max(0, slot - duration_slots + 1), slot + 1):
                        if start_slot in self.variables[i]:
                            constraint = self.model.Add(self.variables[i][start_slot] == 0)
                            self.constraints.append(constraint)
                continue
            
            for role in self.ROLES:
                # Sum demand for this role at this slot
                role_demand = []
                
                for i, occurrence in enumerate(occurrences):
                    demand = occurrence.resource_demands.get(role, 0)
                    if demand > 0:
                        duration_slots = occurrence.duration_slots
                        
                        # Check which start slots would cause this occurrence to be active at current slot
                        for start_slot in range(max(0, slot - duration_slots + 1), slot + 1):
                            if start_slot in self.variables[i]:
                                role_demand.append(self.variables[i][start_slot] * demand)
                
                if role_demand:
                    constraint = self.model.Add(sum(role_demand) <= capacities[role])
                    self.constraints.append(constraint)
    
    def _is_public_holiday(self, slot: int, public_holidays: List[str]) -> bool:
        """Check if a slot falls on a public holiday."""
        if not public_holidays:
            return False
        
        # Convert slot to date (assuming start date is today for simplicity)
        day = slot // self.SLOTS_PER_DAY
        slot_date = datetime.now().date() + timedelta(days=day)
        date_str = slot_date.strftime("%Y-%m-%d")
        
        return date_str in public_holidays
    
    def _calculate_utilization(self, occurrences: List[Occurrence], resources: ResourceCapacity) -> Dict[str, float]:
        """Calculate resource utilization percentages."""
        # Total available capacity over the planning horizon
        total_capacity = {
            "RangerCoordinator": resources.ranger_coordinator * self.TOTAL_SLOTS,
            "SeniorRanger": resources.senior_ranger * self.TOTAL_SLOTS,
            "Ranger": resources.ranger * self.TOTAL_SLOTS
        }
        
        # Total demand (sum of all occurrence demands)
        total_demand = {"RangerCoordinator": 0, "SeniorRanger": 0, "Ranger": 0}
        
        for occurrence in occurrences:
            duration_slots = occurrence.duration_slots
            demands = occurrence.resource_demands
            
            for role in self.ROLES:
                total_demand[role] += demands.get(role, 0) * duration_slots
        
        # Calculate utilization percentages
        utilization = {}
        for role in self.ROLES:
            if total_capacity[role] > 0:
                utilization[role] = (total_demand[role] / total_capacity[role]) * 100.0
            else:
                utilization[role] = 0.0
        
        return utilization
    
    def _analyze_overloads(self, occurrences: List[Occurrence], resources: ResourceCapacity) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
        """Analyze capacity overloads when the problem is infeasible."""
        # For now, return basic overload analysis
        # In a full implementation, this would solve a relaxed model with slack variables
        
        utilization = self._calculate_utilization(occurrences, resources)
        
        overloads = []
        for role in self.ROLES:
            if utilization[role] > 100:
                # Simple overload detection - in reality this would be more sophisticated
                overload_amount = utilization[role] - 100
                if role == "RangerCoordinator":
                    capacity = resources.ranger_coordinator
                elif role == "SeniorRanger":
                    capacity = resources.senior_ranger
                else:  # Ranger
                    capacity = resources.ranger
                extra_needed = int((overload_amount / 100) * capacity) + 1
                
                overloads.append({
                    "date": "Multiple days",
                    "slot": "Various",
                    "role": role,
                    "extra_needed": extra_needed
                })
        
        return overloads, utilization
    
    def get_schedule(self, occurrences: List[Occurrence]) -> Optional[Dict[int, List[Tuple[int, str]]]]:
        """
        Extract the schedule from the solved model.
        
        Returns:
            Dictionary mapping slot -> [(occurrence_index, activity_name), ...]
        """
        if not self.solver or not self.variables:
            return None
        
        schedule = {}
        
        for i, occurrence in enumerate(occurrences):
            duration_slots = occurrence.duration_slots
            
            # Find which slot this occurrence starts at
            for slot, var in self.variables[i].items():
                if self.solver.Value(var) == 1:
                    # This occurrence starts at this slot
                    for s in range(slot, slot + duration_slots):
                        if s not in schedule:
                            schedule[s] = []
                        schedule[s].append((i, occurrence.activity.name))
                    break
        
        return schedule
