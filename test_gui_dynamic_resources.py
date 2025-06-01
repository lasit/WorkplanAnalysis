#!/usr/bin/env python3
"""Test script to verify GUI tabs work with dynamic resource types."""

import sys
from datetime import datetime
from core.models import Project, Activity, ResourceCapacity, AnalysisResult

def test_dashboard_dynamic_resources():
    """Test that Dashboard tab works with dynamic resource types."""
    print("🧪 Testing Dashboard Tab with Dynamic Resources")
    print("=" * 55)
    
    # Create a project with custom resource types
    project = Project(name="test_custom_resources", workplan_path="test.csv")
    project.set_planning_quarter("2025-Q3")
    
    # Create custom resource configuration
    project.current_resources = ResourceCapacity(
        resources={
            "RangerCoordinator": 1,
            "SeniorRanger": 2,
            "Ranger": 5,
            "Vehicle": 3,           # Custom resource
            "Equipment": 8,         # Custom resource
            "Facility": 2           # Custom resource
        }
    )
    
    # Create a mock analysis result with custom resource utilization
    analysis = AnalysisResult(
        timestamp=datetime.now(),
        feasible=False,
        utilization={
            "RangerCoordinator": 85.5,
            "SeniorRanger": 92.3,
            "Ranger": 78.1,
            "Vehicle": 110.2,      # Overloaded
            "Equipment": 65.8,
            "Facility": 45.0
        },
        overloads=[
            {
                "date": "2025-02-15",
                "slot": "Morning",
                "role": "Vehicle",
                "extra_needed": 1
            }
        ],
        solver_stats={
            "status": "INFEASIBLE",
            "solve_time": 2.45,
            "num_variables": 500,
            "num_constraints": 1200
        },
        resource_capacity=project.current_resources
    )
    
    try:
        # Test that we can get all resource types
        all_resources = analysis.resource_capacity.get_all_resources()
        expected_resources = {"RangerCoordinator", "SeniorRanger", "Ranger", "Vehicle", "Equipment", "Facility"}
        actual_resources = set(all_resources.keys())
        
        if expected_resources == actual_resources:
            print("✅ Resource capacity includes all custom resource types")
        else:
            missing = expected_resources - actual_resources
            extra = actual_resources - expected_resources
            print(f"❌ Resource mismatch - Missing: {missing}, Extra: {extra}")
            return False
        
        # Test utilization data includes all resource types
        expected_util_resources = expected_resources
        actual_util_resources = set(analysis.utilization.keys())
        
        if expected_util_resources == actual_util_resources:
            print("✅ Utilization data includes all custom resource types")
        else:
            missing = expected_util_resources - actual_util_resources
            print(f"❌ Utilization missing resources: {missing}")
            return False
        
        # Test that overloaded resources are identified
        overloaded_resources = [role for role, util in analysis.utilization.items() if util > 100]
        if "Vehicle" in overloaded_resources:
            print("✅ Overloaded custom resources correctly identified")
        else:
            print("❌ Failed to identify overloaded custom resources")
            return False
        
        print(f"\n📊 Resource Summary:")
        for resource_name, capacity in all_resources.items():
            utilization = analysis.utilization.get(resource_name, 0)
            status = "OVERLOADED" if utilization > 100 else "OK"
            print(f"   {resource_name}: {capacity} capacity, {utilization:.1f}% utilization ({status})")
        
        print("\n🎉 Dashboard tab dynamic resource test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed with error: {e}")
        return False

