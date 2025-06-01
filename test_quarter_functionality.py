#!/usr/bin/env python3
"""Test script to verify quarter-based functionality."""

import sys
from datetime import date
from core.models import Project, Activity, ResourceCapacity

def test_quarter_parsing():
    """Test financial quarter parsing."""
    print("🧪 Testing Quarter Parsing")
    print("=" * 50)
    
    project = Project(name="test", workplan_path="test.csv")
    
    # Test Q3 2025 (Jan-Mar 2025)
    try:
        start, end = project.parse_financial_quarter("2025-Q3")
        expected_start = date(2025, 1, 1)
        expected_end = date(2025, 3, 31)
        
        assert start == expected_start, f"Expected {expected_start}, got {start}"
        assert end == expected_end, f"Expected {expected_end}, got {end}"
        print(f"✅ 2025-Q3: {start} to {end}")
        
    except Exception as e:
        print(f"❌ Q3 test failed: {e}")
        return False
    
    # Test Q1 2025 (Jul-Sep 2024)
    try:
        start, end = project.parse_financial_quarter("2025-Q1")
        expected_start = date(2024, 7, 1)
        expected_end = date(2024, 9, 30)
        
        assert start == expected_start, f"Expected {expected_start}, got {start}"
        assert end == expected_end, f"Expected {expected_end}, got {end}"
        print(f"✅ 2025-Q1: {start} to {end}")
        
    except Exception as e:
        print(f"❌ Q1 test failed: {e}")
        return False
    
    print("✅ Quarter parsing tests passed!")
    return True

def test_working_days_calculation():
    """Test working days calculation with NT holidays."""
    print("\n🧪 Testing Working Days Calculation")
    print("=" * 50)
    
    project = Project(name="test", workplan_path="test.csv")
    
    # Test 2025-Q3 (Jan-Mar 2025)
    try:
        start_date = date(2025, 1, 1)
        end_date = date(2025, 3, 31)
        
        working_days = project.calculate_working_days(start_date, end_date)
        
        print(f"📅 Period: {start_date} to {end_date}")
        print(f"📊 Total days: {(end_date - start_date).days + 1}")
        print(f"💼 Working days: {len(working_days)}")
        print(f"🎯 Total slots: {len(working_days) * 4}")
        
        # Check that weekends are excluded
        weekend_count = 0
        for day in working_days:
            if day.weekday() >= 5:  # Saturday=5, Sunday=6
                weekend_count += 1
        
        assert weekend_count == 0, f"Found {weekend_count} weekend days in working days"
        print("✅ No weekends in working days")
        
        # Check that NT holidays are excluded
        nt_holidays = project.get_nt_public_holidays(2025)
        holiday_in_period = []
        for holiday_str in nt_holidays:
            holiday_date = date.fromisoformat(holiday_str)
            if start_date <= holiday_date <= end_date:
                holiday_in_period.append(holiday_date)
        
        for holiday in holiday_in_period:
            assert holiday not in working_days, f"Holiday {holiday} found in working days"
        
        print(f"✅ NT holidays excluded: {holiday_in_period}")
        
    except Exception as e:
        print(f"❌ Working days test failed: {e}")
        return False
    
    print("✅ Working days calculation tests passed!")
    return True

def test_quarter_info():
    """Test quarter info generation."""
    print("\n🧪 Testing Quarter Info Generation")
    print("=" * 50)
    
    project = Project(name="test", workplan_path="test.csv")
    project.set_planning_quarter("2025-Q3")
    
    try:
        quarter_info = project.get_quarter_info()
        
        print(f"📋 Quarter Info:")
        for key, value in quarter_info.items():
            if key != "working_days_list":  # Skip the long list
                print(f"   {key}: {value}")
        
        # Verify required fields
        required_fields = ["quarter", "start_date", "end_date", "total_days", "working_days", "total_slots"]
        for field in required_fields:
            assert field in quarter_info, f"Missing field: {field}"
        
        assert quarter_info["quarter"] == "2025-Q3"
        assert quarter_info["total_days"] == 90  # Jan-Mar = 90 days
        assert quarter_info["working_days"] > 0
        assert quarter_info["total_slots"] == quarter_info["working_days"] * 4
        
        print("✅ Quarter info generation passed!")
        
    except Exception as e:
        print(f"❌ Quarter info test failed: {e}")
        return False
    
    return True

