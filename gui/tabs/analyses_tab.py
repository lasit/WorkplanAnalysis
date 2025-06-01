"""Analyses tab for displaying analysis history."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QGroupBox, QTextEdit, QSplitter,
    QMessageBox, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction
from typing import Optional, List
from datetime import datetime

from core.models import Project, AnalysisResult


class AnalysisListWidget(QListWidget):
    """Custom list widget for displaying analyses with context menu."""
    
    # Signals
    analysis_selected = pyqtSignal(object)  # AnalysisResult
    analysis_deleted = pyqtSignal(object)   # AnalysisResult
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_context_menu()
    
    def setup_ui(self):
        """Set up the list widget."""
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.itemSelectionChanged.connect(self.on_selection_changed)
    
    def setup_context_menu(self):
        """Set up context menu."""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def add_analysis(self, analysis: AnalysisResult):
        """Add an analysis to the list."""
        # Create list item
        item = QListWidgetItem()
        
        # Format display text
        timestamp_str = analysis.timestamp.strftime("%Y-%m-%d %H:%M")
        feasible_str = "✅" if analysis.feasible else "❌"
        
        # Get utilization summary
        if analysis.utilization:
            max_util = max(analysis.utilization.values())
            util_summary = f"Max: {max_util:.1f}%"
        else:
            util_summary = "No data"
        
        display_text = f"{timestamp_str} {feasible_str} ({util_summary})"
        item.setText(display_text)
        
        # Store analysis data
        item.setData(Qt.ItemDataRole.UserRole, analysis)
        
        # Set tooltip
        tooltip = f"Analysis: {timestamp_str}\n"
        tooltip += f"Feasible: {'Yes' if analysis.feasible else 'No'}\n"
        if analysis.utilization:
            tooltip += "Utilization:\n"
            for role, util in analysis.utilization.items():
                tooltip += f"  {role}: {util:.1f}%\n"
        if analysis.solver_stats:
            solve_time = analysis.solver_stats.get("solve_time", 0)
            if solve_time > 0:
                tooltip += f"Solve time: {solve_time:.3f}s"
        item.setToolTip(tooltip)
        
        # Add to list (insert at top for newest first)
        self.insertItem(0, item)
    
    def set_analyses(self, analyses: List[AnalysisResult]):
        """Set the list of analyses to display."""
        self.clear()
        
        # Sort by timestamp (newest first)
        sorted_analyses = sorted(analyses, key=lambda a: a.timestamp, reverse=True)
        
        for analysis in sorted_analyses:
            self.add_analysis(analysis)
    
    def get_selected_analysis(self) -> Optional[AnalysisResult]:
        """Get the currently selected analysis."""
        current_item = self.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def on_selection_changed(self):
        """Handle selection changes."""
        analysis = self.get_selected_analysis()
        if analysis:
            self.analysis_selected.emit(analysis)
    
    def show_context_menu(self, position):
        """Show context menu for list items."""
        item = self.itemAt(position)
        if not item:
            return
        
        analysis = item.data(Qt.ItemDataRole.UserRole)
        if not analysis:
            return
        
        menu = QMenu(self)
        
        # View action
        view_action = QAction("View Analysis", self)
        view_action.triggered.connect(lambda: self.analysis_selected.emit(analysis))
        menu.addAction(view_action)
        
        menu.addSeparator()
        
        # Delete action
        delete_action = QAction("Delete Analysis", self)
        delete_action.triggered.connect(lambda: self.delete_analysis_with_confirmation(analysis))
        menu.addAction(delete_action)
        
        menu.exec(self.mapToGlobal(position))
    
    def delete_analysis_with_confirmation(self, analysis: AnalysisResult):
        """Delete an analysis with user confirmation."""
        timestamp_str = analysis.timestamp.strftime("%Y-%m-%d %H:%M")
        reply = QMessageBox.question(
            self,
            "Delete Analysis",
            f"Are you sure you want to delete the analysis from {timestamp_str}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.analysis_deleted.emit(analysis)


class AnalysesTab(QWidget):
    """Tab for displaying and managing analysis history."""
    
    # Signals
    analysis_selected = pyqtSignal(object)  # AnalysisResult
    
    def __init__(self):
        super().__init__()
        self.current_project: Optional[Project] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create splitter for list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - analyses list
        self.setup_analyses_list(splitter)
        
        # Right side - analysis details
        self.setup_analysis_details(splitter)
        
        # Set splitter proportions
        splitter.setSizes([400, 600])
    
    def setup_analyses_list(self, parent_splitter):
        """Set up the analyses list section."""
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        # Header
        header_label = QLabel("Analysis History")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(12)
        header_label.setFont(header_font)
        list_layout.addWidget(header_label)
        
        # Analyses list
        self.analyses_list = AnalysisListWidget()
        self.analyses_list.analysis_selected.connect(self.on_analysis_selected)
        self.analyses_list.analysis_deleted.connect(self.on_analysis_deleted)
        list_layout.addWidget(self.analyses_list)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.clicked.connect(self.clear_all_analyses)
        buttons_layout.addWidget(self.clear_all_button)
        
        buttons_layout.addStretch()
        list_layout.addLayout(buttons_layout)
        
        parent_splitter.addWidget(list_widget)
    
    def setup_analysis_details(self, parent_splitter):
        """Set up the analysis details section."""
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        # Header
        self.details_header = QLabel("Select an analysis to view details")
        details_font = QFont()
        details_font.setBold(True)
        details_font.setPointSize(12)
        self.details_header.setFont(details_font)
        details_layout.addWidget(self.details_header)
        
        # Details text area
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        # Use a monospace font (fallback to system default if Courier not available)
        mono_font = QFont()
        mono_font.setFamily("Monaco")  # macOS monospace font
        mono_font.setPointSize(10)
        mono_font.setStyleHint(QFont.StyleHint.Monospace)
        self.details_text.setFont(mono_font)
        details_layout.addWidget(self.details_text)
        
        # Action buttons for selected analysis
        details_buttons_layout = QHBoxLayout()
        
        self.view_dashboard_button = QPushButton("View in Dashboard")
        self.view_dashboard_button.clicked.connect(self.view_in_dashboard)
        self.view_dashboard_button.setEnabled(False)
        details_buttons_layout.addWidget(self.view_dashboard_button)
        
        self.export_button = QPushButton("Export Analysis")
        self.export_button.clicked.connect(self.export_analysis)
        self.export_button.setEnabled(False)
        details_buttons_layout.addWidget(self.export_button)
        
        details_buttons_layout.addStretch()
        details_layout.addLayout(details_buttons_layout)
        
        parent_splitter.addWidget(details_widget)
        
        # Initially show placeholder
        self.show_no_selection()
    
    def set_project(self, project: Project):
        """Set the current project and update the display."""
        self.current_project = project
        self.update_analyses_list()
        self.show_no_selection()
    
    def update_analyses_list(self):
        """Update the analyses list with current project data."""
        if not self.current_project:
            self.analyses_list.clear()
            return
        
        self.analyses_list.set_analyses(self.current_project.analyses)
    
    def on_analysis_selected(self, analysis: AnalysisResult):
        """Handle analysis selection."""
        self.show_analysis_details(analysis)
        self.analysis_selected.emit(analysis)
    
    def on_analysis_deleted(self, analysis: AnalysisResult):
        """Handle analysis deletion."""
        if self.current_project and analysis in self.current_project.analyses:
            self.current_project.analyses.remove(analysis)
            self.update_analyses_list()
            self.show_no_selection()
    
    def show_analysis_details(self, analysis: AnalysisResult):
        """Show details for the selected analysis."""
        timestamp_str = analysis.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        self.details_header.setText(f"Analysis Details - {timestamp_str}")
        
        # Build details text
        details = []
        details.append(f"Analysis Results")
        details.append("=" * 50)
        details.append(f"Timestamp: {timestamp_str}")
        details.append(f"Feasible: {'Yes' if analysis.feasible else 'No'}")
        details.append("")
        
        # Resource capacity used
        if analysis.resource_capacity:
            details.append("Resource Capacity:")
            details.append(f"  Ranger Coordinator: {analysis.resource_capacity.ranger_coordinator}")
            details.append(f"  Senior Ranger: {analysis.resource_capacity.senior_ranger}")
            details.append(f"  Ranger: {analysis.resource_capacity.ranger}")
            details.append(f"  Slots per day: {analysis.resource_capacity.slots_per_day}")
            if analysis.resource_capacity.public_holidays:
                details.append(f"  Public holidays: {', '.join(analysis.resource_capacity.public_holidays)}")
            details.append("")
        
        # Utilization
        if analysis.utilization:
            details.append("Resource Utilization:")
            for role, util in analysis.utilization.items():
                status = ""
                if util > 100:
                    status = " (OVERLOADED)"
                elif util > 90:
                    status = " (High)"
                elif util > 70:
                    status = " (Moderate)"
                else:
                    status = " (Low)"
                details.append(f"  {role}: {util:.1f}%{status}")
            details.append("")
        
        # Overloads (if any)
        if analysis.overloads:
            details.append("Capacity Overloads:")
            for overload in analysis.overloads:
                date = overload.get("date", "Unknown")
                slot = overload.get("slot", "Unknown")
                role = overload.get("role", "Unknown")
                extra = overload.get("extra_needed", 0)
                details.append(f"  {date} {slot}: {role} needs {extra} more staff")
            details.append("")
        
        # Solver statistics
        if analysis.solver_stats:
            details.append("Solver Statistics:")
            stats = analysis.solver_stats
            details.append(f"  Status: {stats.get('status', 'Unknown')}")
            
            solve_time = stats.get('solve_time', 0)
            if solve_time > 0:
                details.append(f"  Solve time: {solve_time:.3f} seconds")
            
            if 'num_variables' in stats:
                details.append(f"  Variables: {stats['num_variables']}")
            if 'num_constraints' in stats:
                details.append(f"  Constraints: {stats['num_constraints']}")
            
            # Add any other solver stats
            for key, value in stats.items():
                if key not in ['status', 'solve_time', 'num_variables', 'num_constraints']:
                    details.append(f"  {key}: {value}")
        
        self.details_text.setPlainText("\n".join(details))
        
        # Enable action buttons
        self.view_dashboard_button.setEnabled(True)
        self.export_button.setEnabled(True)
    
    def show_no_selection(self):
        """Show placeholder when no analysis is selected."""
        self.details_header.setText("Select an analysis to view details")
        self.details_text.setPlainText("No analysis selected.\n\nSelect an analysis from the list to view detailed information.")
        
        # Disable action buttons
        self.view_dashboard_button.setEnabled(False)
        self.export_button.setEnabled(False)
    
    def view_in_dashboard(self):
        """View the selected analysis in the dashboard tab."""
        analysis = self.analyses_list.get_selected_analysis()
        if analysis:
            # This signal will be connected to switch to dashboard tab
            self.analysis_selected.emit(analysis)
    
    def export_analysis(self):
        """Export the selected analysis to a file."""
        analysis = self.analyses_list.get_selected_analysis()
        if not analysis:
            return
        
        # This would open a file dialog and export the analysis
        # For now, show a placeholder message
        QMessageBox.information(
            self,
            "Export Analysis",
            "Analysis export functionality will be implemented in a future version."
        )
    
    def clear_all_analyses(self):
        """Clear all analyses with user confirmation."""
        if not self.current_project or not self.current_project.analyses:
            QMessageBox.information(
                self,
                "No Analyses",
                "There are no analyses to clear."
            )
            return
        
        count = len(self.current_project.analyses)
        reply = QMessageBox.question(
            self,
            "Clear All Analyses",
            f"Are you sure you want to delete all {count} analyses?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_project.analyses.clear()
            self.update_analyses_list()
            self.show_no_selection()
