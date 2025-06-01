#!/usr/bin/env python3
"""Test script to verify the new project folder structure works correctly."""

import sys
from pathlib import Path
from core.models import Project
from core.data_loader import DataLoader

def test_project_structure():
    """Test that projects are created with the correct folder structure."""
    print("🧪 Testing New Project Structure")
    print("=" * 50)
    
    # Check if projects directory exists
    projects_dir = Path.cwd() / "projects"
    if not projects_dir.exists():
        print("❌ Projects directory does not exist")
        return False
    
    print(f"✅ Projects directory exists: {projects_dir}")
    
    # List existing projects
    existing_projects = Project.get_all_projects()
    print(f"✅ Found {len(existing_projects)} existing projects")
    
    for project in existing_projects:
        print(f"\n📁 Project: {project.name}")
        print(f"   📂 Directory: {project.project_dir}")
        print(f"   📄 CSV Path: {project.workplan_path}")
        print(f"   📊 Activities: {len(project.activities)}")
        print(f"   🔍 Analyses: {len(project.analyses)}")
        
        # Check if files exist
        csv_exists = project.workplan_path.exists()
        resources_file = project.project_dir / "resources.yml"
        resources_exists = resources_file.exists()
        project_file = project.project_dir / "project.json"
        project_exists = project_file.exists()
        
        print(f"   ✅ CSV file exists: {csv_exists}")
        print(f"   ✅ Resources file exists: {resources_exists}")
        print(f"   ✅ Project file exists: {project_exists}")
        
        if not all([csv_exists, resources_exists, project_exists]):
            print(f"   ❌ Missing files in project {project.name}")
            return False
    
    print(f"\n🎉 All {len(existing_projects)} projects have correct structure!")
    return True

def test_project_isolation():
    """Test that each project is self-contained."""
    print("\n🔒 Testing Project Isolation")
    print("=" * 50)
    
    projects = Project.get_all_projects()
    
    for project in projects:
        # Check that CSV is in project directory
        csv_in_project_dir = project.workplan_path.parent == project.project_dir
        print(f"📁 {project.name}: CSV in project dir = {csv_in_project_dir}")
        
        if not csv_in_project_dir:
            print(f"❌ Project {project.name} CSV is not in project directory")
            return False
    
    print("✅ All projects are properly isolated!")
    return True

def main():
    """Run all tests."""
    print("🚀 Testing New Project Folder Structure")
    print("=" * 60)
    
    try:
        # Test 1: Project structure
        if not test_project_structure():
            print("\n❌ Project structure test failed")
            sys.exit(1)
        
        # Test 2: Project isolation
        if not test_project_isolation():
            print("\n❌ Project isolation test failed")
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ New project folder structure is working correctly")
        print("✅ Projects are self-contained in their own folders")
        print("✅ CSV and resource files are copied to project directories")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
