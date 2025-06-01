#!/usr/bin/env python3
"""
Test script for project persistence functionality.
"""

import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from core.models import Project, Activity, ResourceCapacity, AnalysisResult
from core.data_loader import DataLoader


def test_project_persistence():
    """Test project save/load functionality."""
    print("Testing Project Persistence")
    print("=" * 50)
    
    # Test 1: Create and save a project
    print("Test 1: Creating and saving a project...")
    
    # Create sample activities
    activities = [
        Activity(
            activity_id="A001",
            name="Wildlife Survey",
            quarter="Q1",
            frequency=4,
            duration=1.0,
            ranger_coordinator=1,
            senior_ranger=1,
            ranger=2
        ),
        Activity(
            activity_id="A002", 
            name="Trail Maintenance",
            quarter="Q2",
            frequency=2,
            duration=0.5,
            ranger_coordinator=0,
            senior_ranger=1,
            ranger=3
        )
    ]
    
    # Create sample resources
    resources = ResourceCapacity(
        ranger_coordinator=2,
        senior_ranger=3,
        ranger=6,
        public_holidays=["2024-01-01", "2024-12-25"]
    )
    
    # Create sample analysis result
    analysis = AnalysisResult(
        timestamp=datetime.now(),
        feasible=True,
        utilization={"RangerCoordinator": 75.0, "SeniorRanger": 60.0, "Ranger": 80.0},
        overloads=[],
        solver_stats={"solve_time": 1.23, "variables": 100},
        resource_capacity=resources
    )
    
    # Create project
    project = Project(
        name="test_project_persistence",
        workplan_path=Path("/tmp/sample_workplan.csv"),
        activities=activities,
        analyses=[analysis],
        current_resources=resources
    )
    
    try:
        # Save project
        project.save_project()
        print(f"✅ Project saved successfully to {project.project_file}")
        
        # Verify project file exists
        if project.project_file.exists():
            print("✅ Project file exists")
        else:
            print("❌ Project file not found")
            return False
        
        # Test 2: Load the project
        print("\nTest 2: Loading the project...")
        
        loaded_project = Project.load_project(project.project_dir)
        print(f"✅ Project loaded successfully: {loaded_project.name}")
        
        # Test 3: Verify data integrity
        print("\nTest 3: Verifying data integrity...")
        
        # Check basic properties
        assert loaded_project.name == project.name, "Project name mismatch"
        assert loaded_project.workplan_path == project.workplan_path, "Workplan path mismatch"
        print("✅ Basic properties match")
        
        # Check activities
        assert len(loaded_project.activities) == len(project.activities), "Activities count mismatch"
        for orig, loaded in zip(project.activities, loaded_project.activities):
            assert orig.activity_id == loaded.activity_id, "Activity ID mismatch"
            assert orig.name == loaded.name, "Activity name mismatch"
            assert orig.frequency == loaded.frequency, "Activity frequency mismatch"
        print("✅ Activities match")
        
        # Check resources
        assert loaded_project.current_resources.ranger_coordinator == resources.ranger_coordinator
        assert loaded_project.current_resources.senior_ranger == resources.senior_ranger
        assert loaded_project.current_resources.ranger == resources.ranger
        assert loaded_project.current_resources.public_holidays == resources.public_holidays
        print("✅ Resources match")
        
        # Check analyses
        assert len(loaded_project.analyses) == 1, "Analysis count mismatch"
        loaded_analysis = loaded_project.analyses[0]
        assert loaded_analysis.feasible == analysis.feasible, "Analysis feasible mismatch"
        assert loaded_analysis.utilization == analysis.utilization, "Analysis utilization mismatch"
        print("✅ Analyses match")
        
        print("\n🎉 All tests passed! Project persistence is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test project
        try:
            if project.project_file.exists():
                project.project_file.unlink()
            if project.project_dir.exists():
                shutil.rmtree(project.project_dir)
        except:
            pass


def test_serialization_edge_cases():
    """Test edge cases in serialization."""
    print("\nTesting Serialization Edge Cases")
    print("=" * 50)
    
    try:
        # Test empty project
        empty_project = Project(
            name="empty_project",
            workplan_path=Path("/tmp/empty.csv"),
            activities=[],
            analyses=[],
            current_resources=None
        )
        
        # Test serialization
        project_dict = {
            "name": empty_project.name,
            "workplan_path": str(empty_project.workplan_path),
            "created_at": datetime.now().isoformat(),
            "activities": [activity.to_dict() for activity in empty_project.activities],
            "current_resources": empty_project.current_resources.to_dict() if empty_project.current_resources else None,
            "analyses": [analysis.to_dict() for analysis in empty_project.analyses]
        }
        
        print("✅ Empty project serialization works")
        
        # Test activity serialization
        activity = Activity(
            activity_id="TEST",
            name="Test Activity",
            quarter="Q1",
            frequency=1,
            duration=0.25,
            ranger_coordinator=0,
            senior_ranger=1,
            ranger=1
        )
        
        activity_dict = activity.to_dict()
        restored_activity = Activity.from_dict(activity_dict)
        
        assert activity.activity_id == restored_activity.activity_id
        assert activity.duration == restored_activity.duration
        print("✅ Activity serialization works")
        
        # Test resource serialization
        resources = ResourceCapacity()
        resource_dict = resources.to_dict()
        restored_resources = ResourceCapacity.from_dict(resource_dict)
        
        assert resources.ranger_coordinator == restored_resources.ranger_coordinator
        assert resources.public_holidays == restored_resources.public_holidays
        print("✅ Resource serialization works")
        
        print("\n🎉 All edge case tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Edge case test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Workplan Analysis - Project Persistence Test")
    print("=" * 60)
    
    success1 = test_project_persistence()
    success2 = test_serialization_edge_cases()
    
    if success1 and success2:
        print("\n🎉 All persistence tests completed successfully!")
        print("Projects can now be saved and reused between sessions.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
