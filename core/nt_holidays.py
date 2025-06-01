"""Northern Territory public holidays calculator with built-in holiday rules."""

from datetime import date, timedelta
from typing import List, Dict, Tuple
import calendar


class NTHolidays:
    """Calculator for Northern Territory public holidays."""
    
    @staticmethod
    def easter_date(year: int) -> date:
        """Calculate Easter Sunday for a given year using the algorithm."""
        # Using the anonymous Gregorian algorithm
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        
        return date(year, month, day)
    
    @staticmethod
    def nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
        """Find the nth occurrence of a weekday in a month.
        
        Args:
            year: Year
            month: Month (1-12)
            weekday: Weekday (0=Monday, 6=Sunday)
            n: Which occurrence (1=first, 2=second, etc.)
        """
        # Find the first day of the month
        first_day = date(year, month, 1)
        
        # Find the first occurrence of the target weekday
        days_ahead = weekday - first_day.weekday()
        if days_ahead < 0:
            days_ahead += 7
        
        first_occurrence = first_day + timedelta(days=days_ahead)
        
        # Calculate the nth occurrence
        target_date = first_occurrence + timedelta(weeks=n-1)
        
        # Make sure it's still in the same month
        if target_date.month != month:
            return None
        
        return target_date
    
    @classmethod
    def get_fixed_holidays(cls, year: int) -> Dict[str, date]:
        """Get fixed-date holidays for NT."""
        holidays = {}
        
        # New Year's Day
        holidays["New Year's Day"] = date(year, 1, 1)
        
        # Australia Day
        holidays["Australia Day"] = date(year, 1, 26)
        
        # Anzac Day
        holidays["Anzac Day"] = date(year, 4, 25)
        
        # May Day (NT specific)
        holidays["May Day"] = date(year, 5, 1)
        
        # Christmas Day
        holidays["Christmas Day"] = date(year, 12, 25)
        
        # Boxing Day
        holidays["Boxing Day"] = date(year, 12, 26)
        
        return holidays
    
    @classmethod
    def get_variable_holidays(cls, year: int) -> Dict[str, date]:
        """Get variable-date holidays for NT."""
        holidays = {}
        
        # Easter-based holidays
        easter_sunday = cls.easter_date(year)
        holidays["Good Friday"] = easter_sunday - timedelta(days=2)
        holidays["Easter Monday"] = easter_sunday + timedelta(days=1)
        
        # Queen's Birthday (second Monday in June)
        queens_birthday = cls.nth_weekday_of_month(year, 6, 0, 2)  # 0=Monday, 2nd occurrence
        if queens_birthday:
            holidays["Queen's Birthday"] = queens_birthday
        
        # Picnic Day (first Monday in August) - NT specific
        picnic_day = cls.nth_weekday_of_month(year, 8, 0, 1)  # 0=Monday, 1st occurrence
        if picnic_day:
            holidays["Picnic Day"] = picnic_day
        
        return holidays
    
    @classmethod
    def get_all_holidays(cls, year: int) -> Dict[str, date]:
        """Get all NT public holidays for a given year."""
        holidays = {}
        holidays.update(cls.get_fixed_holidays(year))
        holidays.update(cls.get_variable_holidays(year))
        return holidays
    
    @classmethod
    def get_holidays_in_period(cls, start_date: date, end_date: date) -> List[Tuple[str, str]]:
        """Get all NT holidays that fall within a date range.
        
        Args:
            start_date: Start of period
            end_date: End of period
            
        Returns:
            List of tuples (date_string, holiday_name)
        """
        holidays_in_period = []
        
        # Get all years that overlap with the period
        years = set()
        current_date = start_date
        while current_date <= end_date:
            years.add(current_date.year)
            # Move to next year
            try:
                current_date = date(current_date.year + 1, 1, 1)
            except ValueError:
                break
        
        # Get holidays for each year and filter by date range
        for year in years:
            year_holidays = cls.get_all_holidays(year)
            
            for holiday_name, holiday_date in year_holidays.items():
                if start_date <= holiday_date <= end_date:
                    date_str = holiday_date.strftime("%Y-%m-%d")
                    holidays_in_period.append((date_str, holiday_name))
        
        # Sort by date
        holidays_in_period.sort(key=lambda x: x[0])
        
        return holidays_in_period
    
    @classmethod
    def get_holiday_dates_in_period(cls, start_date: date, end_date: date) -> List[str]:
        """Get just the date strings for holidays in a period.
        
        Args:
            start_date: Start of period
            end_date: End of period
            
        Returns:
            List of date strings in YYYY-MM-DD format
        """
        holidays = cls.get_holidays_in_period(start_date, end_date)
        return [date_str for date_str, _ in holidays]
    
    @classmethod
    def is_holiday(cls, check_date: date) -> Tuple[bool, str]:
        """Check if a specific date is a NT public holiday.
        
        Args:
            check_date: Date to check
            
        Returns:
            Tuple of (is_holiday, holiday_name)
        """
        year_holidays = cls.get_all_holidays(check_date.year)
        
        for holiday_name, holiday_date in year_holidays.items():
            if holiday_date == check_date:
                return True, holiday_name
        
        return False, ""


# Convenience functions for common use cases
def get_nt_holidays_for_quarter(quarter_str: str) -> List[Tuple[str, str]]:
    """Get NT holidays for a financial quarter.
    
    Args:
        quarter_str: Quarter string like "2025-Q3"
        
    Returns:
        List of tuples (date_string, holiday_name)
    """
    from .models import Project  # Import here to avoid circular imports
    
    # Create a temporary project to parse the quarter
    temp_project = Project(name="temp", workplan_path="temp")
    try:
        start_date, end_date = temp_project.parse_financial_quarter(quarter_str)
        return NTHolidays.get_holidays_in_period(start_date, end_date)
    except Exception:
        return []


def get_nt_holiday_dates_for_quarter(quarter_str: str) -> List[str]:
    """Get NT holiday date strings for a financial quarter.
    
    Args:
        quarter_str: Quarter string like "2025-Q3"
        
    Returns:
        List of date strings in YYYY-MM-DD format
    """
    holidays = get_nt_holidays_for_quarter(quarter_str)
    return [date_str for date_str, _ in holidays]
