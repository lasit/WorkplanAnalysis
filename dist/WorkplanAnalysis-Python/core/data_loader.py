"""Data loading and validation for CSV and YAML files."""

import pandas as pd
import yaml
from pathlib import Path
from typing import List, Dict, Any
from .models import Activity, ResourceCapacity


class DataLoader:
    """Handles loading and validation of workplan and resource data."""
    
    @staticmethod
    def load_workplan_csv(file_path: Path) -> List[Activity]:
        """Load and validate workplan CSV file."""
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {e}")
        
        # Validate required columns
        required_columns = [
            'ActivityID', 'ActivityName', 'Quarter', 'Frequency', 'Duration',
            'RangerCoordinator', 'SeniorRanger', 'Ranger'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        activities = []
        for index, row in df.iterrows():
            try:
                activity = Activity(
                    activity_id=str(row['ActivityID']),
                    name=str(row['ActivityName']),
                    quarter=str(row['Quarter']),
                    frequency=int(row['Frequency']),
                    duration=float(row['Duration']),
                    ranger_coordinator=int(row['RangerCoordinator']),
                    senior_ranger=int(row['SeniorRanger']),
                    ranger=int(row['Ranger'])
                )
                activities.append(activity)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid data in row {index + 1}: {e}")
        
        return activities
    
    @staticmethod
    def load_resources_yaml(file_path: Path) -> ResourceCapacity:
        """Load and validate resource capacity YAML file."""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to read YAML file: {e}")
        
        if not isinstance(data, dict):
            raise ValueError("YAML file must contain a dictionary")
        
        try:
            return ResourceCapacity(
                ranger_coordinator=data.get('RangerCoordinator', 1),
                senior_ranger=data.get('SeniorRanger', 2),
                ranger=data.get('Ranger', 5),
                slots_per_day=data.get('slots_per_day', 4),
                public_holidays=data.get('public_holidays', [])
            )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid resource data: {e}")
    
    @staticmethod
    def save_resources_yaml(resources: ResourceCapacity, file_path: Path) -> None:
        """Save resource capacity to YAML file."""
        data = {
            'RangerCoordinator': resources.ranger_coordinator,
            'SeniorRanger': resources.senior_ranger,
            'Ranger': resources.ranger,
            'slots_per_day': resources.slots_per_day,
            'public_holidays': resources.public_holidays
        }
        
        try:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise ValueError(f"Failed to save YAML file: {e}")
    
    @staticmethod
    def validate_workplan_data(activities: List[Activity]) -> List[str]:
        """Validate workplan data and return list of warnings/errors."""
        warnings = []
        
        if not activities:
            warnings.append("No activities found in workplan")
            return warnings
        
        # Check for duplicate activity IDs
        activity_ids = [a.activity_id for a in activities]
        duplicates = set([x for x in activity_ids if activity_ids.count(x) > 1])
        if duplicates:
            warnings.append(f"Duplicate activity IDs found: {duplicates}")
        
        # Check for activities with no resource requirements
        no_resources = [a.activity_id for a in activities 
                       if a.ranger_coordinator == 0 and a.senior_ranger == 0 and a.ranger == 0]
        if no_resources:
            warnings.append(f"Activities with no resource requirements: {no_resources}")
        
        # Check for high frequency activities
        high_freq = [a.activity_id for a in activities if a.frequency > 10]
        if high_freq:
            warnings.append(f"High frequency activities (>10): {high_freq}")
        
        return warnings
    
    @staticmethod
    def get_workplan_summary(activities: List[Activity]) -> Dict[str, Any]:
        """Get summary statistics for workplan data."""
        if not activities:
            return {}
        
        total_occurrences = sum(a.frequency for a in activities)
        total_demand = {
            'RangerCoordinator': sum(a.ranger_coordinator * a.frequency for a in activities),
            'SeniorRanger': sum(a.senior_ranger * a.frequency for a in activities),
            'Ranger': sum(a.ranger * a.frequency for a in activities)
        }
        
        duration_breakdown = {}
        for activity in activities:
            duration_breakdown[activity.duration] = duration_breakdown.get(activity.duration, 0) + activity.frequency
        
        return {
            'total_activities': len(activities),
            'total_occurrences': total_occurrences,
            'total_demand': total_demand,
            'duration_breakdown': duration_breakdown,
            'quarters': list(set(a.quarter for a in activities))
        }
