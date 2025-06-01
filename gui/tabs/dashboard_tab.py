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


class UtilisationTableModel(QAbstractTableModel):
    """Table model for displaying utilisation data."""
    
    def __init__(self):
        super().__init__()
        self.data_items: List[tuple] = []  # (role, utilisation, capacity)
        self.headers = ["Role", "Utilisation (%)", "Status"]
    
    def set_data(self, utilisation: Dict[str, float], capacity_data: Optional[Dict[str, int]] = None):
        """Set utilisation data to display."""
        self.beginResetModel()
        self.data_items = []
        
        for role, util in utilisation.items():
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
        
        role_name, utilisation, capacity = self.data_items[index.row()]
        column = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return role_name
            elif column == 1:
                return f"{utilisation:.1f}%"
            elif column == 2:
                if utilisation > 100:
                    return "Overloaded"
                elif utilisation > 90:
                    return "High"
                elif utilisation > 70:
                    return "Moderate"
                else:
                    return "Low"
        
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if column == 1:  # Utilisation column
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        
        elif role == Qt.ItemDataRole.BackgroundRole:
            if column == 2:  # Status column
                if utilisation > 100:
                    return QPalette().color(QPalette.ColorRole.Base).lighter(120)  # Light red
                elif utilisation > 90:
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
        
        # Utilisation section
        self.setup_utilisation_section(scroll_layout)
        
        # Overload section (shown only if infeasible)
        self.setup_overload_section(scroll_layout)
        
        # Enhanced infeasibility diagnostics section
        self.setup_diagnostics_section(scroll_layout)
        
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
    
    def setup_utilisation_section(self, parent_layout):
        """Set up the utilisation display section."""
        utilisation_group = QGroupBox("Resource Utilisation")
        utilisation_layout = QVBoxLayout(utilisation_group)
        
        # Utilisation table
        self.utilisation_table = QTableView()
        self.utilisation_model = UtilisationTableModel()
        self.utilisation_table.setModel(self.utilisation_model)
        
        # Configure table
        self.utilisation_table.setAlternatingRowColors(True)
        self.utilisation_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.utilisation_table.horizontalHeader().setStretchLastSection(True)
        self.utilisation_table.setMaximumHeight(150)
        
        utilisation_layout.addWidget(self.utilisation_table)
        parent_layout.addWidget(utilisation_group)
    
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
    
    def setup_diagnostics_section(self, parent_layout):
        """Set up the enhanced infeasibility diagnostics section."""
        self.diagnostics_group = QGroupBox("Infeasibility Analysis")
        diagnostics_layout = QVBoxLayout(self.diagnostics_group)
        
        # Primary reason and severity
        self.primary_reason_label = QLabel("")
        self.primary_reason_label.setWordWrap(True)
        primary_font = QFont()
        primary_font.setBold(True)
        primary_font.setPointSize(12)
        self.primary_reason_label.setFont(primary_font)
        diagnostics_layout.addWidget(self.primary_reason_label)
        
        # Recommendations section
        recommendations_label = QLabel("Recommendations:")
        recommendations_font = QFont()
        recommendations_font.setBold(True)
        recommendations_label.setFont(recommendations_font)
        diagnostics_layout.addWidget(recommendations_label)
        
        self.recommendations_label = QLabel("")
        self.recommendations_label.setWordWrap(True)
        self.recommendations_label.setStyleSheet("margin-left: 10px; color: #2E7D32;")
        diagnostics_layout.addWidget(self.recommendations_label)
        
        # Detailed issues section
        issues_label = QLabel("Detailed Issues:")
        issues_label.setFont(recommendations_font)
        diagnostics_layout.addWidget(issues_label)
        
        self.issues_label = QLabel("")
        self.issues_label.setWordWrap(True)
        self.issues_label.setStyleSheet("margin-left: 10px; color: #666;")
        diagnostics_layout.addWidget(self.issues_label)
        
        # Initially hidden
        self.diagnostics_group.setVisible(False)
        parent_layout.addWidget(self.diagnostics_group)
    
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
        
        # Update utilisation table
        capacity_data = None
        if analysis.resource_capacity:
            # Get all resource types dynamically
            capacity_data = analysis.resource_capacity.get_all_resources()
        
        self.utilisation_model.set_data(analysis.utilization, capacity_data)
        
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
        
        # Update enhanced diagnostics section
        if not analysis.feasible and analysis.infeasibility_diagnostics:
            self.diagnostics_group.setVisible(True)
            diagnostics = analysis.infeasibility_diagnostics
            
            # Update primary reason with severity styling
            severity_color = {
                "Critical": "#D32F2F",
                "High": "#F57C00", 
                "Moderate": "#FBC02D",
                "Low": "#388E3C",
                "Unknown": "#666"
            }.get(diagnostics.severity, "#666")
            
            self.primary_reason_label.setText(
                f"🔍 Primary Issue: {diagnostics.primary_reason} ({diagnostics.severity} Severity)"
            )
            self.primary_reason_label.setStyleSheet(f"color: {severity_color};")
            
            # Update recommendations
            if diagnostics.recommendations:
                recommendations_text = "\n".join([f"• {rec}" for rec in diagnostics.recommendations[:5]])
                self.recommendations_label.setText(recommendations_text)
            else:
                self.recommendations_label.setText("No specific recommendations available.")
            
            # Update detailed issues
            issues_text = self._format_detailed_issues(diagnostics)
            self.issues_label.setText(issues_text)
            
        else:
            self.diagnostics_group.setVisible(False)
        
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
    
    def _format_detailed_issues(self, diagnostics) -> str:
        """Format detailed diagnostic issues for display."""
        issues = []
        
        # Resource overloads
        if diagnostics.resource_overloads:
            issues.append("🔴 Resource Overloads:")
            for overload in diagnostics.resource_overloads[:3]:  # Show top 3
                role = overload.get("role", "Unknown")
                util = overload.get("utilization_percentage", 0)
                additional = overload.get("min_additional_staff", 0)
                issues.append(f"   • {role}: {util:.1f}% utilised (need {additional} more staff)")
        
        # Scheduling conflicts
        if diagnostics.scheduling_conflicts:
            issues.append("⏰ Scheduling Conflicts:")
            for conflict in diagnostics.scheduling_conflicts[:3]:  # Show top 3
                if conflict.get("type") == "impossible_activity":
                    activity = conflict.get("activity_name", "Unknown")
                    role = conflict.get("role", "Unknown")
                    demand = conflict.get("demand", 0)
                    capacity = conflict.get("capacity", 0)
                    issues.append(f"   • '{activity}' needs {demand} {role} but only {capacity} available")
                elif conflict.get("type") == "time_horizon_exceeded":
                    excess = conflict.get("excess_slots", 0)
                    issues.append(f"   • Total activity time exceeds available slots by {excess}")
        
        # Invalid configurations
        if diagnostics.invalid_configurations:
            issues.append("⚠️ Configuration Issues:")
            for config in diagnostics.invalid_configurations[:3]:  # Show top 3
                if config.get("type") == "excessive_frequency":
                    activity = config.get("activity_name", "Unknown")
                    excess = config.get("excess", 0)
                    issues.append(f"   • '{activity}' frequency too high (reduce by {excess})")
                elif config.get("type") == "zero_resources":
                    activity = config.get("activity_name", "Unknown")
                    issues.append(f"   • '{activity}' requires no resources")
        
        # Constraint violations
        if diagnostics.constraint_violations:
            issues.append("🚫 Constraint Violations:")
            for violation in diagnostics.constraint_violations[:3]:  # Show top 3
                if violation.get("type") == "missing_resource_types":
                    missing = violation.get("missing_resources", [])
                    issues.append(f"   • Missing resource types: {', '.join(missing)}")
        
        return "\n".join(issues) if issues else "No detailed issues identified."
    
    def show_waiting(self):
        """Show the waiting page."""
        self.current_analysis = None
        self.stacked_widget.setCurrentIndex(0)
    
    def clear_results(self):
        """Clear all results and show waiting page."""
        self.show_waiting()
