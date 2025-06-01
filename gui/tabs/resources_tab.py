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
        """Set up the public holidays section with auto-detected and custom holidays."""
        holidays_group = QGroupBox("Public Holidays")
        holidays_layout = QVBoxLayout(holidays_group)
        
        # Quarter info and description
        self.quarter_info_label = QLabel("Holidays for planning period")
        quarter_font = QFont()
        quarter_font.setBold(True)
        self.quarter_info_label.setFont(quarter_font)
        holidays_layout.addWidget(self.quarter_info_label)
        
        # Working days summary
        self.working_days_label = QLabel("Working days calculation will be shown here")
        self.working_days_label.setStyleSheet("color: #666; font-style: italic;")
        holidays_layout.addWidget(self.working_days_label)
        
        # Auto-detected NT holidays section
        auto_holidays_group = QGroupBox("✓ Auto-detected NT Holidays")
        auto_holidays_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #2E7D32;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        auto_holidays_layout = QVBoxLayout(auto_holidays_group)
        
        # Auto holidays list (read-only)
        self.auto_holidays_list = QListWidget()
        self.auto_holidays_list.setMaximumHeight(120)
        self.auto_holidays_list.setStyleSheet("""
            QListWidget {
                background-color: #F1F8E9;
                border: 1px solid #C8E6C9;
                border-radius: 3px;
                color: #2E7D32;
                font-weight: bold;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #E8F5E8;
                color: #1B5E20;
            }
        """)
        # Make it read-only
        self.auto_holidays_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        auto_holidays_layout.addWidget(self.auto_holidays_list)
        
        holidays_layout.addWidget(auto_holidays_group)
        
        # Custom organization holidays section
        custom_holidays_group = QGroupBox("⚙ Additional Organization Holidays")
        custom_holidays_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #1976D2;
                border: 2px solid #2196F3;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        custom_holidays_layout = QVBoxLayout(custom_holidays_group)
        
        # Custom holidays list and controls
        custom_list_layout = QHBoxLayout()
        
        # Custom holidays list (editable)
        self.custom_holidays_list = QListWidget()
        self.custom_holidays_list.setMaximumHeight(100)
        self.custom_holidays_list.setStyleSheet("""
            QListWidget {
                background-color: #E3F2FD;
                border: 1px solid #BBDEFB;
                border-radius: 3px;
                color: #1976D2;
                font-weight: bold;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #E1F5FE;
                color: #0D47A1;
            }
        """)
        custom_list_layout.addWidget(self.custom_holidays_list)
        
        # Buttons for managing custom holidays
        custom_buttons_layout = QVBoxLayout()
        
        self.add_custom_holiday_button = QPushButton("Add Holiday")
        self.add_custom_holiday_button.clicked.connect(self.add_custom_holiday)
        self.add_custom_holiday_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        custom_buttons_layout.addWidget(self.add_custom_holiday_button)
        
        self.remove_custom_holiday_button = QPushButton("Remove Selected")
        self.remove_custom_holiday_button.clicked.connect(self.remove_custom_holiday)
        custom_buttons_layout.addWidget(self.remove_custom_holiday_button)
        
        custom_buttons_layout.addStretch()
        custom_list_layout.addLayout(custom_buttons_layout)
        
        custom_holidays_layout.addLayout(custom_list_layout)
        holidays_layout.addWidget(custom_holidays_group)
        
        # Holiday summary
        self.holiday_summary_label = QLabel("Total holidays: 0")
        summary_font = QFont()
        summary_font.setBold(True)
        self.holiday_summary_label.setFont(summary_font)
        self.holiday_summary_label.setStyleSheet("color: #333; padding: 10px; background-color: #F5F5F5; border-radius: 3px;")
        holidays_layout.addWidget(self.holiday_summary_label)
        
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
        
        # Update holiday displays
        self.update_holiday_displays()
    
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
    
    def update_holiday_displays(self):
        """Update the holiday displays with auto-detected and custom holidays."""
        if not self.current_project:
            self.quarter_info_label.setText("No project selected")
            self.working_days_label.setText("")
            self.auto_holidays_list.clear()
            self.custom_holidays_list.clear()
            self.holiday_summary_label.setText("Total holidays: 0")
            return
        
        # Update quarter info
        if self.current_project.planning_quarter:
            quarter_info = self.current_project.get_quarter_info()
            if quarter_info and not quarter_info.get('error'):
                quarter_text = f"Holidays for {quarter_info['quarter']} ({quarter_info['start_date']} to {quarter_info['end_date']})"
                self.quarter_info_label.setText(quarter_text)
                
                working_days_text = f"{quarter_info['working_days']} working days ({quarter_info['total_days']} total - weekends - holidays)"
                self.working_days_label.setText(working_days_text)
            else:
                self.quarter_info_label.setText(f"Holidays for {self.current_project.planning_quarter}")
                self.working_days_label.setText("Working days calculation unavailable")
        else:
            self.quarter_info_label.setText("No planning quarter set")
            self.working_days_label.setText("")
        
        # Update auto-detected holidays
        self.auto_holidays_list.clear()
        auto_holidays = self.current_project.get_auto_holidays_for_quarter()
        if auto_holidays:
            for date_str, holiday_name in auto_holidays:
                item_text = f"{date_str}  {holiday_name}"
                item = QListWidgetItem(item_text)
                item.setToolTip(f"{holiday_name} - Auto-detected NT public holiday")
                self.auto_holidays_list.addItem(item)
        else:
            item = QListWidgetItem("No NT public holidays in this period")
            item.setToolTip("No Northern Territory public holidays fall within the planning quarter")
            self.auto_holidays_list.addItem(item)
        
        # Update custom holidays
        self.custom_holidays_list.clear()
        if self.current_resources and self.current_resources.custom_holidays:
            for holiday_date in self.current_resources.custom_holidays:
                item = QListWidgetItem(holiday_date)
                item.setToolTip("Organization-specific holiday")
                self.custom_holidays_list.addItem(item)
        
        # Update holiday summary
        auto_count = len(auto_holidays)
        custom_count = len(self.current_resources.custom_holidays) if self.current_resources and self.current_resources.custom_holidays else 0
        legacy_count = len(self.current_resources.public_holidays) if self.current_resources and self.current_resources.public_holidays else 0
        
        total_holidays = auto_count + custom_count + legacy_count
        summary_text = f"Total holidays: {total_holidays} ({auto_count} NT + {custom_count} custom"
        if legacy_count > 0:
            summary_text += f" + {legacy_count} legacy"
        summary_text += ")"
        
        self.holiday_summary_label.setText(summary_text)
    
    def add_custom_holiday(self):
        """Add a new custom organization holiday."""
        from PyQt6.QtWidgets import QCalendarWidget, QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QLabel
        
        # Create calendar dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Organization Holiday")
        dialog.setModal(True)
        dialog.resize(400, 350)
        
        layout = QVBoxLayout(dialog)
        
        # Add instruction label
        instruction_label = QLabel("Select a date for the organization holiday:")
        layout.addWidget(instruction_label)
        
        # Create calendar widget
        calendar = QCalendarWidget()
        calendar.setSelectedDate(QDate.currentDate())
        
        # Set calendar to show only the planning quarter if available
        if self.current_project and self.current_project.planning_quarter:
            try:
                start_date, end_date = self.current_project.parse_financial_quarter(self.current_project.planning_quarter)
                calendar.setMinimumDate(QDate(start_date.year, start_date.month, start_date.day))
                calendar.setMaximumDate(QDate(end_date.year, end_date.month, end_date.day))
            except Exception:
                pass  # If parsing fails, allow any date
        
        layout.addWidget(calendar)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("Add Holiday")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        ok_button.clicked.connect(dialog.accept)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
        # Show dialog and get result
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        # Get selected date
        selected_date = calendar.selectedDate()
        date_str = selected_date.toString("yyyy-MM-dd")
        
        # Check if it's already an auto-detected holiday
        auto_holidays = self.current_project.get_auto_holidays_for_quarter() if self.current_project else []
        auto_dates = [date for date, _ in auto_holidays]
        if date_str in auto_dates:
            QMessageBox.information(
                self,
                "Already a Public Holiday",
                f"This date ({date_str}) is already an auto-detected NT public holiday."
            )
            return
        
        # Check for duplicates in custom holidays
        if self.current_resources and self.current_resources.custom_holidays:
            if date_str in self.current_resources.custom_holidays:
                QMessageBox.information(
                    self,
                    "Duplicate Date",
                    "This date is already in the custom holidays list."
                )
                return
        
        # Add to custom holidays
        if not self.current_resources:
            self.current_resources = ResourceCapacity()
        
        if not self.current_resources.custom_holidays:
            self.current_resources.custom_holidays = []
        
        self.current_resources.custom_holidays.append(date_str)
        self.current_resources.custom_holidays.sort()
        
        # Update display and emit signal
        self.update_holiday_displays()
        self.resources_changed.emit(self.current_resources)
    
    def remove_custom_holiday(self):
        """Remove the selected custom holiday."""
        current_item = self.custom_holidays_list.currentItem()
        if not current_item:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a custom holiday to remove."
            )
            return
        
        date_str = current_item.text()
        
        # Remove from custom holidays
        if self.current_resources and self.current_resources.custom_holidays:
            if date_str in self.current_resources.custom_holidays:
                self.current_resources.custom_holidays.remove(date_str)
        
        # Update display and emit signal
        self.update_holiday_displays()
        self.resources_changed.emit(self.current_resources)
    
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
        
        # Get custom holidays from the current resources (preserve them)
        custom_holidays = []
        if self.current_resources and self.current_resources.custom_holidays:
            custom_holidays = self.current_resources.custom_holidays.copy()
        
        # Get legacy holidays for backward compatibility
        public_holidays = []
        if self.current_resources and self.current_resources.public_holidays:
            public_holidays = self.current_resources.public_holidays.copy()
        
        # Create ResourceCapacity with the new format
        resource_capacity = ResourceCapacity(
            resources=resources_dict,
            slots_per_day=4,
            public_holidays=public_holidays,  # Legacy field
            custom_holidays=custom_holidays   # New field
        )
        
        return resource_capacity
    
    def reset_to_defaults(self):
        """Reset to default resource configuration."""
        default_resources = ResourceCapacity()
        self.set_resources(default_resources)
        self.on_capacity_changed()
