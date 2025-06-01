"""Data models for Workplan Analysis application."""

import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from pathlib import Path
import pytz


@dataclass
class Activity:
    """Represents a single activity from the workplan CSV with flexible resource requirements."""
    activity_id: str
    name: str
    quarter: str
    frequency: int
    duration: float  # 0.25, 0.5, or 1.0 (quarter-day, half-day, full-day)
    resource_requirements: Dict[str, int] = field(default_factory=dict)  # resource_name -> quantity
    
    def __post_init__(self):
        """Initialize with default resources if empty and validate data."""
        if not self.resource_requirements:
            # Default to the original three resource types for backward compatibility
            self.resource_requirements = {
                "RangerCoordinator": getattr(self, 'ranger_coordinator', 0),
                "SeniorRanger": getattr(self, 'senior_ranger', 0),
                "Ranger": getattr(self, 'ranger', 0)
            }
        
        if self.duration not in [0.25, 0.5, 1.0]:
            raise ValueError(f"Invalid duration {self.duration}. Must be 0.25, 0.5, or 1.0")
        if self.frequency < 1:
            raise ValueError(f"Invalid frequency {self.frequency}. Must be >= 1")
        if any(req < 0 for req in self.resource_requirements.values()):
            raise ValueError("All resource requirements must be non-negative")
    
    # Backward compatibility properties
    @property
    def ranger_coordinator(self) -> int:
        return self.resource_requirements.get("RangerCoordinator", 0)
    
    @ranger_coordinator.setter
    def ranger_coordinator(self, value: int):
        self.resource_requirements["RangerCoordinator"] = value
    
    @property
    def senior_ranger(self) -> int:
        return self.resource_requirements.get("SeniorRanger", 0)
    
    @senior_ranger.setter
    def senior_ranger(self, value: int):
        self.resource_requirements["SeniorRanger"] = value
    
    @property
    def ranger(self) -> int:
        return self.resource_requirements.get("Ranger", 0)
    
    @ranger.setter
    def ranger(self, value: int):
        self.resource_requirements["Ranger"] = value
    
    def get_resource_requirement(self, resource_name: str) -> int:
        """Get requirement for a specific resource."""
        return self.resource_requirements.get(resource_name, 0)
    
    def set_resource_requirement(self, resource_name: str, quantity: int):
        """Set requirement for a specific resource."""
        if quantity < 0:
            raise ValueError("Resource requirement must be non-negative")
        if quantity == 0:
            # Remove resource if quantity is 0
            self.resource_requirements.pop(resource_name, None)
        else:
            self.resource_requirements[resource_name] = quantity
    
    def get_all_resource_requirements(self) -> Dict[str, int]:
        """Get all resource requirements."""
        return self.resource_requirements.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "activity_id": self.activity_id,
            "name": self.name,
            "quarter": self.quarter,
            "frequency": self.frequency,
            "duration": self.duration,
            "resource_requirements": self.resource_requirements,
            # Keep backward compatibility fields
            "ranger_coordinator": self.ranger_coordinator,
            "senior_ranger": self.senior_ranger,
            "ranger": self.ranger
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Activity':
        """Create Activity from dictionary."""
        # Handle both new format (with resource_requirements) and old format (individual fields)
        if "resource_requirements" in data:
            resource_requirements = data["resource_requirements"]
        else:
            # Backward compatibility: convert old format to new
            resource_requirements = {
                "RangerCoordinator": data.get("ranger_coordinator", 0),
                "SeniorRanger": data.get("senior_ranger", 0),
                "Ranger": data.get("ranger", 0)
            }
        
        activity = cls(
            activity_id=data["activity_id"],
            name=data["name"],
            quarter=data["quarter"],
            frequency=data["frequency"],
            duration=data["duration"],
            resource_requirements=resource_requirements
        )
        
        return activity


