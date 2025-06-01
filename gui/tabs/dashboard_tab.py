"""Dashboard tab for displaying analysis results."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QTableView, QStackedWidget, QProgressBar, QFrame,
    QGridLayout, QScrollArea, QPushButton
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, pyqtSignal
from PyQt6.QtGui import QFont, QPalette
from typing import Optional, List, Dict, Any

from core.models import Project, AnalysisResult


class UtilizationTableModel(QAbstractTableModel):
    """Table model for displaying utilization data."""
    
    def __init__(self):
        super().__init__()
        self.data_items: List[tuple] = []  # (role, utilization, capacity)
        self.headers = ["Role", "Utilization (%)", "Status"]
    
    def set_data(self, utilization: Dict[str, float], capacity_data: Optional[Dict[str, int]] = None):
        """Set utilization data to display."""
        self.beginResetModel()
        self.data_items = []
        
        for role, util in utilization.items():
            capacity = capacity_data.get(role, 0) if capacity_data else 0
            self.data_items.append((role, util, capacity))
        
        self.endResetModel()
    
    def rowCount(self, parent=QModelIndex()):
        """Return number of rows."""
        return len(self.data_items)
    
    def columnCount(self, parent=QModelIndex()):
        """Return number of columns."""
        return len(self.headers)
    
    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        """Return data for the given index and role."""
        if not index.isValid() or index.row() >= len(self.data_items):
            return QVariant()
        
        role_name, utilization, capacity = self.data_items[index.row()]
        column = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return role_name
            elif column == 1:
                return f"{utilization:.1f}%"
            elif column == 2:
                if utilization > 100:
                    return "Overloaded"
                elif utilization > 90:
                    return "High"
                elif utilization > 70:
                    return "Moderate"
                else:
                    return "Low"
        
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if column == 1:  # Utilization column
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        
        elif role == Qt.ItemDataRole.BackgroundRole:
            if column == 2:  # Status column
                if utilization > 100:
                    return QPalette().color(QPalette.ColorRole.Base).lighter(120)  # Light red
                elif utilization > 90:
                    return QPalette().color(QPalette.ColorRole.Base).lighter(110)  # Light orange
        
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Return header data."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return QVariant()


class OverloadTableModel(QAbstractTableModel):
    """Table model for displaying overload information."""
    
    def __init__(self):
        super().__init__()
        self.overloads: List[Dict[str, Any]] = []
        self.headers = ["Date", "Time Slot", "Role", "Extra Needed"]
    
    def set_overloads(self, overloads: List[Dict[str, Any]]):
        """Set overload data to display."""
        self.beginResetModel()
        self.overloads = overloads
        self.endResetModel()
    
    def rowCount(self, parent=QModelIndex()):
        """Return number of rows."""
        return len(self.overloads)
    
    def columnCount(self, parent=QModelIndex()):
        """Return number of columns."""
        return len(self.headers)
    
    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        """Return data for the given index and role."""
        if not index.isValid() or index.row() >= len(self.overloads):
            return QVariant()
        
        overload = self.overloads[index.row()]
        column = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return overload.get("date", "")
            elif column == 1:
                return overload.get("slot", "")
            elif column == 2:
                return overload.get("role", "")
            elif column == 3:
                return str(overload.get("extra_needed", 0))
        
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if column == 3:  # Extra needed column
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Return header data."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return QVariant()


class DashboardTab(QWidget):
    """Tab for displaying analysis results and dashboard."""
    
    # Signals
    analysis_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_project: Optional[Project] = None
        self.current_analysis: Optional[AnalysisResult] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create stacked widget for different states
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Create pages
        self.setup_waiting_page()
        self.setup_results_page()
        
        # Start with waiting page
        self.stacked_widget.setCurrentIndex(0)
    
    def setup_waiting_page(self):
        """Set up the waiting/no results page."""
        waiting_widget = QWidget()
        waiting_layout = QVBoxLayout(waiting_widget)
        waiting_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon or placeholder
        waiting_label = QLabel("No Analysis Results")
        waiting_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        waiting_label.setFont(font)
        waiting_label.setStyleSheet("color: gray;")
        waiting_layout.addWidget(waiting_label)
        
        instruction_label = QLabel("Run an analysis (F5) to see results here.")
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setStyleSheet("color: gray;")
        waiting_layout.addWidget(instruction_label)
        
        # Add Run Analysis button
        self.run_analysis_button = QPushButton("Run Analysis (F5)")
        self.run_analysis_button.setMinimumWidth(150)
        self.run_analysis_button.clicked.connect(self.analysis_requested.emit)
        waiting_layout.addWidget(self.run_analysis_button)
        
        self.stacked_widget.addWidget(waiting_widget)
    
    def setup_results_page(self):
        """Set up the results display page."""
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Create scroll area for results
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Verdict section
        self.setup_verdict_section(scroll_layout)
        
        # Utilization section
        self.setup_utilization_section(scroll_layout)
        
        # Overload section (shown only if infeasible)
        self.setup_overload_section(scroll_layout)
        
        # Analysis info section
        self.setup_analysis_info_section(scroll_layout)
        
        scroll_area.setWidget(scroll_content)
        results_layout.addWidget(scroll_area)
        
        self.stacked_widget.addWidget(results_widget)
    
    def setup_verdict_section(self, parent_layout):
        """Set up the verdict display section."""
        verdict_group = QGroupBox("Analysis Verdict")
        verdict_layout = QVBoxLayout(verdict_group)
        
        # Verdict label
        self.verdict_label = QLabel("Unknown")
        self.verdict_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        verdict_font = QFont()
        verdict_font.setPointSize(24)
        verdict_font.setBold(True)
        self.verdict_label.setFont(verdict_font)
        verdict_layout.addWidget(self.verdict_label)
        
        # Timestamp label
        self.timestamp_label = QLabel("")
        self.timestamp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timestamp_label.setStyleSheet("color: gray;")
        verdict_layout.addWidget(self.timestamp_label)
        
        parent_layout.addWidget(verdict_group)
    
    def setup_utilization_section(self, parent_layout):
        """Set up the utilization display section."""
        utilization_group = QGroupBox("Resource Utilization")
        utilization_layout = QVBoxLayout(utilization_group)
        
        # Utilization table
        self.utilization_table = QTableView()
        self.utilization_model = UtilizationTableModel()
        self.utilization_table.setModel(self.utilization_model)
        
        # Configure table
        self.utilization_table.setAlternatingRowColors(True)
        self.utilization_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.utilization_table.horizontalHeader().setStretchLastSection(True)
        self.utilization_table.setMaximumHeight(150)
        
        utilization_layout.addWidget(self.utilization_table)
        parent_layout.addWidget(utilization_group)
    
    def setup_overload_section(self, parent_layout):
        """Set up the overload information section."""
        self.overload_group = QGroupBox("Capacity Overloads")
        overload_layout = QVBoxLayout(self.overload_group)
        
        # Overload description
        self.overload_description = QLabel("")
        self.overload_description.setWordWrap(True)
        overload_layout.addWidget(self.overload_description)
        
        # Overload table
        self.overload_table = QTableView()
        self.overload_model = OverloadTableModel()
        self.overload_table.setModel(self.overload_model)
        
        # Configure table
        self.overload_table.setAlternatingRowColors(True)
        self.overload_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.overload_table.horizontalHeader().setStretchLastSection(True)
        self.overload_table.setMaximumHeight(200)
        
        overload_layout.addWidget(self.overload_table)
        
        # Initially hidden
        self.overload_group.setVisible(False)
        parent_layout.addWidget(self.overload_group)
    
    def setup_analysis_info_section(self, parent_layout):
        """Set up the analysis information section."""
        info_group = QGroupBox("Analysis Information")
        info_layout = QGridLayout(info_group)
        
        # Solver statistics
        info_layout.addWidget(QLabel("Solver Status:"), 0, 0)
        self.solver_status_label = QLabel("-")
        info_layout.addWidget(self.solver_status_label, 0, 1)
        
        info_layout.addWidget(QLabel("Solve Time:"), 1, 0)
        self.solve_time_label = QLabel("-")
        info_layout.addWidget(self.solve_time_label, 1, 1)
        
        info_layout.addWidget(QLabel("Variables:"), 0, 2)
        self.variables_label = QLabel("-")
        info_layout.addWidget(self.variables_label, 0, 3)
        
        info_layout.addWidget(QLabel("Constraints:"), 1, 2)
        self.constraints_label = QLabel("-")
        info_layout.addWidget(self.constraints_label, 1, 3)
        
        parent_layout.addWidget(info_group)
    
    def set_project(self, project: Project):
        """Set the current project."""
        self.current_project = project
        
        # Show latest analysis if available
        if project:
            latest_analysis = project.get_latest_analysis()
            if latest_analysis:
                self.show_analysis(latest_analysis)
            else:
                self.show_waiting()
        else:
            self.show_waiting()
    
    def show_analysis(self, analysis: AnalysisResult):
        """Display an analysis result."""
        self.current_analysis = analysis
        
        # Update verdict
        if analysis.feasible:
            self.verdict_label.setText("✅ FEASIBLE")
            self.verdict_label.setStyleSheet("color: green;")
        else:
            self.verdict_label.setText("❌ INFEASIBLE")
            self.verdict_label.setStyleSheet("color: red;")
        
        # Update timestamp
        timestamp_str = analysis.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.setText(f"Analysis completed: {timestamp_str}")
        
        # Update utilization table
        capacity_data = None
        if analysis.resource_capacity:
            # Get all resource types dynamically
            capacity_data = analysis.resource_capacity.get_all_resources()
        
        self.utilization_model.set_data(analysis.utilization, capacity_data)
        
        # Update overload section
        if not analysis.feasible and analysis.overloads:
            self.overload_group.setVisible(True)
            self.overload_model.set_overloads(analysis.overloads)
            
            # Update description
            total_overloads = len(analysis.overloads)
            affected_roles = set(o.get("role", "") for o in analysis.overloads)
            self.overload_description.setText(
                f"Found {total_overloads} capacity overload(s) affecting roles: {', '.join(affected_roles)}"
            )
        else:
            self.overload_group.setVisible(False)
        
        # Update analysis info
        solver_stats = analysis.solver_stats
        self.solver_status_label.setText(solver_stats.get("status", "Unknown"))
        
        solve_time = solver_stats.get("solve_time", 0)
        if solve_time > 0:
            self.solve_time_label.setText(f"{solve_time:.3f} seconds")
        else:
            self.solve_time_label.setText("-")
        
        self.variables_label.setText(str(solver_stats.get("num_variables", "-")))
        self.constraints_label.setText(str(solver_stats.get("num_constraints", "-")))
        
        # Switch to results page
        self.stacked_widget.setCurrentIndex(1)
    
    def show_waiting(self):
        """Show the waiting page."""
        self.current_analysis = None
        self.stacked_widget.setCurrentIndex(0)
    
    def clear_results(self):
        """Clear all results and show waiting page."""
        self.show_waiting()
