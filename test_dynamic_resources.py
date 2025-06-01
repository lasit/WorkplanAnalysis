#!/usr/bin/env python3
"""Test script to verify dynamic resource functionality."""

import sys
from pathlib import Path
from core.models import Project, ResourceCapacity

def test_resource_capacity_functionality():
    """Test the new ResourceCapacity functionality."""
    print("🧪 Testing Dynamic Resource Capacity Functionality")
    print("=" * 60)
    
    # Test 1: Default resources (backward compatibility)
    print("🔄 Test 1: Default resource creation...")
    try:
        default_resources = ResourceCapacity()
        expected_resources = {"RangerCoordinator": 1, "SeniorRanger": 2, "Ranger": 5}
        
        print(f"✅ Default resources created: {default_resources.get_all_resources()}")
        
        # Check backward compatibility properties
        assert default_resources.ranger_coordinator == 1
        assert default_resources.senior_ranger == 2
        assert default_resources.ranger == 5
        
        print("✅ Backward compatibility properties work correctly")
        print("✅ Test 1 passed!")
        
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False
    
    # Test 2: Adding custom resources
    print(f"\n🔄 Test 2: Adding custom resource types...")
    try:
        resources = ResourceCapacity()
        
        # Add custom resources
        resources.add_resource("Vehicle", 3)
        resources.add_resource("Boat", 2)
        resources.add_resource("Drone", 1)
        
        all_resources = resources.get_all_resources()
        print(f"✅ Resources after adding custom types: {all_resources}")
        
        # Verify custom resources
        assert resources.get_resource_capacity("Vehicle") == 3
        assert resources.get_resource_capacity("Boat") == 2
        assert resources.get_resource_capacity("Drone") == 1
        
        print("✅ Custom resources added and retrieved correctly")
        print("✅ Test 2 passed!")
        
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return False
    
    # Test 3: Modifying resource capacities
    print(f"\n🔄 Test 3: Modifying resource capacities...")
    try:
        resources.set_resource_capacity("Vehicle", 5)
        resources.set_resource_capacity("RangerCoordinator", 2)
        
        assert resources.get_resource_capacity("Vehicle") == 5
        assert resources.ranger_coordinator == 2  # Backward compatibility
        
        print(f"✅ Modified resources: {resources.get_all_resources()}")
        print("✅ Test 3 passed!")
        
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return False
    
    # Test 4: Removing resources
    print(f"\n🔄 Test 4: Removing resource types...")
    try:
        resources.remove_resource("Drone")
        
        assert resources.get_resource_capacity("Drone") == 0
        assert "Drone" not in resources.get_all_resources()
        
        print(f"✅ Resources after removal: {resources.get_all_resources()}")
        print("✅ Test 4 passed!")
        
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return False
    
    # Test 5: Serialization and deserialization
    print(f"\n🔄 Test 5: Serialization and deserialization...")
    try:
        # Convert to dict
        resources_dict = resources.to_dict()
        print(f"✅ Serialized to dict: {resources_dict}")
        
        # Create from dict
        restored_resources = ResourceCapacity.from_dict(resources_dict)
        
        # Verify restoration
        assert restored_resources.get_all_resources() == resources.get_all_resources()
        assert restored_resources.ranger_coordinator == resources.ranger_coordinator
        
        print(f"✅ Restored resources: {restored_resources.get_all_resources()}")
        print("✅ Test 5 passed!")
        
    except Exception as e:
        print(f"❌ Test 5 failed: {e}")
        return False
    
    # Test 6: Backward compatibility with old format
    print(f"\n🔄 Test 6: Backward compatibility with old format...")
    try:
        old_format_data = {
            "ranger_coordinator": 3,
            "senior_ranger": 4,
            "ranger": 8,
            "slots_per_day": 4,
            "public_holidays": ["2025-12-25"]
        }
        
        old_resources = ResourceCapacity.from_dict(old_format_data)
        
        assert old_resources.ranger_coordinator == 3
        assert old_resources.senior_ranger == 4
        assert old_resources.ranger == 8
        
        expected_resources = {"RangerCoordinator": 3, "SeniorRanger": 4, "Ranger": 8}
        assert old_resources.get_all_resources() == expected_resources
        
        print(f"✅ Old format converted correctly: {old_resources.get_all_resources()}")
        print("✅ Test 6 passed!")
        
    except Exception as e:
        print(f"❌ Test 6 failed: {e}")
        return False
    
    print(f"\n🎉 All resource capacity tests passed!")
    return True

def test_project_integration():
    """Test integration with existing projects."""
    print("\n🔗 Testing Project Integration")
    print("=" * 60)
    
    try:
        # Get existing projects
        projects = Project.get_all_projects()
        
        if not projects:
            print("ℹ️ No existing projects found, skipping integration test")
            return True
        
        # Test with first project
        project = projects[0]
        print(f"📁 Testing with project: {project.name}")
        
        # Check current resources
        if project.current_resources:
            print(f"✅ Current resources: {project.current_resources.get_all_resources()}")
            
            # Add a custom resource
            project.current_resources.add_resource("TestResource", 1)
            
            # Save and reload
            project.save_project()
            reloaded_project = Project.load_project(project.project_dir)
            
            # Verify custom resource persisted
            assert reloaded_project.current_resources.get_resource_capacity("TestResource") == 1
            
            # Clean up
            reloaded_project.current_resources.remove_resource("TestResource")
            reloaded_project.save_project()
            
            print("✅ Project integration test passed!")
        else:
            print("⚠️ Project has no resources, creating default")
            project.current_resources = ResourceCapacity()
            project.save_project()
            print("✅ Default resources created for project")
        
        return True
        
    except Exception as e:
        print(f"❌ Project integration test failed: {e}")
        return False

def main():
    """Run all dynamic resource tests."""
    print("🚀 Dynamic Resource Functionality Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Resource capacity functionality
        if not test_resource_capacity_functionality():
            print("\n❌ RESOURCE CAPACITY TESTS FAILED")
            sys.exit(1)
        
        # Test 2: Project integration
        if not test_project_integration():
            print("\n❌ PROJECT INTEGRATION TESTS FAILED")
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Dynamic resource functionality is working correctly")
        print("✅ Backward compatibility maintained")
        print("✅ Custom resource types can be added/removed")
        print("✅ Serialization/deserialization works properly")
        print("✅ Project integration is seamless")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
