"""Plan tab for displaying and editing workplan activities."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel,
    QHeaderView, QPushButton, QGroupBox, QGridLayout, QMessageBox, QInputDialog,
    QComboBox, QSpinBox, QDoubleSpinBox, QDialog, QDialogButtonBox, QFormLayout,
    QLineEdit, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Optional, Dict, Any

from core.models import Project, Activity
from core.data_loader import DataLoader


class ActivityEditDialog(QDialog):
    """Dialog for editing or creating activities."""
    
    def __init__(self, activity: Optional[Activity] = None, available_resources: List[str] = None, parent=None):
        super().__init__(parent)
        self.activity = activity
        self.available_resources = available_resources or []
        self.resource_spinboxes = {}
        self.setup_ui()
        
        if activity:
            self.populate_fields()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Edit Activity" if self.activity else "Add Activity")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Form layout for basic fields
        form_layout = QFormLayout()
        
        # Activity ID
        self.id_edit = QLineEdit()
        form_layout.addRow("Activity ID:", self.id_edit)
        
        # Activity Name
        self.name_edit = QLineEdit()
        form_layout.addRow("Activity Name:", self.name_edit)
        
        # Quarter
        self.quarter_edit = QLineEdit()
        self.quarter_edit.setPlaceholderText("e.g., 2025-Q3")
        form_layout.addRow("Quarter:", self.quarter_edit)
        
        # Frequency
        self.frequency_spinbox = QSpinBox()
        self.frequency_spinbox.setRange(1, 100)
        self.frequency_spinbox.setValue(1)
        form_layout.addRow("Frequency:", self.frequency_spinbox)
        
        # Duration
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["0.25 (Quarter-day)", "0.5 (Half-day)", "1.0 (Full-day)"])
        form_layout.addRow("Duration:", self.duration_combo)
        
        layout.addLayout(form_layout)
        
        # Resource requirements section
        resources_group = QGroupBox("Resource Requirements")
        resources_layout = QVBoxLayout(resources_group)
        
        # Table for resource requirements
        self.resources_table = QTableWidget()
        self.resources_table.setColumnCount(2)
        self.resources_table.setHorizontalHeaderLabels(["Resource Type", "Quantity"])
        self.resources_table.horizontalHeader().setStretchLastSection(True)
        self.resources_table.setMaximumHeight(200)
        resources_layout.addWidget(self.resources_table)
        
        # Buttons for managing resources
        resource_buttons_layout = QHBoxLayout()
        
        self.add_resource_button = QPushButton("Add Resource")
        self.add_resource_button.clicked.connect(self.add_resource_requirement)
        resource_buttons_layout.addWidget(self.add_resource_button)
        
        self.remove_resource_button = QPushButton("Remove Selected")
        self.remove_resource_button.clicked.connect(self.remove_resource_requirement)
        resource_buttons_layout.addWidget(self.remove_resource_button)
        
        resource_buttons_layout.addStretch()
        resources_layout.addLayout(resource_buttons_layout)
        
        layout.addWidget(resources_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def populate_fields(self):
        """Populate fields with activity data."""
        if not self.activity:
            return
        
        self.id_edit.setText(self.activity.activity_id)
        self.name_edit.setText(self.activity.name)
        self.quarter_edit.setText(self.activity.quarter)
        self.frequency_spinbox.setValue(self.activity.frequency)
        
        # Set duration
        duration_map = {0.25: 0, 0.5: 1, 1.0: 2}
        self.duration_combo.setCurrentIndex(duration_map.get(self.activity.duration, 0))
        
        # Populate resource requirements
        self.populate_resource_requirements(self.activity.get_all_resource_requirements())
    
    def populate_resource_requirements(self, requirements: Dict[str, int]):
        """Populate the resource requirements table."""
        self.resources_table.setRowCount(len(requirements))
        
        for row, (resource_name, quantity) in enumerate(requirements.items()):
            # Resource name
            name_item = QTableWidgetItem(resource_name)
            self.resources_table.setItem(row, 0, name_item)
            
            # Quantity
            quantity_item = QTableWidgetItem(str(quantity))
            self.resources_table.setItem(row, 1, quantity_item)
    
    def add_resource_requirement(self):
        """Add a new resource requirement."""
        # Show dialog to select resource type
        if self.available_resources:
            resource_name, ok = QInputDialog.getItem(
                self,
                "Add Resource Requirement",
                "Select resource type:",
                self.available_resources,
                0,
                False
            )
        else:
            resource_name, ok = QInputDialog.getText(
                self,
                "Add Resource Requirement",
                "Enter resource type name:"
            )
        
        if not ok or not resource_name:
            return
        
        # Check for duplicates
        for row in range(self.resources_table.rowCount()):
            existing_name = self.resources_table.item(row, 0)
            if existing_name and existing_name.text() == resource_name:
                QMessageBox.information(
                    self,
                    "Duplicate Resource",
                    f"Resource '{resource_name}' is already in the list."
                )
                return
        
        # Add new row
        row_count = self.resources_table.rowCount()
        self.resources_table.setRowCount(row_count + 1)
        
        name_item = QTableWidgetItem(resource_name)
        quantity_item = QTableWidgetItem("1")
        
        self.resources_table.setItem(row_count, 0, name_item)
        self.resources_table.setItem(row_count, 1, quantity_item)
    
    def remove_resource_requirement(self):
        """Remove the selected resource requirement."""
        current_row = self.resources_table.currentRow()
        if current_row < 0:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a resource requirement to remove."
            )
            return
        
        self.resources_table.removeRow(current_row)
    
    def get_activity_data(self) -> Dict[str, Any]:
        """Get the activity data from the dialog."""
        # Get duration value
        duration_values = [0.25, 0.5, 1.0]
        duration = duration_values[self.duration_combo.currentIndex()]
        
        # Get resource requirements
        resource_requirements = {}
        for row in range(self.resources_table.rowCount()):
            name_item = self.resources_table.item(row, 0)
            quantity_item = self.resources_table.item(row, 1)
            
            if name_item and quantity_item:
                resource_name = name_item.text().strip()
                try:
                    quantity = int(quantity_item.text())
                    if quantity > 0 and resource_name:
                        resource_requirements[resource_name] = quantity
                except ValueError:
                    pass
        
        return {
            "activity_id": self.id_edit.text().strip(),
            "name": self.name_edit.text().strip(),
            "quarter": self.quarter_edit.text().strip(),
            "frequency": self.frequency_spinbox.value(),
            "duration": duration,
            "resource_requirements": resource_requirements
        }


class PlanTab(QWidget):
    """Tab for displaying and editing workplan data."""
    
    # Signals
    plan_changed = pyqtSignal()  # Emitted when plan is modified
    
    def __init__(self):
        super().__init__()
        self.current_project: Optional[Project] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Summary section
        self.setup_summary_section(layout)
        
        # Activities table with editing capabilities
        self.setup_activities_section(layout)
    
    def setup_summary_section(self, parent_layout):
        """Set up the summary information section."""
        summary_group = QGroupBox("Workplan Summary")
        summary_layout = QGridLayout(summary_group)
        
        # Create summary labels
        self.total_activities_label = QLabel("0")
        self.total_occurrences_label = QLabel("0")
        self.quarter_label = QLabel("-")
        self.working_days_label = QLabel("-")
        
        # Resource demand labels (will be dynamic based on available resources)
        self.resource_demand_labels = {}
        
        # Duration breakdown labels
        self.quarter_day_label = QLabel("0")
        self.half_day_label = QLabel("0")
        self.full_day_label = QLabel("0")
        
        # Make value labels bold
        font = QFont()
        font.setBold(True)
        for label in [self.total_activities_label, self.total_occurrences_label, 
                     self.quarter_label, self.working_days_label, self.quarter_day_label, 
                     self.half_day_label, self.full_day_label]:
            label.setFont(font)
        
        # Layout summary information
        row = 0
        summary_layout.addWidget(QLabel("Total Activities:"), row, 0)
        summary_layout.addWidget(self.total_activities_label, row, 1)
        summary_layout.addWidget(QLabel("Total Occurrences:"), row, 2)
        summary_layout.addWidget(self.total_occurrences_label, row, 3)
        summary_layout.addWidget(QLabel("Working Days:"), row, 4)
        summary_layout.addWidget(self.working_days_label, row, 5)
        
        row += 1
        summary_layout.addWidget(QLabel("Quarter:"), row, 0)
        summary_layout.addWidget(self.quarter_label, row, 1, 1, 5)
        
        row += 1
        summary_layout.addWidget(QLabel("Duration Breakdown:"), row, 0, 1, 6)
        
        row += 1
        summary_layout.addWidget(QLabel("  Quarter-day (0.25):"), row, 0)
        summary_layout.addWidget(self.quarter_day_label, row, 1)
        summary_layout.addWidget(QLabel("  Half-day (0.5):"), row, 2)
        summary_layout.addWidget(self.half_day_label, row, 3)
        summary_layout.addWidget(QLabel("  Full-day (1.0):"), row, 4)
        summary_layout.addWidget(self.full_day_label, row, 5)
        
        # Resource demand section will be added dynamically
        self.summary_layout = summary_layout
        self.resource_demand_row = row + 1
        
        parent_layout.addWidget(summary_group)
    
    def setup_activities_section(self, parent_layout):
        """Set up the activities editing section."""
        activities_group = QGroupBox("Activities")
        activities_layout = QVBoxLayout(activities_group)
        
        # Buttons for managing activities
        buttons_layout = QHBoxLayout()
        
        self.add_activity_button = QPushButton("Add Activity")
        self.add_activity_button.clicked.connect(self.add_activity)
        buttons_layout.addWidget(self.add_activity_button)
        
        self.edit_activity_button = QPushButton("Edit Selected")
        self.edit_activity_button.clicked.connect(self.edit_activity)
        buttons_layout.addWidget(self.edit_activity_button)
        
        self.remove_activity_button = QPushButton("Remove Selected")
        self.remove_activity_button.clicked.connect(self.remove_activity)
        buttons_layout.addWidget(self.remove_activity_button)
        
        buttons_layout.addStretch()
        
        self.save_plan_button = QPushButton("Save Plan")
        self.save_plan_button.clicked.connect(self.save_plan)
        self.save_plan_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        buttons_layout.addWidget(self.save_plan_button)
        
        activities_layout.addLayout(buttons_layout)
        
        # Activities table
        self.activities_table = QTableWidget()
        self.activities_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.activities_table.setAlternatingRowColors(True)
        self.activities_table.setSortingEnabled(True)
        self.activities_table.itemDoubleClicked.connect(self.edit_activity)
        activities_layout.addWidget(self.activities_table)
        
        parent_layout.addWidget(activities_group)
    
    def set_project(self, project: Project):
        """Set the current project and update the display."""
        self.current_project = project
        self.update_display()
    
    def update_display(self):
        """Update the display with current project data."""
        if not self.current_project:
            self.clear_display()
            return
        
        # Update activities table
        self.populate_activities_table()
        
        # Update summary
        self.update_summary()
    
    def populate_activities_table(self):
        """Populate the activities table with dynamic columns."""
        if not self.current_project:
            return
        
        activities = self.current_project.activities
        
        # Get all unique resource types from activities and project resources
        all_resource_types = set()
        for activity in activities:
            all_resource_types.update(activity.get_all_resource_requirements().keys())
        
        if self.current_project.current_resources:
            all_resource_types.update(self.current_project.current_resources.get_all_resources().keys())
        
        # Create column headers
        base_headers = ["Activity ID", "Activity Name", "Quarter", "Frequency", "Duration"]
        resource_headers = sorted(list(all_resource_types))
        headers = base_headers + resource_headers
        
        # Set up table
        self.activities_table.setRowCount(len(activities))
        self.activities_table.setColumnCount(len(headers))
        self.activities_table.setHorizontalHeaderLabels(headers)
        
        # Populate data
        for row, activity in enumerate(activities):
            # Basic fields
            self.activities_table.setItem(row, 0, QTableWidgetItem(activity.activity_id))
            self.activities_table.setItem(row, 1, QTableWidgetItem(activity.name))
            self.activities_table.setItem(row, 2, QTableWidgetItem(activity.quarter))
            self.activities_table.setItem(row, 3, QTableWidgetItem(str(activity.frequency)))
            self.activities_table.setItem(row, 4, QTableWidgetItem(str(activity.duration)))
            
            # Resource requirements
            requirements = activity.get_all_resource_requirements()
            for col, resource_type in enumerate(resource_headers, start=5):
                quantity = requirements.get(resource_type, 0)
                self.activities_table.setItem(row, col, QTableWidgetItem(str(quantity)))
        
        # Configure column widths
        header = self.activities_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Activity Name
        
        # Set minimum widths for other columns
        for i in range(len(headers)):
            if i != 1:  # Not the activity name column
                self.activities_table.setColumnWidth(i, 100)
    
    def update_summary(self):
        """Update the summary section with dynamic resource information."""
        if not self.current_project or not self.current_project.activities:
            self.clear_summary()
            return
        
        # Get valid activities for the planning quarter
        valid_activities, excluded_activities = self.current_project.get_valid_activities()
        
        # Show quarter and working days information if available
        if self.current_project.planning_quarter:
            quarter_info = self.current_project.get_quarter_info()
            if quarter_info and not quarter_info.get('error'):
                quarter_text = f"{quarter_info['quarter']} ({quarter_info['start_date']} to {quarter_info['end_date']})"
                self.quarter_label.setText(quarter_text)
                
                working_days_text = f"{quarter_info['working_days']} ({quarter_info['total_days']} total - weekends - holidays)"
                self.working_days_label.setText(working_days_text)
            else:
                self.quarter_label.setText(self.current_project.planning_quarter)
                self.working_days_label.setText("-")
        else:
            self.working_days_label.setText("-")
        
        # Use valid activities for summary (only those matching the quarter)
        summary = DataLoader.get_workplan_summary(valid_activities)
        
        # Add excluded activities info to summary
        if excluded_activities:
            summary['excluded_activities'] = len(excluded_activities)
            summary['excluded_activities_list'] = [f"{a.activity_id} ({a.quarter})" for a in excluded_activities]
        
        # Basic counts
        self.total_activities_label.setText(str(summary.get('total_activities', 0)))
        self.total_occurrences_label.setText(str(summary.get('total_occurrences', 0)))
        
        # Note: Quarter and working days are already set above, don't override them here
        
        # Duration breakdown
        duration_breakdown = summary.get('duration_breakdown', {})
        self.quarter_day_label.setText(str(duration_breakdown.get(0.25, 0)))
        self.half_day_label.setText(str(duration_breakdown.get(0.5, 0)))
        self.full_day_label.setText(str(duration_breakdown.get(1.0, 0)))
        
        # Update resource demand section
        self.update_resource_demand_display(summary.get('total_demand', {}))
    
    def update_resource_demand_display(self, total_demand: Dict[str, int]):
        """Update the resource demand display with dynamic resources."""
        # Clear existing resource demand labels
        for label in self.resource_demand_labels.values():
            label.setParent(None)
        self.resource_demand_labels.clear()
        
        if not total_demand:
            return
        
        # Add resource demand section
        row = self.resource_demand_row
        self.summary_layout.addWidget(QLabel("Resource Demand:"), row, 0, 1, 6)
        
        # Add resource demand labels
        col = 0
        for resource_name, demand in sorted(total_demand.items()):
            if col >= 6:  # Start new row if too many resources
                row += 1
                col = 0
            
            label_text = f"  {resource_name}:"
            demand_label = QLabel(str(demand))
            
            font = QFont()
            font.setBold(True)
            demand_label.setFont(font)
            
            self.summary_layout.addWidget(QLabel(label_text), row, col)
            self.summary_layout.addWidget(demand_label, row, col + 1)
            
            self.resource_demand_labels[resource_name] = demand_label
            col += 2
    
    def add_activity(self):
        """Add a new activity."""
        if not self.current_project:
            QMessageBox.information(self, "No Project", "Please select a project first.")
            return
        
        # Get available resource types
        available_resources = []
        if self.current_project.current_resources:
            available_resources = list(self.current_project.current_resources.get_all_resources().keys())
        
        dialog = ActivityEditDialog(available_resources=available_resources, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            activity_data = dialog.get_activity_data()
            
            # Validate required fields
            if not activity_data["activity_id"] or not activity_data["name"]:
                QMessageBox.warning(self, "Invalid Data", "Activity ID and Name are required.")
                return
            
            # Check for duplicate ID
            existing_ids = [a.activity_id for a in self.current_project.activities]
            if activity_data["activity_id"] in existing_ids:
                QMessageBox.warning(self, "Duplicate ID", "An activity with this ID already exists.")
                return
            
            # Create new activity
            try:
                activity = Activity(
                    activity_id=activity_data["activity_id"],
                    name=activity_data["name"],
                    quarter=activity_data["quarter"],
                    frequency=activity_data["frequency"],
                    duration=activity_data["duration"],
                    resource_requirements=activity_data["resource_requirements"]
                )
                
                self.current_project.activities.append(activity)
                self.update_display()
                self.plan_changed.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create activity: {str(e)}")
    
    def edit_activity(self):
        """Edit the selected activity."""
        current_row = self.activities_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", "Please select an activity to edit.")
            return
        
        if not self.current_project or current_row >= len(self.current_project.activities):
            return
        
        activity = self.current_project.activities[current_row]
        
        # Get available resource types
        available_resources = []
        if self.current_project.current_resources:
            available_resources = list(self.current_project.current_resources.get_all_resources().keys())
        
        dialog = ActivityEditDialog(activity=activity, available_resources=available_resources, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            activity_data = dialog.get_activity_data()
            
            # Validate required fields
            if not activity_data["activity_id"] or not activity_data["name"]:
                QMessageBox.warning(self, "Invalid Data", "Activity ID and Name are required.")
                return
            
            # Check for duplicate ID (excluding current activity)
            existing_ids = [a.activity_id for i, a in enumerate(self.current_project.activities) if i != current_row]
            if activity_data["activity_id"] in existing_ids:
                QMessageBox.warning(self, "Duplicate ID", "An activity with this ID already exists.")
                return
            
            # Update activity
            try:
                activity.activity_id = activity_data["activity_id"]
                activity.name = activity_data["name"]
                activity.quarter = activity_data["quarter"]
                activity.frequency = activity_data["frequency"]
                activity.duration = activity_data["duration"]
                activity.resource_requirements = activity_data["resource_requirements"]
                
                self.update_display()
                self.plan_changed.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update activity: {str(e)}")
    
    def remove_activity(self):
        """Remove the selected activity."""
        current_row = self.activities_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", "Please select an activity to remove.")
            return
        
        if not self.current_project or current_row >= len(self.current_project.activities):
            return
        
        activity = self.current_project.activities[current_row]
        
        reply = QMessageBox.question(
            self,
            "Remove Activity",
            f"Are you sure you want to remove activity '{activity.name}' ({activity.activity_id})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_project.activities.pop(current_row)
            self.update_display()
            self.plan_changed.emit()
    
    def save_plan(self):
        """Save the current plan to the project."""
        if not self.current_project:
            QMessageBox.information(self, "No Project", "No project to save.")
            return
        
        try:
            # Save the project
            self.current_project.save_project()
            
            # Also update the CSV file
            self.save_plan_to_csv()
            
            QMessageBox.information(self, "Plan Saved", "Plan has been saved successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save plan: {str(e)}")
    
    def save_plan_to_csv(self):
        """Save the plan to CSV file."""
        if not self.current_project:
            return
        
        import csv
        
        csv_path = self.current_project.workplan_path
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Get all resource types
            all_resources = set()
            for activity in self.current_project.activities:
                all_resources.update(activity.get_all_resource_requirements().keys())
            
            # Create headers
            headers = ["ActivityID", "ActivityName", "Quarter", "Frequency", "Duration"]
            headers.extend(sorted(all_resources))
            
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            # Write activities
            for activity in self.current_project.activities:
                row = [
                    activity.activity_id,
                    activity.name,
                    activity.quarter,
                    activity.frequency,
                    activity.duration
                ]
                
                # Add resource requirements
                requirements = activity.get_all_resource_requirements()
                for resource in sorted(all_resources):
                    row.append(requirements.get(resource, 0))
                
                writer.writerow(row)
    
    def clear_display(self):
        """Clear the display."""
        self.activities_table.setRowCount(0)
        self.activities_table.setColumnCount(0)
        self.clear_summary()
    
    def clear_summary(self):
        """Clear the summary section."""
        self.total_activities_label.setText("0")
        self.total_occurrences_label.setText("0")
        self.quarter_label.setText("-")
        self.working_days_label.setText("-")
        self.quarter_day_label.setText("0")
        self.half_day_label.setText("0")
        self.full_day_label.setText("0")
        
        # Clear resource demand labels
        for label in self.resource_demand_labels.values():
            label.setParent(None)
        self.resource_demand_labels.clear()