def test_activity_filtering():
    """Test activity filtering by quarter."""
    print("\n🧪 Testing Activity Filtering")
    print("=" * 50)
    
    # Create test activities
    activities = [
        Activity("A01", "Activity 1", "2025-Q3", 1, 0.5, {"Ranger": 1}),
        Activity("A02", "Activity 2", "2025-Q3", 2, 1.0, {"Ranger": 2}),
        Activity("A03", "Activity 3", "2025-Q2", 1, 0.25, {"Ranger": 1}),  # Different quarter
        Activity("A04", "Activity 4", "2025-Q3", 1, 0.5, {"Ranger": 1}),
    ]
    
    project = Project(name="test", workplan_path="test.csv", activities=activities)
    project.set_planning_quarter("2025-Q3")
    
    try:
        valid_activities, excluded_activities = project.get_valid_activities()
        
        print(f"📊 Total activities: {len(activities)}")
        print(f"✅ Valid activities (Q3): {len(valid_activities)}")
        print(f"❌ Excluded activities: {len(excluded_activities)}")
        
        # Check that filtering worked correctly
        assert len(valid_activities) == 3, f"Expected 3 valid activities, got {len(valid_activities)}"
        assert len(excluded_activities) == 1, f"Expected 1 excluded activity, got {len(excluded_activities)}"
        
        # Check that excluded activity is the Q2 one
        assert excluded_activities[0].activity_id == "A03"
        assert excluded_activities[0].quarter == "2025-Q2"
        
        # Check that all valid activities are Q3
        for activity in valid_activities:
            assert activity.quarter == "2025-Q3"
        
        print("✅ Activity filtering tests passed!")
        
    except Exception as e:
        print(f"❌ Activity filtering test failed: {e}")
        return False
    
    return True

def test_quarter_auto_detection():
    """Test automatic quarter detection."""
    print("\n🧪 Testing Quarter Auto-Detection")
    print("=" * 50)
    
    # Create activities with mixed quarters (Q3 should be most common)
    activities = [
        Activity("A01", "Activity 1", "2025-Q3", 1, 0.5, {"Ranger": 1}),
        Activity("A02", "Activity 2", "2025-Q3", 1, 1.0, {"Ranger": 2}),
        Activity("A03", "Activity 3", "2025-Q3", 1, 0.25, {"Ranger": 1}),
        Activity("A04", "Activity 4", "2025-Q2", 1, 0.5, {"Ranger": 1}),  # Minority
    ]
    
    try:
        project = Project(name="test", workplan_path="test.csv", activities=activities)
        
        # Should auto-detect Q3 as the most common quarter
        detected_quarter = project.planning_quarter
        print(f"🔍 Auto-detected quarter: {detected_quarter}")
        
        assert detected_quarter == "2025-Q3", f"Expected 2025-Q3, got {detected_quarter}"
        
        print("✅ Quarter auto-detection tests passed!")
        
    except Exception as e:
        print(f"❌ Quarter auto-detection test failed: {e}")
        return False
    
    return True

def main():
    """Run all quarter functionality tests."""
    print("🚀 Quarter Functionality Test Suite")
    print("=" * 60)
    
    tests = [
        test_quarter_parsing,
        test_working_days_calculation,
        test_quarter_info,
        test_activity_filtering,
        test_quarter_auto_detection
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
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Quarter parsing works correctly")
        print("✅ Working days calculation excludes weekends and NT holidays")
        print("✅ Quarter info generation provides accurate data")
        print("✅ Activity filtering by quarter works properly")
        print("✅ Auto-detection of planning quarter works")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
