"""Resources tab for editing resource capacity configuration with dynamic resource types."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QSpinBox, QGroupBox, QListWidget, QListWidgetItem,
    QMessageBox, QDateEdit, QFrame, QInputDialog, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from typing import Optional, List, Dict
from datetime import datetime

from core.models import Project, ResourceCapacity


class ResourcesTab(QWidget):
    """Tab for editing resource capacity configuration."""
    
    # Signals
    resources_changed = pyqtSignal(object)  # ResourceCapacity
    
    def __init__(self):
        super().__init__()
        self.current_project: Optional[Project] = None
        self.current_resources: Optional[ResourceCapacity] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Resource capacity section
        self.setup_capacity_section(layout)
        
        # Public holidays section
        self.setup_holidays_section(layout)
        
        # Action buttons
        self.setup_action_buttons(layout)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def setup_capacity_section(self, parent_layout):
        """Set up the resource capacity editing section with dynamic resource types."""
        capacity_group = QGroupBox("Resource Capacity")
        capacity_layout = QVBoxLayout(capacity_group)
        
        # Title and description
        title_label = QLabel("Resource Types and Capacity")
        title_font = QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)
        capacity_layout.addWidget(title_label)
        
        desc_label = QLabel("Configure resource types and how many are available per time slot.")
        desc_label.setStyleSheet("color: gray;")
        capacity_layout.addWidget(desc_label)
        
        # Resource table
        table_layout = QVBoxLayout()
        
        # Table for resources
        self.resources_table = QTableWidget()
        self.resources_table.setColumnCount(2)
        self.resources_table.setHorizontalHeaderLabels(["Resource Type", "Capacity"])
        self.resources_table.horizontalHeader().setStretchLastSection(True)
        self.resources_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.resources_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.resources_table.setMaximumHeight(200)
        self.resources_table.itemChanged.connect(self.on_table_item_changed)
        table_layout.addWidget(self.resources_table)
        
        # Buttons for managing resources
        buttons_layout = QHBoxLayout()
        
        self.add_resource_button = QPushButton("Add Resource Type")
        self.add_resource_button.clicked.connect(self.add_resource_type)
        buttons_layout.addWidget(self.add_resource_button)
        
        self.remove_resource_button = QPushButton("Remove Selected")
        self.remove_resource_button.clicked.connect(self.remove_resource_type)
        buttons_layout.addWidget(self.remove_resource_button)
        
        buttons_layout.addStretch()
        
        # Info about slots per day
        info_label = QLabel("Slots per day: 4 (quarter-day slots, fixed)")
        info_label.setStyleSheet("font-weight: bold; color: #666;")
        buttons_layout.addWidget(info_label)
        
        table_layout.addLayout(buttons_layout)
        capacity_layout.addLayout(table_layout)
        
        parent_layout.addWidget(capacity_group)
    
    def setup_holidays_section(self, parent_layout):
        """Set up the public holidays section."""
        holidays_group = QGroupBox("Public Holidays")
        holidays_layout = QVBoxLayout(holidays_group)
        
        # Description
        desc_label = QLabel("Specify dates when no work can be scheduled (format: YYYY-MM-DD).")
        desc_label.setStyleSheet("color: gray;")
        holidays_layout.addWidget(desc_label)
        
        # Holidays list and controls
        list_layout = QHBoxLayout()
        
        # Holidays list
        self.holidays_list = QListWidget()
        self.holidays_list.setMaximumHeight(150)
        list_layout.addWidget(self.holidays_list)
        
        # Buttons for managing holidays
        buttons_layout = QVBoxLayout()
        
        self.add_holiday_button = QPushButton("Add Holiday")
        self.add_holiday_button.clicked.connect(self.add_holiday)
        buttons_layout.addWidget(self.add_holiday_button)
        
        self.remove_holiday_button = QPushButton("Remove Selected")
        self.remove_holiday_button.clicked.connect(self.remove_holiday)
        buttons_layout.addWidget(self.remove_holiday_button)
        
        buttons_layout.addStretch()
        list_layout.addLayout(buttons_layout)
        
        holidays_layout.addLayout(list_layout)
        parent_layout.addWidget(holidays_group)
    
    def setup_action_buttons(self, parent_layout):
        """Set up action buttons."""
        buttons_layout = QHBoxLayout()
        
        # Save button
        self.save_button = QPushButton("Save Resource Configuration")
        self.save_button.clicked.connect(self.save_resources)
        self.save_button.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        buttons_layout.addWidget(self.save_button)
        
        # Reset button
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        buttons_layout.addWidget(self.reset_button)
        
        buttons_layout.addStretch()
        parent_layout.addLayout(buttons_layout)
    
    def set_project(self, project: Project):
        """Set the current project."""
        self.current_project = project
        if project and project.current_resources:
            self.set_resources(project.current_resources)
        else:
            self.reset_to_defaults()
    
    def set_resources(self, resources: ResourceCapacity):
        """Set the resource configuration to display."""
        self.current_resources = resources
        
        # Update resources table
        self.populate_resources_table(resources.get_all_resources())
        
        # Update holidays list
        self.holidays_list.clear()
        for holiday in resources.public_holidays:
            item = QListWidgetItem(holiday)
            self.holidays_list.addItem(item)
    
    def populate_resources_table(self, resources_dict: Dict[str, int]):
        """Populate the resources table with resource data."""
        self.resources_table.setRowCount(len(resources_dict))
        
        for row, (resource_name, capacity) in enumerate(resources_dict.items()):
            # Resource name (editable)
            name_item = QTableWidgetItem(resource_name)
            self.resources_table.setItem(row, 0, name_item)
            
            # Capacity (editable)
            capacity_item = QTableWidgetItem(str(capacity))
            self.resources_table.setItem(row, 1, capacity_item)
    
    def get_current_resources(self) -> ResourceCapacity:
        """Get the current resource configuration from the UI."""
        # Get resources from table
        resources_dict = {}
        for row in range(self.resources_table.rowCount()):
            name_item = self.resources_table.item(row, 0)
            capacity_item = self.resources_table.item(row, 1)
            
            if name_item and capacity_item:
                resource_name = name_item.text().strip()
                try:
                    capacity = int(capacity_item.text())
                    if capacity < 0:
                        capacity = 0
                except ValueError:
                    capacity = 0
                
                if resource_name:  # Only add if name is not empty
                    resources_dict[resource_name] = capacity
        
        # Get holidays
        holidays = []
        for i in range(self.holidays_list.count()):
            item = self.holidays_list.item(i)
            holidays.append(item.text())
        
        # Create ResourceCapacity with the new format
        resource_capacity = ResourceCapacity(
            resources=resources_dict,
            slots_per_day=4,
            public_holidays=holidays
        )
        
        return resource_capacity
    
    def on_capacity_changed(self):
        """Handle changes to capacity values."""
        # Update current resources
        self.current_resources = self.get_current_resources()
        
        # Emit signal for immediate feedback
        self.resources_changed.emit(self.current_resources)
    
    def on_table_item_changed(self, item):
        """Handle changes to table items."""
        # Validate capacity values
        if item.column() == 1:  # Capacity column
            try:
                value = int(item.text())
                if value < 0:
                    item.setText("0")
            except ValueError:
                item.setText("0")
        
        # Update resources
        self.on_capacity_changed()
    
    def add_resource_type(self):
        """Add a new resource type."""
        resource_name, ok = QInputDialog.getText(
            self,
            "Add Resource Type",
            "Enter resource type name:",
            text="New Resource"
        )
        
        if not ok or not resource_name.strip():
            return
        
        resource_name = resource_name.strip()
        
        # Check for duplicates
        for row in range(self.resources_table.rowCount()):
            existing_name = self.resources_table.item(row, 0)
            if existing_name and existing_name.text() == resource_name:
                QMessageBox.information(
                    self,
                    "Duplicate Resource",
                    f"Resource type '{resource_name}' already exists."
                )
                return
        
        # Add new row
        row_count = self.resources_table.rowCount()
        self.resources_table.setRowCount(row_count + 1)
        
        # Set items
        name_item = QTableWidgetItem(resource_name)
        capacity_item = QTableWidgetItem("0")
        
        self.resources_table.setItem(row_count, 0, name_item)
        self.resources_table.setItem(row_count, 1, capacity_item)
        
        # Update resources
        self.on_capacity_changed()
    
    def remove_resource_type(self):
        """Remove the selected resource type."""
        current_row = self.resources_table.currentRow()
        if current_row < 0:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a resource type to remove."
            )
            return
        
        # Get resource name for confirmation
        name_item = self.resources_table.item(current_row, 0)
        resource_name = name_item.text() if name_item else "Unknown"
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Remove Resource Type",
            f"Are you sure you want to remove '{resource_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.resources_table.removeRow(current_row)
            self.on_capacity_changed()
    
    def add_holiday(self):
        """Add a new public holiday."""
        from PyQt6.QtWidgets import QInputDialog
        
        # Get date from user
        date_str, ok = QInputDialog.getText(
            self,
            "Add Public Holiday",
            "Enter date (YYYY-MM-DD):",
            text=QDate.currentDate().toString("yyyy-MM-dd")
        )
        
        if not ok or not date_str.strip():
            return
        
        date_str = date_str.strip()
        
        # Validate date format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Date",
                "Please enter a valid date in YYYY-MM-DD format."
            )
            return
        
        # Check for duplicates
        for i in range(self.holidays_list.count()):
            if self.holidays_list.item(i).text() == date_str:
                QMessageBox.information(
                    self,
                    "Duplicate Date",
                    "This date is already in the list."
                )
                return
        
        # Add to list
        item = QListWidgetItem(date_str)
        self.holidays_list.addItem(item)
        
        # Sort the list
        self.holidays_list.sortItems()
        
        # Update resources
        self.on_holidays_changed()
    
    def remove_holiday(self):
        """Remove the selected public holiday."""
        current_item = self.holidays_list.currentItem()
        if not current_item:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a holiday to remove."
            )
            return
        
        # Remove item
        row = self.holidays_list.row(current_item)
        self.holidays_list.takeItem(row)
        
        # Update resources
        self.on_holidays_changed()
    
    def on_holidays_changed(self):
        """Handle changes to the holidays list."""
        # Update current resources
        self.current_resources = self.get_current_resources()
        
        # Emit signal
        self.resources_changed.emit(self.current_resources)
    
    def save_resources(self):
        """Save the current resource configuration."""
        if not self.current_project:
            QMessageBox.information(
                self,
                "No Project",
                "Please select a project first."
            )
            return
        
        # Get current configuration
        resources = self.get_current_resources()
        
        # Update project
        self.current_project.current_resources = resources
        self.current_resources = resources
        
        # Emit signal
        self.resources_changed.emit(resources)
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Resources Saved",
            "Resource configuration has been saved to the project."
        )
    
    def reset_to_defaults(self):
        """Reset to default resource configuration."""
        default_resources = ResourceCapacity()
        self.set_resources(default_resources)
        self.on_capacity_changed()
