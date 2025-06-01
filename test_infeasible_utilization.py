#!/usr/bin/env python3
"""Test script to verify that infeasible analysis results include utilization data."""

import sys
from core.models import Project, Activity, ResourceCapacity
from core.solver import WorkplanSolver

def test_infeasible_utilization():
    """Test that infeasible analysis results include utilization for each role."""
    print("🧪 Testing Infeasible Analysis Utilization")
    print("=" * 50)
    
    # Create a project with impossible resource demands (guaranteed infeasible)
    project = Project(name="test_infeasible", workplan_path="test.csv")
    project.set_planning_quarter("2025-Q3")
    
    # Create activities that require way more resources than available
    activities = [
        Activity(
            activity_id="OVERLOAD1",
            name="Impossible Activity 1",
            quarter="2025-Q3",
            frequency=50,  # Very high frequency
            duration=1.0,  # Full day
            resource_requirements={
                "RangerCoordinator": 5,  # Way more than available (1)
                "SeniorRanger": 10,      # Way more than available (2)
                "Ranger": 20             # Way more than available (5)
            }
        ),
        Activity(
            activity_id="OVERLOAD2",
            name="Impossible Activity 2",
            quarter="2025-Q3",
            frequency=30,
            duration=0.5,
            resource_requirements={
                "RangerCoordinator": 3,
                "SeniorRanger": 8,
                "Ranger": 15
            }
        )
    ]
    
    project.activities = activities
    
    # Set minimal resources (guaranteed to be insufficient)
    project.current_resources = ResourceCapacity(
        resources={
            "RangerCoordinator": 1,
            "SeniorRanger": 2,
            "Ranger": 5
        }
    )
    
    # Run analysis
    solver = WorkplanSolver()
    result = solver.analyze_project(project, time_limit_seconds=10)
    
    print(f"📊 Analysis Result:")
    print(f"   Feasible: {result.feasible}")
    print(f"   Status: {result.solver_stats.get('status', 'Unknown')}")
    print(f"   Solve time: {result.solver_stats.get('solve_time', 0):.2f}s")
    
    # Check utilization data
    print(f"\n📈 Utilization Data:")
    if result.utilization:
        for role, util in result.utilization.items():
            print(f"   {role}: {util:.1f}%")
        
        # Verify we have utilization for all resource types
        expected_roles = {"RangerCoordinator", "SeniorRanger", "Ranger"}
        actual_roles = set(result.utilization.keys())
        
        if expected_roles.issubset(actual_roles):
            print("✅ All expected resource types have utilization data")
        else:
            missing = expected_roles - actual_roles
            print(f"❌ Missing utilization for: {missing}")
            return False
        
        # Verify utilization values are reasonable (should be > 100% for infeasible)
        high_utilization_count = sum(1 for util in result.utilization.values() if util > 100)
        if high_utilization_count > 0:
            print(f"✅ {high_utilization_count} resource types show overutilization (>100%)")
        else:
            print("❌ No resource types show overutilization - this seems wrong for infeasible case")
            return False
        
    else:
        print("❌ No utilization data found!")
        return False
    
    # Check overload data
    print(f"\n🚨 Overload Data:")
    if result.overloads:
        for overload in result.overloads:
            role = overload.get('role', 'Unknown')
            extra_needed = overload.get('extra_needed', 0)
            print(f"   {role}: needs {extra_needed} additional resources")
        print(f"✅ Found {len(result.overloads)} overload(s)")
    else:
        print("⚠️  No overload data (this might be expected for simple overload analysis)")
    
    # Final verification
    if not result.feasible and result.utilization:
        print("\n🎉 SUCCESS: Infeasible analysis includes utilization data!")
        return True
    else:
        print("\n❌ FAILURE: Missing utilization data for infeasible analysis")
        return False

def main():
    """Run the infeasible utilization test."""
    print("🚀 Infeasible Analysis Utilization Test")
    print("=" * 60)
    
    try:
        success = test_infeasible_utilization()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ TEST PASSED: Infeasible analysis now includes utilization data!")
            print("🎯 Users will see resource utilization even when plans are infeasible")
            return True
        else:
            print("❌ TEST FAILED: Utilization data missing for infeasible analysis")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