@dataclass
class ResourceCapacity:
    """Represents resource capacity configuration with flexible resource types."""
    resources: Dict[str, int] = field(default_factory=dict)  # resource_name -> capacity
    slots_per_day: int = 4
    public_holidays: List[str] = field(default_factory=list)  # Legacy field for backward compatibility
    custom_holidays: List[str] = field(default_factory=list)  # User-added organization holidays
    
    def __post_init__(self):
        """Initialize with default resources if empty and validate data."""
        if not self.resources:
            # Default to the original three resource types for backward compatibility
            self.resources = {
                "RangerCoordinator": 1,
                "SeniorRanger": 2,
                "Ranger": 5
            }
        
        if self.slots_per_day != 4:
            raise ValueError("slots_per_day must be 4 (quarter-day slots)")
        if any(capacity < 0 for capacity in self.resources.values()):
            raise ValueError("All capacity values must be non-negative")
    
    def add_resource(self, resource_name: str, capacity: int = 0):
        """Add a new resource type."""
        if capacity < 0:
            raise ValueError("Capacity must be non-negative")
        self.resources[resource_name] = capacity
    
    def remove_resource(self, resource_name: str):
        """Remove a resource type."""
        if resource_name in self.resources:
            del self.resources[resource_name]
    
    def get_resource_capacity(self, resource_name: str) -> int:
        """Get capacity for a specific resource."""
        return self.resources.get(resource_name, 0)
    
    def set_resource_capacity(self, resource_name: str, capacity: int):
        """Set capacity for a specific resource."""
        if capacity < 0:
            raise ValueError("Capacity must be non-negative")
        self.resources[resource_name] = capacity
    
    def get_all_resources(self) -> Dict[str, int]:
        """Get all resources and their capacities."""
        return self.resources.copy()
    
    # Backward compatibility properties
    @property
    def ranger_coordinator(self) -> int:
        return self.resources.get("RangerCoordinator", 0)
    
    @ranger_coordinator.setter
    def ranger_coordinator(self, value: int):
        self.resources["RangerCoordinator"] = value
    
    @property
    def senior_ranger(self) -> int:
        return self.resources.get("SeniorRanger", 0)
    
    @senior_ranger.setter
    def senior_ranger(self, value: int):
        self.resources["SeniorRanger"] = value
    
    @property
    def ranger(self) -> int:
        return self.resources.get("Ranger", 0)
    
    @ranger.setter
    def ranger(self, value: int):
        self.resources["Ranger"] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "resources": self.resources,
            "slots_per_day": self.slots_per_day,
            "public_holidays": self.public_holidays,
            "custom_holidays": self.custom_holidays,
            # Keep backward compatibility fields
            "ranger_coordinator": self.ranger_coordinator,
            "senior_ranger": self.senior_ranger,
            "ranger": self.ranger
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceCapacity':
        """Create ResourceCapacity from dictionary."""
        # Handle both new format (with resources dict) and old format (individual fields)
        if "resources" in data:
            resources = data["resources"]
        else:
            # Backward compatibility: convert old format to new
            resources = {
                "RangerCoordinator": data.get("ranger_coordinator", 1),
                "SeniorRanger": data.get("senior_ranger", 2),
                "Ranger": data.get("ranger", 5)
            }
        
        return cls(
            resources=resources,
            slots_per_day=data.get("slots_per_day", 4),
            public_holidays=data.get("public_holidays", []),
            custom_holidays=data.get("custom_holidays", [])
        )


@dataclass
class AnalysisResult:
    """Results from a constraint programming analysis."""
    timestamp: datetime
    feasible: bool
    utilization: Dict[str, float]  # Role -> utilization percentage
    overloads: List[Dict[str, Any]] = field(default_factory=list)
    solver_stats: Dict[str, Any] = field(default_factory=dict)
    resource_capacity: Optional[ResourceCapacity] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "feasible": self.feasible,
            "utilization": self.utilization,
            "overloads": self.overloads,
            "solver_stats": self.solver_stats,
            "resource_capacity": self.resource_capacity.to_dict() if self.resource_capacity else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """Create AnalysisResult from dictionary."""
        timestamp = datetime.fromisoformat(data["timestamp"])
        resource_capacity = None
        if data.get("resource_capacity"):
            resource_capacity = ResourceCapacity.from_dict(data["resource_capacity"])
        
        return cls(
            timestamp=timestamp,
            feasible=data["feasible"],
            utilization=data["utilization"],
            overloads=data.get("overloads", []),
            solver_stats=data.get("solver_stats", {}),
            resource_capacity=resource_capacity
        )


