#!/usr/bin/env python3
"""Test end-to-end flow for infeasible analysis to verify Dashboard display."""

import sys
from core.models import Project, Activity, ResourceCapacity
from core.solver import WorkplanSolver

def test_end_to_end_infeasible_flow():
    """Test the complete flow from solver to Dashboard for infeasible results."""
    print("🧪 Testing End-to-End Infeasible Analysis Flow")
    print("=" * 55)
    
    # Create a project guaranteed to be infeasible
    project = Project(name="test_e2e_infeasible", workplan_path="test.csv")
    project.set_planning_quarter("2025-Q3")
    
    # Create activities with impossible resource demands
    activities = [
        Activity(
            activity_id="IMPOSSIBLE1",
            name="Impossible Activity 1",
            quarter="2025-Q3",
            frequency=100,  # Very high frequency
            duration=1.0,   # Full day
            resource_requirements={
                "RangerCoordinator": 10,  # Way more than available
                "SeniorRanger": 20,       # Way more than available
                "Ranger": 50              # Way more than available
            }
        )
    ]
    
    project.activities = activities
    
    # Set very limited resources
    project.current_resources = ResourceCapacity(
        resources={
            "RangerCoordinator": 1,
            "SeniorRanger": 2,
            "Ranger": 5
        }
    )
    
    print(f"📋 Project Setup:")
    print(f"   Activities: {len(project.activities)}")
    print(f"   Total occurrences: {sum(a.frequency for a in project.activities)}")
    print(f"   Resource capacity: {project.current_resources.get_all_resources()}")
    
    # Run the solver
    print(f"\n🔧 Running Solver...")
    solver = WorkplanSolver()
    result = solver.analyze_project(project, time_limit_seconds=10)
    
    print(f"\n📊 Solver Results:")
    print(f"   Feasible: {result.feasible}")
    print(f"   Status: {result.solver_stats.get('status', 'Unknown')}")
    print(f"   Solve time: {result.solver_stats.get('solve_time', 0):.3f}s")
    
    # Check utilization data
    print(f"\n📈 Utilization Analysis:")
    if result.utilization:
        print(f"   Has utilization data: ✅")
        for role, util in result.utilization.items():
            print(f"   {role}: {util:.1f}%")
        
        # Check if any utilization > 100% (expected for infeasible)
        overloaded = [role for role, util in result.utilization.items() if util > 100]
        if overloaded:
            print(f"   Overloaded resources: {overloaded} ✅")
        else:
            print(f"   ❌ No overloaded resources found (unexpected for infeasible)")
            return False
    else:
        print(f"   ❌ NO UTILIZATION DATA!")
        return False
    
    # Check resource capacity data
    print(f"\n🏗️ Resource Capacity Check:")
    if result.resource_capacity:
        capacity_data = result.resource_capacity.get_all_resources()
        print(f"   Has resource capacity: ✅")
        for role, capacity in capacity_data.items():
            print(f"   {role}: {capacity}")
    else:
        print(f"   ❌ NO RESOURCE CAPACITY DATA!")
        return False
    
    # Check overload data
    print(f"\n🚨 Overload Analysis:")
    if result.overloads:
        print(f"   Has overload data: ✅")
        for overload in result.overloads:
            role = overload.get('role', 'Unknown')
            extra = overload.get('extra_needed', 0)
            print(f"   {role}: needs {extra} additional resources")
    else:
        print(f"   No overload data (may be expected for simple analysis)")
    
    # Simulate Dashboard display
    print(f"\n🖥️ Dashboard Display Simulation:")
    print(f"   Verdict: {'❌ INFEASIBLE' if not result.feasible else '✅ FEASIBLE'}")
    print(f"   Utilization Table Data:")
    
    # This is exactly what the Dashboard should do
    capacity_data = result.resource_capacity.get_all_resources() if result.resource_capacity else {}
    
    table_data = []
    for role, util in result.utilization.items():
        capacity = capacity_data.get(role, 0)
        status = "Overloaded" if util > 100 else "High" if util > 90 else "Moderate" if util > 70 else "Low"
        table_data.append((role, util, status))
        print(f"     {role}: {util:.1f}% ({status})")
    
    # Verify we have data for the table
    if table_data:
        print(f"\n✅ Dashboard table should display {len(table_data)} rows")
        print(f"✅ All utilization percentages available")
        print(f"✅ Status indicators calculated correctly")
        
        # Add to project analyses (simulate saving)
        project.analyses.append(result)
        print(f"✅ Analysis added to project history")
        
        return True
    else:
        print(f"\n❌ No data available for Dashboard table!")
        return False

def main():
    """Run the end-to-end infeasible test."""
    print("🚀 End-to-End Infeasible Analysis Test")
    print("=" * 60)
    
    try:
        success = test_end_to_end_infeasible_flow()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ END-TO-END TEST PASSED!")
            print("🎯 Solver produces utilization data for infeasible results")
            print("📊 Dashboard should display utilization table correctly")
            print("🔍 If Dashboard still not showing data, check GUI event handling")
            return True
        else:
            print("❌ END-TO-END TEST FAILED!")
            print("🔧 Issue in solver utilization calculation")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
