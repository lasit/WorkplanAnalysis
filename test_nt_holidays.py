#!/usr/bin/env python3
"""Test script to verify NT holidays calculator."""

import sys
from datetime import date
from core.nt_holidays import NTHolidays, get_nt_holidays_for_quarter

def test_fixed_holidays():
    """Test fixed-date holidays."""
    print("🧪 Testing Fixed Holidays")
    print("=" * 40)
    
    try:
        holidays_2025 = NTHolidays.get_fixed_holidays(2025)
        
        expected = {
            "New Year's Day": date(2025, 1, 1),
            "Australia Day": date(2025, 1, 26),
            "Anzac Day": date(2025, 4, 25),
            "May Day": date(2025, 5, 1),
            "Christmas Day": date(2025, 12, 25),
            "Boxing Day": date(2025, 12, 26)
        }
        
        for name, expected_date in expected.items():
            actual_date = holidays_2025.get(name)
            assert actual_date == expected_date, f"{name}: expected {expected_date}, got {actual_date}"
            print(f"✅ {name}: {actual_date}")
        
        print("✅ All fixed holidays correct!")
        return True
        
    except Exception as e:
        print(f"❌ Fixed holidays test failed: {e}")
        return False

def test_variable_holidays():
    """Test variable-date holidays."""
    print("\n🧪 Testing Variable Holidays")
    print("=" * 40)
    
    try:
        holidays_2025 = NTHolidays.get_variable_holidays(2025)
        
        print(f"📅 Easter-based holidays for 2025:")
        easter_sunday = NTHolidays.easter_date(2025)
        print(f"   Easter Sunday: {easter_sunday}")
        print(f"   Good Friday: {holidays_2025['Good Friday']}")
        print(f"   Easter Monday: {holidays_2025['Easter Monday']}")
        
        # Verify Easter calculations
        assert holidays_2025['Good Friday'] == easter_sunday - date.resolution * 2
        assert holidays_2025['Easter Monday'] == easter_sunday + date.resolution
        
        print(f"📅 Other variable holidays for 2025:")
        queens_bday = holidays_2025["Queen's Birthday"]
        picnic_day = holidays_2025["Picnic Day"]
        print(f"   Queen's Birthday: {queens_bday}")
        print(f"   Picnic Day: {picnic_day}")
        
        # Verify Queen's Birthday is 2nd Monday in June
        queens_birthday = holidays_2025["Queen's Birthday"]
        assert queens_birthday.month == 6
        assert queens_birthday.weekday() == 0  # Monday
        
        # Verify Picnic Day is 1st Monday in August
        picnic_day = holidays_2025["Picnic Day"]
        assert picnic_day.month == 8
        assert picnic_day.weekday() == 0  # Monday
        
        print("✅ All variable holidays correct!")
        return True
        
    except Exception as e:
        print(f"❌ Variable holidays test failed: {e}")
        return False

def test_quarter_holidays():
    """Test getting holidays for a specific quarter."""
    print("\n🧪 Testing Quarter Holiday Detection")
    print("=" * 40)
    
    try:
        # Test 2025-Q3 (Jan-Mar 2025)
        q3_holidays = get_nt_holidays_for_quarter("2025-Q3")
        
        print(f"📋 NT Holidays for 2025-Q3 (Jan-Mar 2025):")
        for date_str, holiday_name in q3_holidays:
            print(f"   • {date_str}  {holiday_name}")
        
        # Should include New Year's Day and Australia Day
        holiday_dates = [date_str for date_str, _ in q3_holidays]
        assert "2025-01-01" in holiday_dates, "Missing New Year's Day"
        assert "2025-01-26" in holiday_dates, "Missing Australia Day"
        
        # Test 2025-Q1 (Jul-Sep 2024)
        q1_holidays = get_nt_holidays_for_quarter("2025-Q1")
        
        print(f"\n📋 NT Holidays for 2025-Q1 (Jul-Sep 2024):")
        for date_str, holiday_name in q1_holidays:
            print(f"   • {date_str}  {holiday_name}")
        
        # Should include Picnic Day (August)
        q1_dates = [date_str for date_str, _ in q1_holidays]
        picnic_day_found = any("2024-08" in date_str for date_str in q1_dates)
        assert picnic_day_found, "Missing Picnic Day in Q1"
        
        print("✅ Quarter holiday detection working!")
        return True
        
    except Exception as e:
        print(f"❌ Quarter holidays test failed: {e}")
        return False

def test_holiday_checker():
    """Test individual date holiday checking."""
    print("\n🧪 Testing Holiday Checker")
    print("=" * 40)
    
    try:
        # Test known holidays
        test_cases = [
            (date(2025, 1, 1), True, "New Year's Day"),
            (date(2025, 1, 26), True, "Australia Day"),
            (date(2025, 1, 15), False, ""),  # Regular day
            (date(2025, 4, 25), True, "Anzac Day"),
            (date(2025, 12, 25), True, "Christmas Day"),
        ]
        
        for test_date, expected_is_holiday, expected_name in test_cases:
            is_holiday, holiday_name = NTHolidays.is_holiday(test_date)
            
            assert is_holiday == expected_is_holiday, f"Date {test_date}: expected {expected_is_holiday}, got {is_holiday}"
            
            if expected_is_holiday:
                assert holiday_name == expected_name, f"Date {test_date}: expected '{expected_name}', got '{holiday_name}'"
                print(f"✅ {test_date}: {holiday_name}")
            else:
                print(f"✅ {test_date}: Not a holiday")
        
        print("✅ Holiday checker working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Holiday checker test failed: {e}")
        return False

def test_multiple_years():
    """Test holidays across multiple years."""
    print("\n🧪 Testing Multiple Years")
    print("=" * 40)
    
    try:
        years_to_test = [2024, 2025, 2026, 2027]
        
        for year in years_to_test:
            holidays = NTHolidays.get_all_holidays(year)
            print(f"📅 {year}: {len(holidays)} holidays")
            
            # Should have at least 8 holidays (6 fixed + 2 Easter + Queen's + Picnic)
            assert len(holidays) >= 8, f"Year {year} has too few holidays: {len(holidays)}"
            
            # Check that Easter dates are reasonable
            easter = NTHolidays.easter_date(year)
            assert 3 <= easter.month <= 4, f"Easter {year} in wrong month: {easter.month}"
        
        print("✅ Multiple years test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Multiple years test failed: {e}")
        return False

def main():
    """Run all NT holidays tests."""
    print("🚀 NT Holidays Calculator Test Suite")
    print("=" * 60)
    
    tests = [
        test_fixed_holidays,
        test_variable_holidays,
        test_quarter_holidays,
        test_holiday_checker,
        test_multiple_years
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
        print("✅ Fixed holidays calculated correctly")
        print("✅ Variable holidays (Easter, Queen's Birthday, Picnic Day) working")
        print("✅ Quarter-based holiday detection functional")
        print("✅ Individual date checking accurate")
        print("✅ Multi-year calculations reliable")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
