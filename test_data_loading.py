#!/usr/bin/env python3
"""
Test script to verify data loading functionality.
"""

from pathlib import Path
from core.data_loader import DataLoader
from core.models import Project

def test_sample_data():
    """Test loading the sample data files."""
    print("Testing Workplan Analysis Data Loading")
    print("=" * 50)
    
    # Test CSV loading
    csv_path = Path("sample_workplan.csv")
    if csv_path.exists():
        print(f"Loading workplan from: {csv_path}")
        try:
            activities = DataLoader.load_workplan_csv(csv_path)
            print(f"✅ Successfully loaded {len(activities)} activities")
            
            # Show first few activities
            print("\nFirst 3 activities:")
            for i, activity in enumerate(activities[:3]):
                print(f"  {i+1}. {activity.activity_id}: {activity.name}")
                print(f"     Frequency: {activity.frequency}, Duration: {activity.duration}")
                print(f"     Resources: RC={activity.ranger_coordinator}, SR={activity.senior_ranger}, R={activity.ranger}")
            
            # Validate data
            warnings = DataLoader.validate_workplan_data(activities)
            if warnings:
                print(f"\n⚠️  Validation warnings:")
                for warning in warnings:
                    print(f"   - {warning}")
            else:
                print("\n✅ No validation warnings")
            
            # Get summary
            summary = DataLoader.get_workplan_summary(activities)
            print(f"\nWorkplan Summary:")
            print(f"  Total activities: {summary.get('total_activities', 0)}")
            print(f"  Total occurrences: {summary.get('total_occurrences', 0)}")
            print(f"  Quarters: {', '.join(summary.get('quarters', []))}")
            print(f"  Total demand: {summary.get('total_demand', {})}")
            
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
    else:
        print(f"❌ CSV file not found: {csv_path}")
    
    print()
    
    # Test YAML loading
    yaml_path = Path("sample_resources.yml")
    if yaml_path.exists():
        print(f"Loading resources from: {yaml_path}")
        try:
            resources = DataLoader.load_resources_yaml(yaml_path)
            print(f"✅ Successfully loaded resource configuration")
            print(f"  Ranger Coordinator: {resources.ranger_coordinator}")
            print(f"  Senior Ranger: {resources.senior_ranger}")
            print(f"  Ranger: {resources.ranger}")
            print(f"  Slots per day: {resources.slots_per_day}")
            print(f"  Public holidays: {resources.public_holidays}")
            
        except Exception as e:
            print(f"❌ Error loading YAML: {e}")
    else:
        print(f"❌ YAML file not found: {yaml_path}")
    
    print("\n" + "=" * 50)
    print("Data loading test completed!")

if __name__ == "__main__":
    test_sample_data()
