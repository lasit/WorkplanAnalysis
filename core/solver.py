"""Constraint programming solver for workplan feasibility analysis."""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from ortools.sat.python import cp_model

from .models import Project, Activity, ResourceCapacity, AnalysisResult, Occurrence, InfeasibilityDiagnostics


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
        
        # Dynamic values set per project
        self.TOTAL_DAYS = 60  # Default fallback
        self.TOTAL_SLOTS = 240  # Default fallback
        self.working_days = []  # Actual working days for the quarter
        
        # Role names mapping (will be dynamic based on project resources)
        self.ROLES = ["RangerCoordinator", "SeniorRanger", "Ranger"]  # Default fallback
    
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
            # Set up quarter-based planning horizon
            self._setup_planning_horizon(project)
            
            # Get valid activities for the planning quarter
            valid_activities, excluded_activities = project.get_valid_activities()
            
            if excluded_activities:
                print(f"Note: {len(excluded_activities)} activities excluded (wrong quarter)")
            
            # Expand valid activities into occurrences
            occurrences = self._expand_activities(valid_activities)
            
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
                # Infeasible - run comprehensive diagnostic analysis
                overloads, utilization = self._analyze_overloads(occurrences, project.current_resources)
                diagnostics = self._analyze_infeasibility(occurrences, project.current_resources, utilization)
                
                return AnalysisResult(
                    timestamp=datetime.now(),
                    feasible=False,
                    utilization=utilization,
                    overloads=overloads,  # Keep for backward compatibility
                    solver_stats={
                        "status": "INFEASIBLE",
                        "solve_time": solve_time,
                        "num_variables": len(self.variables),
                        "num_constraints": len(self.constraints),
                        "wall_time": self.solver.WallTime(),
                        "user_time": self.solver.UserTime()
                    },
                    resource_capacity=project.current_resources,
                    infeasibility_diagnostics=diagnostics
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
        # Get all resource types from the project
        all_resources = resources.get_all_resources()
        self.ROLES = list(all_resources.keys())  # Update roles dynamically
        
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
                    demand = occurrence.activity.get_resource_requirement(role)
                    if demand > 0:
                        duration_slots = occurrence.duration_slots
                        
                        # Check which start slots would cause this occurrence to be active at current slot
                        for start_slot in range(max(0, slot - duration_slots + 1), slot + 1):
                            if start_slot in self.variables[i]:
                                role_demand.append(self.variables[i][start_slot] * demand)
                
                if role_demand:
                    capacity = all_resources.get(role, 0)
                    constraint = self.model.Add(sum(role_demand) <= capacity)
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
        # Get all resource types dynamically
        all_resources = resources.get_all_resources()
        
        # Total available capacity over the planning horizon
        total_capacity = {}
        for role, capacity in all_resources.items():
            total_capacity[role] = capacity * self.TOTAL_SLOTS
        
        # Total demand (sum of all occurrence demands)
        total_demand = {role: 0 for role in all_resources.keys()}
        
        for occurrence in occurrences:
            duration_slots = occurrence.duration_slots
            
            for role in all_resources.keys():
                demand = occurrence.activity.get_resource_requirement(role)
                total_demand[role] += demand * duration_slots
        
        # Calculate utilization percentages
        utilization = {}
        for role in all_resources.keys():
            if total_capacity[role] > 0:
                utilization[role] = (total_demand[role] / total_capacity[role]) * 100.0
            else:
                utilization[role] = 0.0
        
        return utilization
    
    def _analyze_overloads(self, occurrences: List[Occurrence], resources: ResourceCapacity) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
        """Analyze capacity overloads when the problem is infeasible."""
        # Calculate utilization for all resource types
        utilization = self._calculate_utilization(occurrences, resources)
        
        # Get all resource types dynamically
        all_resources = resources.get_all_resources()
        
        overloads = []
        for role, capacity in all_resources.items():
            if utilization.get(role, 0) > 100:
                # Simple overload detection - in reality this would be more sophisticated
                overload_amount = utilization[role] - 100
                extra_needed = int((overload_amount / 100) * capacity) + 1
                
                overloads.append({
                    "date": "Multiple days",
                    "slot": "Various",
                    "role": role,
                    "extra_needed": extra_needed
                })
        
        return overloads, utilization
    
    def _analyze_infeasibility(self, occurrences: List[Occurrence], resources: ResourceCapacity, utilization: Dict[str, float]) -> InfeasibilityDiagnostics:
        """Perform comprehensive infeasibility analysis."""
        diagnostics = InfeasibilityDiagnostics()
        
        # Analyze resource overloads
        resource_overloads = self._analyze_resource_overloads(occurrences, resources, utilization)
        diagnostics.resource_overloads = resource_overloads
        
        # Analyze scheduling conflicts
        scheduling_conflicts = self._analyze_scheduling_conflicts(occurrences, resources)
        diagnostics.scheduling_conflicts = scheduling_conflicts
        
        # Analyze invalid configurations
        invalid_configurations = self._analyze_invalid_configurations(occurrences, resources)
        diagnostics.invalid_configurations = invalid_configurations
        
        # Analyze constraint violations
        constraint_violations = self._analyze_constraint_violations(occurrences, resources)
        diagnostics.constraint_violations = constraint_violations
        
        # Determine primary reason and severity
        diagnostics.primary_reason, diagnostics.severity = self._determine_primary_reason(
            resource_overloads, scheduling_conflicts, invalid_configurations, constraint_violations
        )
        
        # Generate recommendations
        diagnostics.recommendations = self._generate_recommendations(
            resource_overloads, scheduling_conflicts, invalid_configurations, constraint_violations, utilization
        )
        
        return diagnostics
    
    def _analyze_resource_overloads(self, occurrences: List[Occurrence], resources: ResourceCapacity, utilization: Dict[str, float]) -> List[Dict[str, Any]]:
        """Analyze resource capacity overloads in detail."""
        overloads = []
        all_resources = resources.get_all_resources()
        
        for role, capacity in all_resources.items():
            util = utilization.get(role, 0)
            if util > 100:
                # Calculate detailed overload information
                overload_percentage = util - 100
                total_demand = sum(
                    occurrence.activity.get_resource_requirement(role) * occurrence.duration_slots
                    for occurrence in occurrences
                )
                total_capacity = capacity * self.TOTAL_SLOTS
                excess_demand = total_demand - total_capacity
                
                # Calculate minimum additional staff needed
                min_additional_staff = max(1, int(excess_demand / self.TOTAL_SLOTS) + 1)
                
                overloads.append({
                    "type": "resource_overload",
                    "role": role,
                    "current_capacity": capacity,
                    "utilization_percentage": util,
                    "overload_percentage": overload_percentage,
                    "total_demand": total_demand,
                    "total_capacity": total_capacity,
                    "excess_demand": excess_demand,
                    "min_additional_staff": min_additional_staff,
                    "severity": "Critical" if util > 150 else "High" if util > 120 else "Moderate"
                })
        
        return overloads
    
    def _analyze_scheduling_conflicts(self, occurrences: List[Occurrence], resources: ResourceCapacity) -> List[Dict[str, Any]]:
        """Analyze scheduling conflicts that prevent feasible solutions."""
        conflicts = []
        
        # Check for activities that require more resources than available
        all_resources = resources.get_all_resources()
        
        for occurrence in occurrences:
            for role, demand in occurrence.activity.get_all_resource_requirements().items():
                capacity = all_resources.get(role, 0)
                if demand > capacity:
                    conflicts.append({
                        "type": "impossible_activity",
                        "activity_id": occurrence.activity.activity_id,
                        "activity_name": occurrence.activity.name,
                        "role": role,
                        "demand": demand,
                        "capacity": capacity,
                        "deficit": demand - capacity,
                        "severity": "Critical",
                        "description": f"Activity '{occurrence.activity.name}' requires {demand} {role} but only {capacity} available"
                    })
        
        # Check for time horizon constraints
        total_activity_time = sum(occurrence.duration_slots for occurrence in occurrences)
        if total_activity_time > self.TOTAL_SLOTS:
            conflicts.append({
                "type": "time_horizon_exceeded",
                "total_activity_slots": total_activity_time,
                "available_slots": self.TOTAL_SLOTS,
                "excess_slots": total_activity_time - self.TOTAL_SLOTS,
                "severity": "High",
                "description": f"Total activity time ({total_activity_time} slots) exceeds available time ({self.TOTAL_SLOTS} slots)"
            })
        
        return conflicts
    
    def _analyze_invalid_configurations(self, occurrences: List[Occurrence], resources: ResourceCapacity) -> List[Dict[str, Any]]:
        """Analyze invalid activity configurations."""
        invalid_configs = []
        
        # Check for activities with zero resource requirements
        for occurrence in occurrences:
            total_resources = sum(occurrence.activity.get_all_resource_requirements().values())
            if total_resources == 0:
                invalid_configs.append({
                    "type": "zero_resources",
                    "activity_id": occurrence.activity.activity_id,
                    "activity_name": occurrence.activity.name,
                    "severity": "Low",
                    "description": f"Activity '{occurrence.activity.name}' requires no resources"
                })
        
        # Check for excessive frequency
        activity_frequencies = {}
        for occurrence in occurrences:
            activity_id = occurrence.activity.activity_id
            if activity_id not in activity_frequencies:
                activity_frequencies[activity_id] = {
                    "activity": occurrence.activity,
                    "count": 0
                }
            activity_frequencies[activity_id]["count"] += 1
        
        for activity_id, info in activity_frequencies.items():
            activity = info["activity"]
            count = info["count"]
            duration_slots = int(activity.duration * 4)  # Convert duration to slots
            max_possible = self.TOTAL_SLOTS // duration_slots if duration_slots > 0 else 0
            
            if count > max_possible:
                invalid_configs.append({
                    "type": "excessive_frequency",
                    "activity_id": activity_id,
                    "activity_name": activity.name,
                    "frequency": count,
                    "max_possible": max_possible,
                    "excess": count - max_possible,
                    "severity": "High",
                    "description": f"Activity '{activity.name}' frequency ({count}) exceeds maximum possible ({max_possible})"
                })
        
        return invalid_configs
    
    def _analyze_constraint_violations(self, occurrences: List[Occurrence], resources: ResourceCapacity) -> List[Dict[str, Any]]:
        """Analyze other constraint programming violations."""
        violations = []
        
        # Check for resource type mismatches
        activity_resources = set()
        for occurrence in occurrences:
            activity_resources.update(occurrence.activity.get_all_resource_requirements().keys())
        
        available_resources = set(resources.get_all_resources().keys())
        missing_resources = activity_resources - available_resources
        
        if missing_resources:
            violations.append({
                "type": "missing_resource_types",
                "missing_resources": list(missing_resources),
                "severity": "Critical",
                "description": f"Activities require resource types not defined in capacity: {', '.join(missing_resources)}"
            })
        
        return violations
    
    def _determine_primary_reason(self, resource_overloads: List[Dict[str, Any]], 
                                 scheduling_conflicts: List[Dict[str, Any]], 
                                 invalid_configurations: List[Dict[str, Any]], 
                                 constraint_violations: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Determine the primary reason for infeasibility and its severity."""
        
        # Priority order: Critical violations > Resource overloads > Scheduling conflicts > Invalid configs
        
        # Check for critical violations first
        critical_violations = [
            item for item in constraint_violations + scheduling_conflicts + invalid_configurations
            if item.get("severity") == "Critical"
        ]
        
        if critical_violations:
            if any(item.get("type") == "missing_resource_types" for item in critical_violations):
                return "Missing Resource Types", "Critical"
            elif any(item.get("type") == "impossible_activity" for item in critical_violations):
                return "Impossible Activity Requirements", "Critical"
            else:
                return "Critical Configuration Error", "Critical"
        
        # Check for resource overloads
        if resource_overloads:
            critical_overloads = [item for item in resource_overloads if item.get("severity") == "Critical"]
            high_overloads = [item for item in resource_overloads if item.get("severity") == "High"]
            
            if critical_overloads:
                return "Severe Resource Capacity Shortage", "Critical"
            elif high_overloads:
                return "Resource Capacity Insufficient", "High"
            else:
                return "Resource Capacity Shortage", "Moderate"
        
        # Check for scheduling conflicts
        if scheduling_conflicts:
            return "Scheduling Conflicts", "High"
        
        # Check for invalid configurations
        if invalid_configurations:
            return "Invalid Activity Configuration", "Moderate"
        
        # Default case
        return "Unknown Infeasibility", "Unknown"
    
    def _generate_recommendations(self, resource_overloads: List[Dict[str, Any]], 
                                scheduling_conflicts: List[Dict[str, Any]], 
                                invalid_configurations: List[Dict[str, Any]], 
                                constraint_violations: List[Dict[str, Any]], 
                                utilization: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations to resolve infeasibility."""
        recommendations = []
        
        # Recommendations for resource overloads
        if resource_overloads:
            # Sort by severity and impact
            sorted_overloads = sorted(resource_overloads, 
                                    key=lambda x: (x.get("utilization_percentage", 0)), 
                                    reverse=True)
            
            for overload in sorted_overloads[:3]:  # Top 3 most critical
                role = overload["role"]
                min_additional = overload["min_additional_staff"]
                current = overload["current_capacity"]
                
                recommendations.append(
                    f"Hire {min_additional} additional {role} staff (increase from {current} to {current + min_additional})"
                )
        
        # Recommendations for scheduling conflicts
        for conflict in scheduling_conflicts:
            if conflict.get("type") == "impossible_activity":
                recommendations.append(
                    f"Increase {conflict['role']} capacity to at least {conflict['demand']} to accommodate '{conflict['activity_name']}'"
                )
            elif conflict.get("type") == "time_horizon_exceeded":
                excess_slots = conflict["excess_slots"]
                recommendations.append(
                    f"Reduce total activity frequency by {excess_slots} slots or extend planning period"
                )
        
        # Recommendations for invalid configurations
        for config in invalid_configurations:
            if config.get("type") == "excessive_frequency":
                activity_name = config["activity_name"]
                excess = config["excess"]
                recommendations.append(
                    f"Reduce frequency of '{activity_name}' by {excess} occurrences"
                )
        
        # Recommendations for constraint violations
        for violation in constraint_violations:
            if violation.get("type") == "missing_resource_types":
                missing = violation["missing_resources"]
                recommendations.append(
                    f"Define capacity for missing resource types: {', '.join(missing)}"
                )
        
        # General recommendations based on utilization
        high_util_roles = [role for role, util in utilization.items() if 90 <= util <= 100]
        if high_util_roles:
            recommendations.append(
                f"Consider increasing capacity for high-utilisation roles: {', '.join(high_util_roles)}"
            )
        
        # Alternative approaches
        if resource_overloads:
            recommendations.append("Alternative: Reschedule activities to different quarters with lower demand")
            recommendations.append("Alternative: Split high-frequency activities across multiple quarters")
        
        return recommendations[:8]  # Limit to 8 most important recommendations
    
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
    
    def _setup_planning_horizon(self, project: Project):
        """Set up the planning horizon based on the project's quarter."""
        if project.planning_quarter:
            try:
                quarter_info = project.get_quarter_info()
                if quarter_info and "working_days" in quarter_info:
                    self.TOTAL_DAYS = quarter_info["working_days"]
                    self.TOTAL_SLOTS = quarter_info["total_slots"]
                    self.working_days = quarter_info["working_days_list"]
                    
                    print(f"Using quarter-based planning: {project.planning_quarter}")
                    print(f"Working days: {self.TOTAL_DAYS}, Total slots: {self.TOTAL_SLOTS}")
                    return
            except Exception as e:
                print(f"Warning: Could not use quarter-based planning: {e}")
        
        # Fallback to default values
        print("Using default 60-day planning horizon")
        self.TOTAL_DAYS = 60
        self.TOTAL_SLOTS = 240
        self.working_days = []
