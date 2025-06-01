#!/usr/bin/env python3
"""Test the enhanced infeasibility diagnostics system."""

import sys
from datetime import datetime
from core.models import Project, Activity, ResourceCapacity
from core.solver import WorkplanSolver

def test_enhanced_diagnostics():
    """Test the comprehensive infeasibility diagnostics system."""
    print("🚀 Enhanced Infeasibility Diagnostics Test")
    print("=" * 60)
    
    # Create a project with multiple types of infeasibility issues
    project = Project(name="test_enhanced_diagnostics", workplan_path="test.csv")
    project.set_planning_quarter("2025-Q3")
    
    # Create activities that will cause different types of issues
    activities = [
        # Activity requiring more resources than available (impossible activity)
        Activity(
            activity_id="IMPOSSIBLE1",
            name="Impossible High-Demand Activity",
            quarter="2025-Q3",
            frequency=5,
            duration=1.0,
            resource_requirements={
                "RangerCoordinator": 10,  # Way more than available
                "SeniorRanger": 15,       # Way more than available
                "Ranger": 25              # Way more than available
            }
        ),
        # High frequency activity (resource overload)
        Activity(
            activity_id="OVERLOAD1",
            name="High Frequency Patrol",
            quarter="2025-Q3",
            frequency=100,  # Very high frequency
            duration=0.5,
            resource_requirements={
                "RangerCoordinator": 1,
                "SeniorRanger": 2,
                "Ranger": 3
            }
        ),
        # Activity with missing resource type
        Activity(
            activity_id="MISSING1",
            name="Vehicle Maintenance",
            quarter="2025-Q3",
            frequency=10,
            duration=0.25,
            resource_requirements={
                "Vehicle": 2,  # Resource type not defined in capacity
                "Mechanic": 1  # Another missing resource type
            }
        ),
        # Activity with zero resources (invalid config)
        Activity(
            activity_id="ZERO1",
            name="Zero Resource Activity",
            quarter="2025-Q3",
            frequency=5,
            duration=0.5,
            resource_requirements={}  # No resources required
        )
    ]
    
    project.activities = activities
    
    # Set very limited resources to guarantee infeasibility
    project.current_resources = ResourceCapacity(
        resources={
            "RangerCoordinator": 1,
            "SeniorRanger": 2,
            "Ranger": 5
            # Note: Vehicle and Mechanic are missing
        }
    )
    
    print(f"📋 Test Project Setup:")
    print(f"   Activities: {len(activities)}")
    print(f"   Total occurrences: {sum(a.frequency for a in activities)}")
    print(f"   Resource capacity: {project.current_resources.get_all_resources()}")
    
    # Run the solver
    print(f"\n🔧 Running Enhanced Solver Analysis...")
    solver = WorkplanSolver()
    result = solver.analyze_project(project, time_limit_seconds=10)
    
    print(f"\n📊 Analysis Results:")
    print(f"   Feasible: {result.feasible}")
    print(f"   Status: {result.solver_stats.get('status', 'Unknown')}")
    print(f"   Solve time: {result.solver_stats.get('solve_time', 0):.3f}s")
    
    # Test enhanced diagnostics
    if result.infeasibility_diagnostics:
        diagnostics = result.infeasibility_diagnostics
        print(f"\n🔍 Enhanced Diagnostics Analysis:")
        print(f"   Primary Reason: {diagnostics.primary_reason}")
        print(f"   Severity: {diagnostics.severity}")
        
        # Test resource overloads
        print(f"\n🔴 Resource Overloads ({len(diagnostics.resource_overloads)}):")
        for overload in diagnostics.resource_overloads:
            role = overload.get("role", "Unknown")
            util = overload.get("utilization_percentage", 0)
            additional = overload.get("min_additional_staff", 0)
            severity = overload.get("severity", "Unknown")
            print(f"     {role}: {util:.1f}% utilised, need {additional} more staff ({severity})")
        
        # Test scheduling conflicts
        print(f"\n⏰ Scheduling Conflicts ({len(diagnostics.scheduling_conflicts)}):")
        for conflict in diagnostics.scheduling_conflicts:
            conflict_type = conflict.get("type", "Unknown")
            description = conflict.get("description", "No description")
            severity = conflict.get("severity", "Unknown")
            print(f"     {conflict_type}: {description} ({severity})")
        
        # Test invalid configurations
        print(f"\n⚠️ Invalid Configurations ({len(diagnostics.invalid_configurations)}):")
        for config in diagnostics.invalid_configurations:
            config_type = config.get("type", "Unknown")
            description = config.get("description", "No description")
            severity = config.get("severity", "Unknown")
            print(f"     {config_type}: {description} ({severity})")
        
        # Test constraint violations
        print(f"\n🚫 Constraint Violations ({len(diagnostics.constraint_violations)}):")
        for violation in diagnostics.constraint_violations:
            violation_type = violation.get("type", "Unknown")
            description = violation.get("description", "No description")
            severity = violation.get("severity", "Unknown")
            print(f"     {violation_type}: {description} ({severity})")
        
        # Test recommendations
        print(f"\n💡 Recommendations ({len(diagnostics.recommendations)}):")
        for i, recommendation in enumerate(diagnostics.recommendations, 1):
            print(f"     {i}. {recommendation}")
        
        # Verify we have the expected types of issues
        expected_issues = {
            "resource_overloads": True,
            "scheduling_conflicts": True,
            "invalid_configurations": True,
            "constraint_violations": True
        }
        
        actual_issues = {
            "resource_overloads": len(diagnostics.resource_overloads) > 0,
            "scheduling_conflicts": len(diagnostics.scheduling_conflicts) > 0,
            "invalid_configurations": len(diagnostics.invalid_configurations) > 0,
            "constraint_violations": len(diagnostics.constraint_violations) > 0
        }
        
        print(f"\n✅ Issue Detection Verification:")
        all_detected = True
        for issue_type, expected in expected_issues.items():
            actual = actual_issues[issue_type]
            status = "✅" if actual == expected else "❌"
            print(f"     {status} {issue_type}: Expected {expected}, Got {actual}")
            if actual != expected:
                all_detected = False
        
        # Test specific issue types
        print(f"\n🧪 Specific Issue Type Tests:")
        
        # Check for missing resource types
        missing_resource_violations = [
            v for v in diagnostics.constraint_violations 
            if v.get("type") == "missing_resource_types"
        ]
        if missing_resource_violations:
            missing_resources = missing_resource_violations[0].get("missing_resources", [])
            expected_missing = {"Vehicle", "Mechanic"}
            actual_missing = set(missing_resources)
            if expected_missing.issubset(actual_missing):
                print(f"     ✅ Missing resource types detected: {missing_resources}")
            else:
                print(f"     ❌ Missing resource types: Expected {expected_missing}, Got {actual_missing}")
                all_detected = False
        else:
            print(f"     ❌ Missing resource types not detected")
            all_detected = False
        
        # Check for impossible activities
        impossible_conflicts = [
            c for c in diagnostics.scheduling_conflicts 
            if c.get("type") == "impossible_activity"
        ]
        if impossible_conflicts:
            print(f"     ✅ Impossible activities detected: {len(impossible_conflicts)}")
        else:
            print(f"     ❌ Impossible activities not detected")
            all_detected = False
        
        # Check for zero resource activities
        zero_resource_configs = [
            c for c in diagnostics.invalid_configurations 
            if c.get("type") == "zero_resources"
        ]
        if zero_resource_configs:
            print(f"     ✅ Zero resource activities detected: {len(zero_resource_configs)}")
        else:
            print(f"     ❌ Zero resource activities not detected")
            all_detected = False
        
        return all_detected
        
    else:
        print(f"\n❌ No enhanced diagnostics available!")
        return False

def main():
    """Run the enhanced diagnostics test."""
    print("🚀 Enhanced Infeasibility Diagnostics Test Suite")
    print("=" * 70)
    
    try:
        success = test_enhanced_diagnostics()
        
        print("\n" + "=" * 70)
        if success:
            print("✅ ENHANCED DIAGNOSTICS TEST PASSED!")
            print("🎯 All diagnostic categories detected correctly")
            print("📊 Comprehensive infeasibility analysis working")
            print("💡 Actionable recommendations generated")
            print("🔍 Detailed issue breakdown available")
            return True
        else:
            print("❌ ENHANCED DIAGNOSTICS TEST FAILED!")
            print("🔧 Some diagnostic features not working correctly")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
