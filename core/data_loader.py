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
                # Build resource requirements from CSV columns
                resource_requirements = {}
                
                # Handle standard resource columns
                if 'RangerCoordinator' in row:
                    resource_requirements['RangerCoordinator'] = int(row['RangerCoordinator'])
                if 'SeniorRanger' in row:
                    resource_requirements['SeniorRanger'] = int(row['SeniorRanger'])
                if 'Ranger' in row:
                    resource_requirements['Ranger'] = int(row['Ranger'])
                
                # Handle any additional resource columns
                for col in df.columns:
                    if col not in ['ActivityID', 'ActivityName', 'Quarter', 'Frequency', 'Duration', 
                                   'RangerCoordinator', 'SeniorRanger', 'Ranger']:
                        # This is a custom resource column
                        try:
                            value = int(row[col])
                            if value > 0:
                                resource_requirements[col] = value
                        except (ValueError, TypeError):
                            pass  # Skip invalid resource values
                
                activity = Activity(
                    activity_id=str(row['ActivityID']),
                    name=str(row['ActivityName']),
                    quarter=str(row['Quarter']),
                    frequency=int(row['Frequency']),
                    duration=float(row['Duration']),
                    resource_requirements=resource_requirements
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
            # Build resources dictionary from YAML data
            resources = {}
            
            # Handle standard resource types
            if 'RangerCoordinator' in data:
                resources['RangerCoordinator'] = data['RangerCoordinator']
            if 'SeniorRanger' in data:
                resources['SeniorRanger'] = data['SeniorRanger']
            if 'Ranger' in data:
                resources['Ranger'] = data['Ranger']
            
            # Handle any additional resource types
            for key, value in data.items():
                if key not in ['RangerCoordinator', 'SeniorRanger', 'Ranger', 'slots_per_day', 'public_holidays', 'custom_holidays']:
                    if isinstance(value, int) and value >= 0:
                        resources[key] = value
            
            # If no resources found, use defaults
            if not resources:
                resources = {
                    'RangerCoordinator': 1,
                    'SeniorRanger': 2,
                    'Ranger': 5
                }
            
            return ResourceCapacity(
                resources=resources,
                slots_per_day=data.get('slots_per_day', 4),
                public_holidays=data.get('public_holidays', []),
                custom_holidays=data.get('custom_holidays', [])
            )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid resource data: {e}")
    
    @staticmethod
    def save_resources_yaml(resources: ResourceCapacity, file_path: Path) -> None:
        """Save resource capacity to YAML file."""
        # Build data from the new dynamic structure
        data = resources.get_all_resources().copy()  # Get all resource types
        
        # Add other fields
        data['slots_per_day'] = resources.slots_per_day
        
        # Add legacy public holidays for backward compatibility
        if resources.public_holidays:
            data['public_holidays'] = resources.public_holidays
        
        # Add custom organization holidays
        if resources.custom_holidays:
            data['custom_holidays'] = resources.custom_holidays
        
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
        
        # Calculate total demand for all resource types
        total_demand = {}
        for activity in activities:
            requirements = activity.get_all_resource_requirements()
            for resource_name, quantity in requirements.items():
                if resource_name not in total_demand:
                    total_demand[resource_name] = 0
                total_demand[resource_name] += quantity * activity.frequency
        
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