@dataclass
class Project:
    """Represents a project containing workplan and analyses."""
    name: str
    workplan_path: Path
    activities: List[Activity] = field(default_factory=list)
    analyses: List[AnalysisResult] = field(default_factory=list)
    current_resources: Optional[ResourceCapacity] = None
    planning_quarter: Optional[str] = None  # e.g., "2025-Q3"
    
    def __post_init__(self):
        """Initialize project with default resources and quarter if not provided."""
        if self.current_resources is None:
            self.current_resources = ResourceCapacity()
        
        # Auto-detect planning quarter from activities if not set
        if self.planning_quarter is None and self.activities:
            self.planning_quarter = self._detect_planning_quarter()
    
    @property
    def project_dir(self) -> Path:
        """Get the project directory path."""
        from pathlib import Path
        # Use projects/ folder in the application directory
        app_dir = Path.cwd()
        return app_dir / "projects" / self.name
    
    def ensure_project_dir(self):
        """Ensure project directory exists."""
        self.project_dir.mkdir(parents=True, exist_ok=True)
    
    def get_latest_analysis(self) -> Optional[AnalysisResult]:
        """Get the most recent analysis result."""
        if not self.analyses:
            return None
        return max(self.analyses, key=lambda a: a.timestamp)
    
    @property
    def project_file(self) -> Path:
        """Get the project file path."""
        return self.project_dir / "project.json"
    
    def save_project(self) -> None:
        """Save project to JSON file."""
        self.ensure_project_dir()
        
        project_data = {
            "name": self.name,
            "workplan_path": str(self.workplan_path),
            "created_at": datetime.now().isoformat(),
            "planning_quarter": self.planning_quarter,
            "activities": [activity.to_dict() for activity in self.activities],
            "current_resources": self.current_resources.to_dict() if self.current_resources else None,
            "analyses": [analysis.to_dict() for analysis in self.analyses]
        }
        
        try:
            with open(self.project_file, 'w') as f:
                json.dump(project_data, f, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save project: {e}")
    
    @classmethod
    def load_project(cls, project_dir: Path) -> 'Project':
        """Load project from JSON file."""
        project_file = project_dir / "project.json"
        
        if not project_file.exists():
            raise FileNotFoundError(f"Project file not found: {project_file}")
        
        try:
            with open(project_file, 'r') as f:
                data = json.load(f)
            
            # Load activities
            activities = [Activity.from_dict(activity_data) for activity_data in data.get("activities", [])]
            
            # Load current resources
            current_resources = None
            if data.get("current_resources"):
                current_resources = ResourceCapacity.from_dict(data["current_resources"])
            
            # Load analyses
            analyses = [AnalysisResult.from_dict(analysis_data) for analysis_data in data.get("analyses", [])]
            
            # Create project
            project = cls(
                name=data["name"],
                workplan_path=Path(data["workplan_path"]),
                activities=activities,
                analyses=analyses,
                current_resources=current_resources,
                planning_quarter=data.get("planning_quarter")
            )
            
            return project
            
        except Exception as e:
            raise ValueError(f"Failed to load project: {e}")
    
    @classmethod
    def get_all_projects(cls) -> List['Project']:
        """Get all available projects from the file system."""
        app_dir = Path.cwd()
        projects_dir = app_dir / "projects"
        
        if not projects_dir.exists():
            return []
        
        projects = []
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                project_file = project_dir / "project.json"
                if project_file.exists():
                    try:
                        project = cls.load_project(project_dir)
                        projects.append(project)
                    except Exception as e:
                        # Skip corrupted projects but log the error
                        print(f"Warning: Could not load project from {project_dir}: {e}")
        
        return projects
    
    def duplicate(self, new_name: str, include_analyses: bool = False) -> 'Project':
        """Create a duplicate of this project with a new name.
        
        Args:
            new_name: Name for the new project
            include_analyses: Whether to include analysis history (default: False)
            
        Returns:
            New Project instance
            
        Raises:
            ValueError: If project with new_name already exists
        """
        import shutil
        from datetime import datetime
        
        # Check if project with new name already exists
        app_dir = Path.cwd()
        new_project_dir = app_dir / "projects" / new_name
        if new_project_dir.exists():
            raise ValueError(f"Project '{new_name}' already exists")
        
        # Create new project directory
        new_project_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all files from current project
        for file_path in self.project_dir.iterdir():
            if file_path.is_file():
                shutil.copy2(file_path, new_project_dir / file_path.name)
        
        # Load the duplicated project
        duplicated_project = Project.load_project(new_project_dir)
        
        # Update project name and paths
        duplicated_project.name = new_name
        duplicated_project.workplan_path = new_project_dir / "workplan.csv"
        
        # Clear analyses if not requested
        if not include_analyses:
            duplicated_project.analyses = []
        
        # Save the updated project
        duplicated_project.save_project()
        
        return duplicated_project
    
    def _detect_planning_quarter(self) -> Optional[str]:
        """Auto-detect planning quarter from activities (most common quarter)."""
        if not self.activities:
            return None
        
        # Count quarters
        quarter_counts = {}
        for activity in self.activities:
            quarter = activity.quarter
            quarter_counts[quarter] = quarter_counts.get(quarter, 0) + 1
        
        # Return most common quarter
        return max(quarter_counts, key=quarter_counts.get)
    
    def parse_financial_quarter(self, quarter_str: str) -> Tuple[date, date]:
        """Parse financial quarter string to start and end dates.
        
        Australian Financial Year Quarters:
        Q1: July, August, September
        Q2: October, November, December
        Q3: January, February, March
        Q4: April, May, June
        
        Args:
            quarter_str: Quarter string like "2025-Q3"
            
        Returns:
            Tuple of (start_date, end_date)
        """
        try:
            year_str, quarter_str = quarter_str.split('-Q')
            year = int(year_str)
            quarter = int(quarter_str)
            
            if quarter == 1:  # Jul-Sep (previous calendar year)
                start_date = date(year - 1, 7, 1)
                end_date = date(year - 1, 9, 30)
            elif quarter == 2:  # Oct-Dec (previous calendar year)
                start_date = date(year - 1, 10, 1)
                end_date = date(year - 1, 12, 31)
            elif quarter == 3:  # Jan-Mar (current calendar year)
                start_date = date(year, 1, 1)
                end_date = date(year, 3, 31)
            elif quarter == 4:  # Apr-Jun (current calendar year)
                start_date = date(year, 4, 1)
                end_date = date(year, 6, 30)
            else:
                raise ValueError(f"Invalid quarter: {quarter}. Must be 1, 2, 3, or 4")
            
            return start_date, end_date
            
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid quarter format '{quarter_str}'. Expected format: 'YYYY-QN' (e.g., '2025-Q3')")
    
    def get_auto_holidays_for_quarter(self) -> List[Tuple[str, str]]:
        """Get auto-detected NT holidays for the planning quarter.
        
        Returns:
            List of tuples (date_string, holiday_name)
        """
        if not self.planning_quarter:
            return []
        
        try:
            from .nt_holidays import get_nt_holidays_for_quarter
            return get_nt_holidays_for_quarter(self.planning_quarter)
        except Exception:
            return []
    
    def get_all_holidays_for_quarter(self) -> List[str]:
        """Get all holidays (auto + custom) for the planning quarter.
        
        Returns:
            List of holiday date strings in YYYY-MM-DD format
        """
        all_holidays = set()
        
        # Add auto-detected NT holidays
        auto_holidays = self.get_auto_holidays_for_quarter()
        for date_str, _ in auto_holidays:
            all_holidays.add(date_str)
        
        # Add custom organization holidays
        if self.current_resources and self.current_resources.custom_holidays:
            all_holidays.update(self.current_resources.custom_holidays)
        
        # Add legacy public holidays for backward compatibility
        if self.current_resources and self.current_resources.public_holidays:
            all_holidays.update(self.current_resources.public_holidays)
        
        return sorted(list(all_holidays))
    
    def calculate_working_days(self, start_date: date, end_date: date, additional_holidays: List[str] = None) -> List[date]:
        """Calculate working days (Mon-Fri) excluding all public holidays.
        
        Args:
            start_date: Start date
            end_date: End date
            additional_holidays: Additional holidays in YYYY-MM-DD format
            
        Returns:
            List of working days
        """
        working_days = []
        current = start_date
        
        # Get all holidays for the period
        all_holidays = set()
        
        # Add auto-detected NT holidays
        try:
            from .nt_holidays import NTHolidays
            nt_holiday_dates = NTHolidays.get_holiday_dates_in_period(start_date, end_date)
            all_holidays.update(nt_holiday_dates)
        except Exception:
            pass  # Fall back to no NT holidays if import fails
        
        # Add custom organization holidays
        if self.current_resources and self.current_resources.custom_holidays:
            all_holidays.update(self.current_resources.custom_holidays)
        
        # Add legacy public holidays for backward compatibility
        if self.current_resources and self.current_resources.public_holidays:
            all_holidays.update(self.current_resources.public_holidays)
        
        # Add additional holidays
        if additional_holidays:
            all_holidays.update(additional_holidays)
        
        # Calculate working days
        while current <= end_date:
            # Check if it's a weekday (Monday=0 to Friday=4)
            if current.weekday() < 5:
                # Check if it's not a public holiday
                date_str = current.strftime("%Y-%m-%d")
                if date_str not in all_holidays:
                    working_days.append(current)
            
            current += timedelta(days=1)
        
        return working_days
    
    def get_quarter_info(self) -> Dict[str, Any]:
        """Get information about the planning quarter.
        
        Returns:
            Dictionary with quarter information
        """
        if not self.planning_quarter:
            return {}
        
        try:
            start_date, end_date = self.parse_financial_quarter(self.planning_quarter)
            working_days = self.calculate_working_days(start_date, end_date)
            
            # Convert to NT timezone for display
            nt_tz = pytz.timezone('Australia/Darwin')
            
            return {
                "quarter": self.planning_quarter,
                "start_date": start_date,
                "end_date": end_date,
                "total_days": (end_date - start_date).days + 1,
                "working_days": len(working_days),
                "working_days_list": working_days,
                "total_slots": len(working_days) * 4,
                "timezone": "Australia/Darwin (NT)"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_valid_activities(self) -> Tuple[List[Activity], List[Activity]]:
        """Get activities that match the planning quarter and those that don't.
        
        Returns:
            Tuple of (valid_activities, excluded_activities)
        """
        if not self.planning_quarter:
            return self.activities, []
        
        valid_activities = []
        excluded_activities = []
        
        for activity in self.activities:
            if activity.quarter == self.planning_quarter:
                valid_activities.append(activity)
            else:
                excluded_activities.append(activity)
        
        return valid_activities, excluded_activities
    
    def set_planning_quarter(self, quarter: str):
        """Set the planning quarter for this project.
        
        Args:
            quarter: Quarter string like "2025-Q3"
        """
        # Validate quarter format
        try:
            self.parse_financial_quarter(quarter)
            self.planning_quarter = quarter
        except ValueError as e:
            raise ValueError(f"Invalid quarter format: {e}")


@dataclass
class Occurrence:
    """Represents a single occurrence of an activity (after frequency expansion)."""
    activity: Activity
    occurrence_index: int  # 0-based index for this occurrence
    assigned_slot: Optional[int] = None  # Slot index when scheduled
    
    @property
    def duration_slots(self) -> int:
        """Get duration in quarter-day slots."""
        return int(self.activity.duration * 4)
    
    @property
    def resource_demands(self) -> Dict[str, int]:
        """Get resource demands for this occurrence."""
        return self.activity.get_all_resource_requirements()
