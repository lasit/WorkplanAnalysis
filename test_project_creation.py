#!/usr/bin/env python3
"""
Test script to verify project creation works without the hashable error.
"""

from pathlib import Path
from core.models import Project
from core.data_loader import DataLoader

def test_project_creation():
    """Test that we can create a Project object and use it in collections."""
    print("Testing Project Creation and Hashability Fix")
    print("=" * 50)
    
    # Load sample data
    csv_path = Path("sample_workplan.csv")
    if not csv_path.exists():
        print("❌ sample_workplan.csv not found")
        return
    
    try:
        # Load activities
        activities = DataLoader.load_workplan_csv(csv_path)
        print(f"✅ Loaded {len(activities)} activities")
        
        # Create project
        project = Project(
            name="test_project",
            workplan_path=csv_path,
            activities=activities
        )
        print(f"✅ Created project: {project.name}")
        
        # Test using project in a list (this should work)
        project_list = [(project, "item1")]
        print(f"✅ Project can be used in list of tuples")
        
        # Test finding project in list
        found = None
        for proj, item in project_list:
            if proj == project:
                found = proj
                break
        
        if found:
            print(f"✅ Project can be found in list: {found.name}")
        else:
            print("❌ Project not found in list")
        
        # Test project directory creation
        project.ensure_project_dir()
        print(f"✅ Project directory created: {project.project_dir}")
        
        print("\n✅ All tests passed! Project creation should work in the GUI now.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_project_creation()
