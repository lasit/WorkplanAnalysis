"""Resources tab for editing resource capacity configuration."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QSpinBox, QGroupBox, QListWidget, QListWidgetItem,
    QMessageBox, QDateEdit, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from typing import Optional, List
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
        """Set up the resource capacity editing section."""
        capacity_group = QGroupBox("Resource Capacity")
        capacity_layout = QGridLayout(capacity_group)
        
        # Title and description
        title_label = QLabel("Staff Available per Time Slot")
        title_font = QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)
        capacity_layout.addWidget(title_label, 0, 0, 1, 3)
        
        desc_label = QLabel("Configure how many staff of each role are available simultaneously.")
        desc_label.setStyleSheet("color: gray;")
        capacity_layout.addWidget(desc_label, 1, 0, 1, 3)
        
        # Add some spacing
        capacity_layout.addWidget(QFrame(), 2, 0, 1, 3)
        
        # Resource capacity controls
        row = 3
        
        # Ranger Coordinator
        capacity_layout.addWidget(QLabel("Ranger Coordinator:"), row, 0)
        self.rc_spinbox = QSpinBox()
        self.rc_spinbox.setRange(0, 10)
        self.rc_spinbox.setValue(1)
        self.rc_spinbox.valueChanged.connect(self.on_capacity_changed)
        capacity_layout.addWidget(self.rc_spinbox, row, 1)
        capacity_layout.addWidget(QLabel("staff"), row, 2)
        
        row += 1
        
        # Senior Ranger
        capacity_layout.addWidget(QLabel("Senior Ranger:"), row, 0)
        self.sr_spinbox = QSpinBox()
        self.sr_spinbox.setRange(0, 20)
        self.sr_spinbox.setValue(2)
        self.sr_spinbox.valueChanged.connect(self.on_capacity_changed)
        capacity_layout.addWidget(self.sr_spinbox, row, 1)
        capacity_layout.addWidget(QLabel("staff"), row, 2)
        
        row += 1
        
        # Ranger
        capacity_layout.addWidget(QLabel("Ranger:"), row, 0)
        self.ranger_spinbox = QSpinBox()
        self.ranger_spinbox.setRange(0, 50)
        self.ranger_spinbox.setValue(5)
        self.ranger_spinbox.valueChanged.connect(self.on_capacity_changed)
        capacity_layout.addWidget(self.ranger_spinbox, row, 1)
        capacity_layout.addWidget(QLabel("staff"), row, 2)
        
        row += 1
        
        # Slots per day (read-only)
        capacity_layout.addWidget(QLabel("Slots per day:"), row, 0)
        self.slots_label = QLabel("4")
        self.slots_label.setStyleSheet("font-weight: bold;")
        capacity_layout.addWidget(self.slots_label, row, 1)
        capacity_layout.addWidget(QLabel("(quarter-day slots, fixed)"), row, 2)
        
        # Set column stretches
        capacity_layout.setColumnStretch(0, 1)
        capacity_layout.setColumnStretch(1, 0)
        capacity_layout.setColumnStretch(2, 1)
        
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
        
        # Update capacity controls
        self.rc_spinbox.setValue(resources.ranger_coordinator)
        self.sr_spinbox.setValue(resources.senior_ranger)
        self.ranger_spinbox.setValue(resources.ranger)
        
        # Update holidays list
        self.holidays_list.clear()
        for holiday in resources.public_holidays:
            item = QListWidgetItem(holiday)
            self.holidays_list.addItem(item)
    
    def get_current_resources(self) -> ResourceCapacity:
        """Get the current resource configuration from the UI."""
        holidays = []
        for i in range(self.holidays_list.count()):
            item = self.holidays_list.item(i)
            holidays.append(item.text())
        
        return ResourceCapacity(
            ranger_coordinator=self.rc_spinbox.value(),
            senior_ranger=self.sr_spinbox.value(),
            ranger=self.ranger_spinbox.value(),
            slots_per_day=4,  # Fixed value
            public_holidays=holidays
        )
    
    def on_capacity_changed(self):
        """Handle changes to capacity values."""
        # Update current resources
        self.current_resources = self.get_current_resources()
        
        # Emit signal for immediate feedback
        self.resources_changed.emit(self.current_resources)
    
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
