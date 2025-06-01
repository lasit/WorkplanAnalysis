"""Plan tab for displaying workplan activities."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QLabel,
    QHeaderView, QPushButton, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt6.QtGui import QFont
from typing import List, Optional, Any

from core.models import Project, Activity
from core.data_loader import DataLoader


class ActivityTableModel(QAbstractTableModel):
    """Table model for displaying activity data."""
    
    def __init__(self):
        super().__init__()
        self.activities: List[Activity] = []
        self.headers = [
            "Activity ID", "Activity Name", "Quarter", "Frequency", 
            "Duration", "Ranger Coordinator", "Senior Ranger", "Ranger"
        ]
    
    def set_activities(self, activities: List[Activity]):
        """Set the activities to display."""
        self.beginResetModel()
        self.activities = activities
        self.endResetModel()
    
    def rowCount(self, parent=QModelIndex()):
        """Return number of rows."""
        return len(self.activities)
    
    def columnCount(self, parent=QModelIndex()):
        """Return number of columns."""
        return len(self.headers)
    
    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        """Return data for the given index and role."""
        if not index.isValid() or index.row() >= len(self.activities):
            return QVariant()
        
        activity = self.activities[index.row()]
        column = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return activity.activity_id
            elif column == 1:
                return activity.name
            elif column == 2:
                return activity.quarter
            elif column == 3:
                return str(activity.frequency)
            elif column == 4:
                return str(activity.duration)
            elif column == 5:
                return str(activity.ranger_coordinator)
            elif column == 6:
                return str(activity.senior_ranger)
            elif column == 7:
                return str(activity.ranger)
        
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if column >= 3:  # Numeric columns
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        
        elif role == Qt.ItemDataRole.ToolTipRole:
            tooltip = f"Activity: {activity.name}\n"
            tooltip += f"ID: {activity.activity_id}\n"
            tooltip += f"Quarter: {activity.quarter}\n"
            tooltip += f"Frequency: {activity.frequency} times\n"
            tooltip += f"Duration: {activity.duration} days\n"
            tooltip += f"Resources needed:\n"
            tooltip += f"  Ranger Coordinator: {activity.ranger_coordinator}\n"
            tooltip += f"  Senior Ranger: {activity.senior_ranger}\n"
            tooltip += f"  Ranger: {activity.ranger}"
            return tooltip
        
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Return header data."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return QVariant()


class PlanTab(QWidget):
    """Tab for displaying and managing workplan data."""
    
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
        
        # Activities table
        self.setup_activities_table(layout)
    
    def setup_summary_section(self, parent_layout):
        """Set up the summary information section."""
        summary_group = QGroupBox("Workplan Summary")
        summary_layout = QGridLayout(summary_group)
        
        # Create summary labels
        self.total_activities_label = QLabel("0")
        self.total_occurrences_label = QLabel("0")
        self.quarter_label = QLabel("-")
        
        # Resource demand labels
        self.rc_demand_label = QLabel("0")
        self.sr_demand_label = QLabel("0")
        self.ranger_demand_label = QLabel("0")
        
        # Duration breakdown labels
        self.quarter_day_label = QLabel("0")
        self.half_day_label = QLabel("0")
        self.full_day_label = QLabel("0")
        
        # Make value labels bold
        font = QFont()
        font.setBold(True)
        for label in [self.total_activities_label, self.total_occurrences_label, 
                     self.quarter_label, self.rc_demand_label, self.sr_demand_label,
                     self.ranger_demand_label, self.quarter_day_label, 
                     self.half_day_label, self.full_day_label]:
            label.setFont(font)
        
        # Layout summary information
        row = 0
        summary_layout.addWidget(QLabel("Total Activities:"), row, 0)
        summary_layout.addWidget(self.total_activities_label, row, 1)
        summary_layout.addWidget(QLabel("Total Occurrences:"), row, 2)
        summary_layout.addWidget(self.total_occurrences_label, row, 3)
        summary_layout.addWidget(QLabel("Quarter:"), row, 4)
        summary_layout.addWidget(self.quarter_label, row, 5)
        
        row += 1
        summary_layout.addWidget(QLabel("Resource Demand:"), row, 0, 1, 6)
        
        row += 1
        summary_layout.addWidget(QLabel("  Ranger Coordinator:"), row, 0)
        summary_layout.addWidget(self.rc_demand_label, row, 1)
        summary_layout.addWidget(QLabel("  Senior Ranger:"), row, 2)
        summary_layout.addWidget(self.sr_demand_label, row, 3)
        summary_layout.addWidget(QLabel("  Ranger:"), row, 4)
        summary_layout.addWidget(self.ranger_demand_label, row, 5)
        
        row += 1
        summary_layout.addWidget(QLabel("Duration Breakdown:"), row, 0, 1, 6)
        
        row += 1
        summary_layout.addWidget(QLabel("  Quarter-day (0.25):"), row, 0)
        summary_layout.addWidget(self.quarter_day_label, row, 1)
        summary_layout.addWidget(QLabel("  Half-day (0.5):"), row, 2)
        summary_layout.addWidget(self.half_day_label, row, 3)
        summary_layout.addWidget(QLabel("  Full-day (1.0):"), row, 4)
        summary_layout.addWidget(self.full_day_label, row, 5)
        
        parent_layout.addWidget(summary_group)
    
    def setup_activities_table(self, parent_layout):
        """Set up the activities table."""
        # Table section
        table_group = QGroupBox("Activities")
        table_layout = QVBoxLayout(table_group)
        
        # Create table view and model
        self.table_view = QTableView()
        self.table_model = ActivityTableModel()
        self.table_view.setModel(self.table_model)
        
        # Configure table appearance
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSortingEnabled(True)
        
        # Configure headers
        header = self.table_view.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Activity Name column
        
        # Set minimum column widths
        self.table_view.setColumnWidth(0, 80)   # Activity ID
        self.table_view.setColumnWidth(2, 80)   # Quarter
        self.table_view.setColumnWidth(3, 80)   # Frequency
        self.table_view.setColumnWidth(4, 80)   # Duration
        self.table_view.setColumnWidth(5, 120)  # Ranger Coordinator
        self.table_view.setColumnWidth(6, 100)  # Senior Ranger
        self.table_view.setColumnWidth(7, 80)   # Ranger
        
        table_layout.addWidget(self.table_view)
        parent_layout.addWidget(table_group)
    
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
        self.table_model.set_activities(self.current_project.activities)
        
        # Update summary
        self.update_summary()
    
    def update_summary(self):
        """Update the summary section."""
        if not self.current_project or not self.current_project.activities:
            self.clear_summary()
            return
        
        summary = DataLoader.get_workplan_summary(self.current_project.activities)
        
        # Basic counts
        self.total_activities_label.setText(str(summary.get('total_activities', 0)))
        self.total_occurrences_label.setText(str(summary.get('total_occurrences', 0)))
        
        # Quarter information
        quarters = summary.get('quarters', [])
        quarter_text = ', '.join(quarters) if quarters else '-'
        self.quarter_label.setText(quarter_text)
        
        # Resource demands
        total_demand = summary.get('total_demand', {})
        self.rc_demand_label.setText(str(total_demand.get('RangerCoordinator', 0)))
        self.sr_demand_label.setText(str(total_demand.get('SeniorRanger', 0)))
        self.ranger_demand_label.setText(str(total_demand.get('Ranger', 0)))
        
        # Duration breakdown
        duration_breakdown = summary.get('duration_breakdown', {})
        self.quarter_day_label.setText(str(duration_breakdown.get(0.25, 0)))
        self.half_day_label.setText(str(duration_breakdown.get(0.5, 0)))
        self.full_day_label.setText(str(duration_breakdown.get(1.0, 0)))
    
    def clear_display(self):
        """Clear the display."""
        self.table_model.set_activities([])
        self.clear_summary()
    
    def clear_summary(self):
        """Clear the summary section."""
        self.total_activities_label.setText("0")
        self.total_occurrences_label.setText("0")
        self.quarter_label.setText("-")
        self.rc_demand_label.setText("0")
        self.sr_demand_label.setText("0")
        self.ranger_demand_label.setText("0")
        self.quarter_day_label.setText("0")
        self.half_day_label.setText("0")
        self.full_day_label.setText("0")
