"""Data models for Workplan Analysis application."""

import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path


@dataclass
class Activity:
    """Represents a single activity from the workplan CSV."""
    activity_id: str
    name: str
    quarter: str
    frequency: int
    duration: float  # 0.25, 0.5, or 1.0 (quarter-day, half-day, full-day)
    ranger_coordinator: int
    senior_ranger: int
    ranger: int
    
    def __post_init__(self):
        """Validate activity data after initialization."""
        if self.duration not in [0.25, 0.5, 1.0]:
            raise ValueError(f"Invalid duration {self.duration}. Must be 0.25, 0.5, or 1.0")
        if self.frequency < 1:
            raise ValueError(f"Invalid frequency {self.frequency}. Must be >= 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "activity_id": self.activity_id,
            "name": self.name,
            "quarter": self.quarter,
            "frequency": self.frequency,
            "duration": self.duration,
            "ranger_coordinator": self.ranger_coordinator,
            "senior_ranger": self.senior_ranger,
            "ranger": self.ranger
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Activity':
        """Create Activity from dictionary."""
        return cls(
            activity_id=data["activity_id"],
            name=data["name"],
            quarter=data["quarter"],
            frequency=data["frequency"],
            duration=data["duration"],
            ranger_coordinator=data["ranger_coordinator"],
            senior_ranger=data["senior_ranger"],
            ranger=data["ranger"]
        )


@dataclass
class ResourceCapacity:
    """Represents resource capacity configuration with flexible resource types."""
    resources: Dict[str, int] = field(default_factory=dict)  # resource_name -> capacity
    slots_per_day: int = 4
    public_holidays: List[str] = field(default_factory=list)
    
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
            public_holidays=data.get("public_holidays", [])
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
    
    def __post_init__(self):
        """Initialize project with default resources if not provided."""
        if self.current_resources is None:
            self.current_resources = ResourceCapacity()
    
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
                current_resources=current_resources
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
        return {
            "RangerCoordinator": self.activity.ranger_coordinator,
            "SeniorRanger": self.activity.senior_ranger,
            "Ranger": self.activity.ranger
        }
