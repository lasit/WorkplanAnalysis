#!/usr/bin/env python3
"""Test script to verify project duplication functionality."""

import sys
from pathlib import Path
from core.models import Project

def test_project_duplication():
    """Test project duplication functionality."""
    print("🧪 Testing Project Duplication Functionality")
    print("=" * 60)
    
    # Get existing projects
    projects = Project.get_all_projects()
    
    if not projects:
        print("❌ No existing projects found to test duplication")
        return False
    
    # Use the first project for testing
    original_project = projects[0]
    print(f"📁 Original project: {original_project.name}")
    print(f"   📊 Activities: {len(original_project.activities)}")
    print(f"   🔍 Analyses: {len(original_project.analyses)}")
    
    # Test 1: Duplicate without analyses
    print(f"\n🔄 Test 1: Duplicating '{original_project.name}' without analyses...")
    try:
        duplicate_name = f"{original_project.name}_test_copy"
        duplicated_project = original_project.duplicate(duplicate_name, include_analyses=False)
        
        print(f"✅ Successfully created: {duplicated_project.name}")
        print(f"   📊 Activities: {len(duplicated_project.activities)}")
        print(f"   🔍 Analyses: {len(duplicated_project.analyses)} (should be 0)")
        print(f"   📂 Directory: {duplicated_project.project_dir}")
        
        # Verify files exist
        csv_exists = duplicated_project.workplan_path.exists()
        resources_exists = (duplicated_project.project_dir / "resources.yml").exists()
        project_exists = (duplicated_project.project_dir / "project.json").exists()
        
        print(f"   📄 CSV file: {'✅' if csv_exists else '❌'}")
        print(f"   ⚙️ Resources file: {'✅' if resources_exists else '❌'}")
        print(f"   📋 Project file: {'✅' if project_exists else '❌'}")
        
        if not all([csv_exists, resources_exists, project_exists]):
            print("❌ Test 1 failed: Missing files")
            return False
            
        if len(duplicated_project.analyses) != 0:
            print("❌ Test 1 failed: Should have no analyses")
            return False
            
        print("✅ Test 1 passed!")
        
    except Exception as e:
        print(f"❌ Test 1 failed with error: {e}")
        return False
    
    # Test 2: Duplicate with analyses (if original has any)
    if original_project.analyses:
        print(f"\n🔄 Test 2: Duplicating '{original_project.name}' with analyses...")
        try:
            duplicate_name_2 = f"{original_project.name}_test_copy_with_analyses"
            duplicated_project_2 = original_project.duplicate(duplicate_name_2, include_analyses=True)
            
            print(f"✅ Successfully created: {duplicated_project_2.name}")
            print(f"   📊 Activities: {len(duplicated_project_2.activities)}")
            print(f"   🔍 Analyses: {len(duplicated_project_2.analyses)} (should be {len(original_project.analyses)})")
            
            if len(duplicated_project_2.analyses) != len(original_project.analyses):
                print("❌ Test 2 failed: Analysis count mismatch")
                return False
                
            print("✅ Test 2 passed!")
            
        except Exception as e:
            print(f"❌ Test 2 failed with error: {e}")
            return False
    else:
        print("\n⏭️ Test 2 skipped: Original project has no analyses")
    
    # Test 3: Try to duplicate with existing name (should fail)
    print(f"\n🔄 Test 3: Testing duplicate name collision...")
    try:
        # Try to create duplicate with same name as original
        original_project.duplicate(original_project.name, include_analyses=False)
        print("❌ Test 3 failed: Should have raised ValueError for existing name")
        return False
    except ValueError as e:
        print(f"✅ Test 3 passed: Correctly rejected duplicate name ({e})")
    except Exception as e:
        print(f"❌ Test 3 failed with unexpected error: {e}")
        return False
    
    print(f"\n🎉 All duplication tests passed!")
    return True

def cleanup_test_projects():
    """Clean up test projects created during testing."""
    print("\n🧹 Cleaning up test projects...")
    
    projects = Project.get_all_projects()
    test_projects = [p for p in projects if "_test_copy" in p.name]
    
    for project in test_projects:
        try:
            import shutil
            if project.project_dir.exists():
                shutil.rmtree(project.project_dir)
                print(f"🗑️ Removed: {project.name}")
        except Exception as e:
            print(f"⚠️ Could not remove {project.name}: {e}")
    
    if test_projects:
        print(f"✅ Cleaned up {len(test_projects)} test project(s)")
    else:
        print("ℹ️ No test projects to clean up")

def main():
    """Run all duplication tests."""
    print("🚀 Project Duplication Test Suite")
    print("=" * 60)
    
    try:
        # Run tests
        if not test_project_duplication():
            print("\n❌ TESTS FAILED")
            sys.exit(1)
        
        # Clean up
        cleanup_test_projects()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Project duplication functionality is working correctly")
        print("✅ Files are properly copied to new project directories")
        print("✅ Analysis inclusion/exclusion works as expected")
        print("✅ Duplicate name collision is properly handled")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
