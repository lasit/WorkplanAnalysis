#!/usr/bin/env python3
"""Test the real app workflow to identify where utilization data is lost."""

import sys
from pathlib import Path
from core.models import Project, Activity, ResourceCapacity
from core.data_loader import DataLoader
from core.solver import WorkplanSolver

def create_test_project():
    """Create a test project that will be infeasible."""
    print("🏗️ Creating Test Project")
    print("=" * 30)
    
    # Create activities that will be infeasible
    activities = [
        Activity(
            activity_id="TEST1",
            name="Test Activity 1",
            quarter="2025-Q3",
            frequency=50,  # High frequency
            duration=1.0,  # Full day
            resource_requirements={
                "RangerCoordinator": 5,  # More than available
                "SeniorRanger": 10,      # More than available
                "Ranger": 20             # More than available
            }
        ),
        Activity(
            activity_id="TEST2", 
            name="Test Activity 2",
            quarter="2025-Q3",
            frequency=30,
            duration=0.5,
            resource_requirements={
                "RangerCoordinator": 3,
                "SeniorRanger": 6,
                "Ranger": 12
            }
        )
    ]
    
    # Create project
    project = Project(
        name="test_real_workflow",
        workplan_path=Path("test.csv"),
        activities=activities
    )
    project.set_planning_quarter("2025-Q3")
    
    # Set limited resources (guaranteed infeasible)
    project.current_resources = ResourceCapacity(
        resources={
            "RangerCoordinator": 1,
            "SeniorRanger": 2,
            "Ranger": 5
        }
    )
    
    print(f"   Created project with {len(activities)} activities")
    print(f"   Total occurrences: {sum(a.frequency for a in activities)}")
    print(f"   Resource capacity: {project.current_resources.get_all_resources()}")
    
    return project

def test_real_workflow():
    """Test the complete real app workflow."""
    print("🧪 Testing Real App Workflow")
    print("=" * 40)
    
    # Step 1: Create project (simulates loading CSV)
    project = create_test_project()
    
    # Step 2: Validate project data
    print(f"\n📋 Project Validation:")
    print(f"   Activities: {len(project.activities)}")
    print(f"   Planning quarter: {project.planning_quarter}")
    print(f"   Resources: {project.current_resources.get_all_resources()}")
    
    # Check valid activities for quarter
    valid_activities, excluded_activities = project.get_valid_activities()
    print(f"   Valid activities for quarter: {len(valid_activities)}")
    print(f"   Excluded activities: {len(excluded_activities)}")
    
    if not valid_activities:
        print("   ❌ No valid activities for analysis!")
        return False
    
    # Step 3: Run solver (simulates clicking "Run Analysis")
    print(f"\n🔧 Running Solver Analysis:")
    solver = WorkplanSolver()
    
    try:
        result = solver.analyze_project(project, time_limit_seconds=10)
        
        print(f"   Status: {result.solver_stats.get('status', 'Unknown')}")
        print(f"   Feasible: {result.feasible}")
        print(f"   Solve time: {result.solver_stats.get('solve_time', 0):.3f}s")
        
        # Step 4: Check analysis result data
        print(f"\n📊 Analysis Result Inspection:")
        print(f"   Has utilization data: {bool(result.utilization)}")
        print(f"   Has resource capacity: {bool(result.resource_capacity)}")
        print(f"   Has overloads: {bool(result.overloads)}")
        
        if result.utilization:
            print(f"   Utilization data:")
            for role, util in result.utilization.items():
                print(f"     {role}: {util:.1f}%")
        else:
            print(f"   ❌ NO UTILIZATION DATA IN RESULT!")
            return False
        
        if result.resource_capacity:
            capacity_data = result.resource_capacity.get_all_resources()
            print(f"   Resource capacity data:")
            for role, capacity in capacity_data.items():
                print(f"     {role}: {capacity}")
        else:
            print(f"   ❌ NO RESOURCE CAPACITY IN RESULT!")
            return False
        
        # Step 5: Simulate adding to project (what main window does)
        print(f"\n💾 Simulating Project Update:")
        project.analyses.append(result)
        print(f"   Added analysis to project")
        print(f"   Project now has {len(project.analyses)} analysis(es)")
        
        # Step 6: Simulate Dashboard display (what main window does)
        print(f"\n🖥️ Simulating Dashboard Display:")
        latest_analysis = project.get_latest_analysis()
        
        if latest_analysis:
            print(f"   Latest analysis found: {latest_analysis.feasible}")
            print(f"   Latest analysis utilization: {bool(latest_analysis.utilization)}")
            
            if latest_analysis.utilization:
                print(f"   Dashboard would show:")
                capacity_data = latest_analysis.resource_capacity.get_all_resources() if latest_analysis.resource_capacity else {}
                for role, util in latest_analysis.utilization.items():
                    capacity = capacity_data.get(role, 0)
                    status = "Overloaded" if util > 100 else "High" if util > 90 else "Moderate" if util > 70 else "Low"
                    print(f"     {role}: {util:.1f}% ({status})")
                
                print(f"\n✅ WORKFLOW SUCCESSFUL!")
                print(f"✅ Utilization data preserved through entire workflow")
                return True
            else:
                print(f"   ❌ Latest analysis missing utilization data!")
                return False
        else:
            print(f"   ❌ No latest analysis found!")
            return False
            
    except Exception as e:
        print(f"   ❌ Solver failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the real workflow test."""
    print("🚀 Real App Workflow Test")
    print("=" * 50)
    
    try:
        success = test_real_workflow()
        
        print("\n" + "=" * 50)
        if success:
            print("✅ REAL WORKFLOW TEST PASSED!")
            print("🎯 Utilization data flows correctly through entire app workflow")
            print("📊 Dashboard should display utilization for infeasible results")
            print("🔍 If user still sees empty table, check for UI refresh issues")
            return True
        else:
            print("❌ REAL WORKFLOW TEST FAILED!")
            print("🔧 Issue found in app workflow - utilization data lost somewhere")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