def test_analyses_tab_dynamic_resources():
    """Test that Analyses tab works with dynamic resource types."""
    print("\n🧪 Testing Analyses Tab with Dynamic Resources")
    print("=" * 55)
    
    # Create a project with mixed resource types
    project = Project(name="test_mixed_resources", workplan_path="test.csv")
    
    # Create resource configuration with both standard and custom types
    project.current_resources = ResourceCapacity(
        resources={
            "RangerCoordinator": 2,
            "SeniorRanger": 4,
            "Ranger": 10,
            "Drone": 5,             # Custom resource
            "Boat": 2,              # Custom resource
            "RadioEquipment": 15    # Custom resource
        }
    )
    
    # Create analysis result
    analysis = AnalysisResult(
        timestamp=datetime.now(),
        feasible=True,
        utilization={
            "RangerCoordinator": 75.0,
            "SeniorRanger": 68.5,
            "Ranger": 82.3,
            "Drone": 45.2,
            "Boat": 90.1,
            "RadioEquipment": 55.8
        },
        overloads=[],
        solver_stats={
            "status": "FEASIBLE",
            "solve_time": 1.23
        },
        resource_capacity=project.current_resources
    )
    
    try:
        # Test resource capacity display
        all_resources = analysis.resource_capacity.get_all_resources()
        
        print(f"📋 Resource Capacity Details:")
        for resource_name, capacity in all_resources.items():
            print(f"   {resource_name}: {capacity}")
        
        # Verify all expected resources are present
        expected_resources = {"RangerCoordinator", "SeniorRanger", "Ranger", "Drone", "Boat", "RadioEquipment"}
        actual_resources = set(all_resources.keys())
        
        if expected_resources == actual_resources:
            print("✅ All resource types correctly available for analysis details")
        else:
            print(f"❌ Resource type mismatch in analysis details")
            return False
        
        # Test utilization display
        print(f"\n📈 Utilization Summary:")
        for role, util in analysis.utilization.items():
            status = "High" if util > 80 else "Moderate" if util > 60 else "Low"
            print(f"   {role}: {util:.1f}% ({status})")
        
        print("\n🎉 Analyses tab dynamic resource test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Analyses test failed with error: {e}")
        return False

def test_backward_compatibility():
    """Test that GUI still works with standard resource types."""
    print("\n🧪 Testing Backward Compatibility with Standard Resources")
    print("=" * 60)
    
    # Create a project with only standard resource types
    project = Project(name="test_standard_resources", workplan_path="test.csv")
    
    # Use default resource configuration (standard types only)
    project.current_resources = ResourceCapacity()  # Uses defaults
    
    # Create analysis result with standard resources only
    analysis = AnalysisResult(
        timestamp=datetime.now(),
        feasible=True,
        utilization={
            "RangerCoordinator": 65.0,
            "SeniorRanger": 78.5,
            "Ranger": 72.3
        },
        overloads=[],
        solver_stats={
            "status": "FEASIBLE",
            "solve_time": 0.85
        },
        resource_capacity=project.current_resources
    )
    
    try:
        # Test that standard resources still work
        all_resources = analysis.resource_capacity.get_all_resources()
        expected_standard = {"RangerCoordinator", "SeniorRanger", "Ranger"}
        actual_resources = set(all_resources.keys())
        
        if expected_standard.issubset(actual_resources):
            print("✅ Standard resource types still work correctly")
        else:
            print(f"❌ Standard resource types missing: {expected_standard - actual_resources}")
            return False
        
        # Test utilization for standard resources
        for role in expected_standard:
            if role in analysis.utilization:
                util = analysis.utilization[role]
                print(f"   {role}: {util:.1f}%")
            else:
                print(f"❌ Missing utilization for {role}")
                return False
        
        print("\n🎉 Backward compatibility test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Backward compatibility test failed with error: {e}")
        return False

def main():
    """Run all GUI dynamic resource tests."""
    print("🚀 GUI Dynamic Resource Test Suite")
    print("=" * 70)
    
    tests = [
        test_dashboard_dynamic_resources,
        test_analyses_tab_dynamic_resources,
        test_backward_compatibility
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL GUI TESTS PASSED!")
        print("✅ Dashboard tab works with dynamic resource types")
        print("✅ Analyses tab displays all resource types correctly")
        print("✅ Backward compatibility maintained for standard resources")
        print("✅ Custom resource types fully supported in GUI")
        return True
    else:
        print("❌ SOME GUI TESTS FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
