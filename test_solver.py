#!/usr/bin/env python3
"""
Test script to verify the constraint programming solver works correctly.
"""

from pathlib import Path
from core.models import Project
from core.data_loader import DataLoader
from core.solver import WorkplanSolver

def test_solver():
    """Test the constraint programming solver."""
    print("Testing Workplan Analysis Solver")
    print("=" * 50)
    
    # Load sample data
    csv_path = Path("sample_workplan.csv")
    yaml_path = Path("sample_resources.yml")
    
    if not csv_path.exists():
        print("❌ sample_workplan.csv not found")
        return
    
    if not yaml_path.exists():
        print("❌ sample_resources.yml not found")
        return
    
    try:
        # Load activities and resources
        activities = DataLoader.load_workplan_csv(csv_path)
        resources = DataLoader.load_resources_yaml(yaml_path)
        
        print(f"✅ Loaded {len(activities)} activities")
        print(f"✅ Loaded resources: RC={resources.ranger_coordinator}, SR={resources.senior_ranger}, R={resources.ranger}")
        
        # Create project
        project = Project(
            name="test_solver",
            workplan_path=csv_path,
            activities=activities,
            current_resources=resources
        )
        
        print(f"✅ Created project: {project.name}")
        
        # Calculate total demand
        total_occurrences = sum(a.frequency for a in activities)
        total_demand = {
            'RangerCoordinator': sum(a.ranger_coordinator * a.frequency for a in activities),
            'SeniorRanger': sum(a.senior_ranger * a.frequency for a in activities),
            'Ranger': sum(a.ranger * a.frequency for a in activities)
        }
        
        print(f"\nWorkload Analysis:")
        print(f"  Total occurrences: {total_occurrences}")
        print(f"  Total demand: {total_demand}")
        
        # Calculate rough utilization estimate
        total_slots = 60 * 4  # 60 days * 4 slots per day
        capacity = {
            'RangerCoordinator': resources.ranger_coordinator * total_slots,
            'SeniorRanger': resources.senior_ranger * total_slots,
            'Ranger': resources.ranger * total_slots
        }
        
        print(f"  Total capacity: {capacity}")
        
        for role in ['RangerCoordinator', 'SeniorRanger', 'Ranger']:
            if capacity[role] > 0:
                util = (total_demand[role] / capacity[role]) * 100
                print(f"  {role} rough utilization: {util:.1f}%")
        
        # Run solver
        print(f"\n🔄 Running constraint programming solver...")
        solver = WorkplanSolver()
        result = solver.analyze_project(project, time_limit_seconds=10)
        
        print(f"\n📊 Analysis Results:")
        print(f"  Feasible: {'✅ YES' if result.feasible else '❌ NO'}")
        print(f"  Timestamp: {result.timestamp}")
        
        if result.utilization:
            print(f"  Utilization:")
            for role, util in result.utilization.items():
                status = ""
                if util > 100:
                    status = " (OVERLOADED)"
                elif util > 90:
                    status = " (High)"
                elif util > 70:
                    status = " (Moderate)"
                else:
                    status = " (Low)"
                print(f"    {role}: {util:.1f}%{status}")
        
        if result.solver_stats:
            stats = result.solver_stats
            print(f"  Solver stats:")
            print(f"    Status: {stats.get('status', 'Unknown')}")
            print(f"    Solve time: {stats.get('solve_time', 0):.3f}s")
            print(f"    Variables: {stats.get('num_variables', 0)}")
            print(f"    Constraints: {stats.get('num_constraints', 0)}")
        
        if result.overloads:
            print(f"  Overloads:")
            for overload in result.overloads:
                print(f"    {overload}")
        
        print(f"\n✅ Solver test completed successfully!")
        
        # Test with reduced resources to force infeasibility
        print(f"\n🔄 Testing with reduced resources...")
        reduced_resources = DataLoader.load_resources_yaml(yaml_path)
        reduced_resources.ranger_coordinator = 0  # Remove all coordinators
        reduced_resources.senior_ranger = 1       # Reduce senior rangers
        reduced_resources.ranger = 2              # Reduce rangers
        
        project.current_resources = reduced_resources
        result2 = solver.analyze_project(project, time_limit_seconds=10)
        
        print(f"  Reduced resources feasible: {'✅ YES' if result2.feasible else '❌ NO (expected)'}")
        if result2.utilization:
            for role, util in result2.utilization.items():
                if util > 100:
                    print(f"    {role}: {util:.1f}% (OVERLOADED)")
        
        print(f"\n✅ All solver tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_solver()
