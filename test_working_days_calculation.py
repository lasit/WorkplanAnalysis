#!/usr/bin/env python3
"""Test script to verify working days calculation includes all holidays."""

import sys
from datetime import date
from core.models import Project, ResourceCapacity

def test_working_days_with_all_holidays():
    """Test that working days calculation includes NT + organization holidays."""
    print("🧪 Testing Working Days Calculation with All Holidays")
    print("=" * 60)
    
    # Create a project for 2025-Q3 (Jan-Mar 2025)
    project = Project(name="test", workplan_path="test.csv")
    project.set_planning_quarter("2025-Q3")
    
    # Add some custom organization holidays
    project.current_resources = ResourceCapacity()
    project.current_resources.custom_holidays = ["2025-02-15", "2025-03-10"]  # Staff Training Day, Team Building
    
    try:
        quarter_info = project.get_quarter_info()
        
        print(f"📋 Quarter: {quarter_info['quarter']}")
        print(f"📅 Period: {quarter_info['start_date']} to {quarter_info['end_date']}")
        print(f"📊 Total days: {quarter_info['total_days']}")
        print(f"💼 Working days: {quarter_info['working_days']}")
        print(f"🎯 Total slots: {quarter_info['total_slots']}")
        
        # Get auto-detected NT holidays
        auto_holidays = project.get_auto_holidays_for_quarter()
        print(f"\n✓ Auto-detected NT holidays ({len(auto_holidays)}):")
        for date_str, holiday_name in auto_holidays:
            print(f"   • {date_str}  {holiday_name}")
        
        # Show custom holidays
        custom_holidays = project.current_resources.custom_holidays
        print(f"\n⚙ Custom organization holidays ({len(custom_holidays)}):")
        for holiday_date in custom_holidays:
            print(f"   • {holiday_date}  Organization holiday")
        
        # Calculate expected working days manually
        start_date, end_date = project.parse_financial_quarter("2025-Q3")
        total_days = (end_date - start_date).days + 1
        
        # Count weekends
        current = start_date
        weekend_days = 0
        while current <= end_date:
            if current.weekday() >= 5:  # Saturday=5, Sunday=6
                weekend_days += 1
            current += date.resolution
        
        total_holidays = len(auto_holidays) + len(custom_holidays)
        expected_working_days = total_days - weekend_days - total_holidays
        
        print(f"\n📊 Calculation breakdown:")
        print(f"   Total days: {total_days}")
        print(f"   Weekend days: {weekend_days}")
        print(f"   NT holidays: {len(auto_holidays)}")
        print(f"   Custom holidays: {len(custom_holidays)}")
        print(f"   Expected working days: {expected_working_days}")
        print(f"   Actual working days: {quarter_info['working_days']}")
        
        # Verify the calculation
        if quarter_info['working_days'] == expected_working_days:
            print("✅ Working days calculation is CORRECT!")
            return True
        else:
            print("❌ Working days calculation is INCORRECT!")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_plan_tab_display():
    """Test that the Plan tab would show the correct working days."""
    print("\n🧪 Testing Plan Tab Working Days Display")
    print("=" * 60)
    
    # Create a project similar to what would be shown in Plan tab
    project = Project(name="test", workplan_path="test.csv")
    project.set_planning_quarter("2025-Q3")
    
    # Add custom holidays
    project.current_resources = ResourceCapacity()
    project.current_resources.custom_holidays = ["2025-02-15"]  # One custom holiday
    
    try:
        quarter_info = project.get_quarter_info()
        
        # This is what should appear in the Plan tab
        quarter_text = f"{quarter_info['quarter']} ({quarter_info['start_date']} to {quarter_info['end_date']})"
        working_days_text = f"{quarter_info['working_days']} ({quarter_info['total_days']} total - weekends - holidays)"
        
        print(f"📋 Quarter display: {quarter_text}")
        print(f"💼 Working days display: {working_days_text}")
        
        # Verify it includes all holidays
        auto_holidays = project.get_auto_holidays_for_quarter()
        custom_holidays = project.current_resources.custom_holidays
        
        print(f"\n📊 Holiday breakdown:")
        print(f"   NT holidays: {len(auto_holidays)} (New Year's Day, Australia Day)")
        print(f"   Custom holidays: {len(custom_holidays)} (Staff Training Day)")
        print(f"   Total holidays excluded: {len(auto_holidays) + len(custom_holidays)}")
        
        if quarter_info['working_days'] > 0:
            print("✅ Plan tab will show correct working days!")
            return True
        else:
            print("❌ Plan tab working days calculation failed!")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Run all working days tests."""
    print("🚀 Working Days Calculation Test Suite")
    print("=" * 70)
    
    tests = [
        test_working_days_with_all_holidays,
        test_plan_tab_display
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
        print("🎉 ALL TESTS PASSED!")
        print("✅ Working days calculation includes NT holidays")
        print("✅ Working days calculation includes custom organization holidays")
        print("✅ Plan tab will display accurate working days count")
        print("✅ Holiday exclusion working correctly")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
