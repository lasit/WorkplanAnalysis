"""Project tree widget for displaying projects and analyses."""

from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, QInputDialog, QCheckBox, QVBoxLayout, QDialog, QDialogButtonBox, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from typing import Optional, List

from core.models import Project, AnalysisResult


class ProjectTreeWidget(QTreeWidget):
    """Tree widget for displaying projects and their analyses."""
    
    # Signals
    project_selected = pyqtSignal(object)  # Project
    analysis_selected = pyqtSignal(object)  # AnalysisResult
    project_duplicated = pyqtSignal(object)  # Project (new duplicated project)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_context_menu()
        
        # Keep track of projects and their tree items
        self.project_items = []  # List of (project, QTreeWidgetItem) tuples
    
    def setup_ui(self):
        """Set up the tree widget."""
        self.setHeaderLabel("Projects")
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        
        # Connect selection signal
        self.itemSelectionChanged.connect(self.on_selection_changed)
    
    def setup_context_menu(self):
        """Set up context menu for tree items."""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def add_project(self, project: Project):
        """Add a project to the tree."""
        # Create project item
        project_item = QTreeWidgetItem(self)
        project_item.setText(0, project.name)
        project_item.setData(0, Qt.ItemDataRole.UserRole, ("project", project))
        project_item.setExpanded(True)
        
        # Store reference
        self.project_items.append((project, project_item))
        
        # Add analyses if any
        for analysis in project.analyses:
            self.add_analysis_to_project(project, analysis)
    
    def _find_project_item(self, project: Project) -> Optional[QTreeWidgetItem]:
        """Find the tree widget item for a given project."""
        for proj, item in self.project_items:
            if proj == project:
                return item
        return None
    
    def add_analysis_to_project(self, project: Project, analysis: AnalysisResult):
        """Add an analysis to a project in the tree."""
        project_item = self._find_project_item(project)
        if project_item is None:
            return
        
        # Create analysis item
        analysis_item = QTreeWidgetItem(project_item)
        
        # Format timestamp for display
        timestamp_str = analysis.timestamp.strftime("%Y-%m-%d %H:%M")
        feasible_str = "✅" if analysis.feasible else "❌"
        analysis_item.setText(0, f"{timestamp_str} {feasible_str}")
        analysis_item.setData(0, Qt.ItemDataRole.UserRole, ("analysis", analysis))
        
        # Set tooltip with more details
        tooltip = f"Analysis: {timestamp_str}\n"
        tooltip += f"Feasible: {'Yes' if analysis.feasible else 'No'}\n"
        if analysis.utilization:
            tooltip += "Utilisation:\n"
            for role, util in analysis.utilization.items():
                tooltip += f"  {role}: {util:.1f}%\n"
        analysis_item.setToolTip(0, tooltip)
    
    def update_project(self, project: Project):
        """Update a project's display in the tree."""
        project_item = self._find_project_item(project)
        if project_item is None:
            self.add_project(project)
            return
        
        # Clear existing analysis items
        project_item.takeChildren()
        
        # Re-add all analyses
        for analysis in project.analyses:
            self.add_analysis_to_project(project, analysis)
    
    def remove_project(self, project: Project):
        """Remove a project from the tree."""
        project_item = self._find_project_item(project)
        if project_item is not None:
            index = self.indexOfTopLevelItem(project_item)
            if index >= 0:
                self.takeTopLevelItem(index)
            # Remove from our list
            self.project_items = [(p, i) for p, i in self.project_items if p != project]
    
    def on_selection_changed(self):
        """Handle selection changes in the tree."""
        selected_items = self.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        data = item.data(0, Qt.ItemDataRole.UserRole)
        
        if not data:
            return
        
        item_type, item_data = data
        
        if item_type == "project":
            self.project_selected.emit(item_data)
        elif item_type == "analysis":
            self.analysis_selected.emit(item_data)
    
    def show_context_menu(self, position):
        """Show context menu for tree items."""
        item = self.itemAt(position)
        if not item:
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        item_type, item_data = data
        
        menu = QMenu(self)
        
        if item_type == "project":
            # Project context menu
            refresh_action = QAction("Refresh Project", self)
            refresh_action.triggered.connect(lambda: self.refresh_project(item_data))
            menu.addAction(refresh_action)
            
            menu.addSeparator()
            
            duplicate_action = QAction("Duplicate Project...", self)
            duplicate_action.triggered.connect(lambda: self.duplicate_project_with_dialog(item_data))
            menu.addAction(duplicate_action)
            
            menu.addSeparator()
            
            remove_action = QAction("Remove Project", self)
            remove_action.triggered.connect(lambda: self.remove_project_with_confirmation(item_data))
            menu.addAction(remove_action)
            
        elif item_type == "analysis":
            # Analysis context menu
            view_action = QAction("View Analysis", self)
            view_action.triggered.connect(lambda: self.analysis_selected.emit(item_data))
            menu.addAction(view_action)
            
            menu.addSeparator()
            
            delete_action = QAction("Delete Analysis", self)
            delete_action.triggered.connect(lambda: self.delete_analysis_with_confirmation(item_data))
            menu.addAction(delete_action)
        
        if menu.actions():
            menu.exec(self.mapToGlobal(position))
    
    def refresh_project(self, project: Project):
        """Refresh a project's display."""
        self.update_project(project)
    
    def remove_project_with_confirmation(self, project: Project):
        """Remove a project with user confirmation."""
        reply = QMessageBox.question(
            self,
            "Remove Project",
            f"Are you sure you want to remove project '{project.name}'?\n\n"
            "This will only remove it from the current session. "
            "Project files will not be deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.remove_project(project)
    
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
            # Find the project containing this analysis and remove it
            for project, item in self.project_items:
                if analysis in project.analyses:
                    project.analyses.remove(analysis)
                    self.update_project(project)
                    break
    
    def get_selected_project(self) -> Optional[Project]:
        """Get the currently selected project."""
        selected_items = self.selectedItems()
        if not selected_items:
            return None
        
        item = selected_items[0]
        data = item.data(0, Qt.ItemDataRole.UserRole)
        
        if not data:
            return None
        
        item_type, item_data = data
        
        if item_type == "project":
            return item_data
        elif item_type == "analysis":
            # Find the parent project
            parent_item = item.parent()
            if parent_item:
                parent_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
                if parent_data and parent_data[0] == "project":
                    return parent_data[1]
        
        return None
    
    def select_project(self, project: Project):
        """Programmatically select a project in the tree."""
        project_item = self._find_project_item(project)
        if project_item is not None:
            self.setCurrentItem(project_item)
    
    def duplicate_project_with_dialog(self, project: Project):
        """Show dialog to duplicate a project with options."""
        dialog = DuplicateProjectDialog(project, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name, include_analyses = dialog.get_values()
            
            try:
                # Create the duplicate
                duplicated_project = project.duplicate(new_name, include_analyses)
                
                # Add to tree
                self.add_project(duplicated_project)
                
                # Select the new project
                self.select_project(duplicated_project)
                
                # Emit signal
                self.project_duplicated.emit(duplicated_project)
                
                # Show success message
                analyses_text = "with" if include_analyses else "without"
                QMessageBox.information(
                    self,
                    "Project Duplicated",
                    f"Project '{project.name}' has been successfully duplicated as '{new_name}' {analyses_text} analysis history."
                )
                
            except ValueError as e:
                QMessageBox.warning(
                    self,
                    "Duplication Failed",
                    f"Failed to duplicate project:\n\n{str(e)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Duplication Error",
                    f"An unexpected error occurred while duplicating the project:\n\n{str(e)}"
                )


class DuplicateProjectDialog(QDialog):
    """Dialog for duplicating a project with options."""
    
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Duplicate Project")
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(f"Duplicate project '{self.project.name}'")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # New name input
        layout.addWidget(QLabel("New project name:"))
        self.name_input = QInputDialog.getText(
            self, 
            "Project Name", 
            "Enter name for the duplicated project:",
            text=f"{self.project.name}_copy"
        )
        
        # Include analyses checkbox
        self.include_analyses_checkbox = QCheckBox("Include analysis history")
        self.include_analyses_checkbox.setToolTip(
            "If checked, all previous analyses will be copied to the new project.\n"
            "If unchecked, the new project will start with no analysis history."
        )
        layout.addWidget(self.include_analyses_checkbox)
        
        # Info text
        info_label = QLabel(
            "This will create a complete copy of the project including:\n"
            "• Workplan CSV file\n"
            "• Resource configuration\n"
            "• Project metadata\n"
            "• Analysis history (if selected)"
        )
        info_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(info_label)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_values(self):
        """Get the values from the dialog."""
        # Since we're using QInputDialog.getText, we need to handle it differently
        new_name, ok = QInputDialog.getText(
            self,
            "Project Name",
            "Enter name for the duplicated project:",
            text=f"{self.project.name}_copy"
        )
        
        if not ok or not new_name.strip():
            return None, False
            
        include_analyses = self.include_analyses_checkbox.isChecked()
        return new_name.strip(), include_analyses
    
    def exec(self):
        """Override exec to handle the input dialog properly."""
        new_name, ok = QInputDialog.getText(
            self,
            "Duplicate Project",
            f"Enter name for the duplicated project '{self.project.name}':",
            text=f"{self.project.name}_copy"
        )
        
        if not ok or not new_name.strip():
            return QDialog.DialogCode.Rejected
            
        self.new_name = new_name.strip()
        
        # Show checkbox dialog for analyses
        msg = QMessageBox(self)
        msg.setWindowTitle("Include Analysis History?")
        msg.setText(f"Include analysis history in the duplicated project '{self.new_name}'?")
        msg.setInformativeText(
            "• Yes: Copy all previous analyses to the new project\n"
            "• No: Start with a clean project (no analysis history)"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        
        result = msg.exec()
        self.include_analyses = result == QMessageBox.StandardButton.Yes
        
        return QDialog.DialogCode.Accepted
    
    def get_values(self):
        """Get the values from the dialog."""
        return getattr(self, 'new_name', ''), getattr(self, 'include_analyses', False)
