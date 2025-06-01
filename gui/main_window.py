"""Main application window for Workplan Analysis."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QDockWidget, QMenuBar, QStatusBar, QFileDialog, QMessageBox,
    QApplication, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
from pathlib import Path
from typing import Optional, List

from core.models import Project, Activity, ResourceCapacity
from core.data_loader import DataLoader
from core.solver import WorkplanSolver
from .project_tree import ProjectTreeWidget
from .tabs.plan_tab import PlanTab
from .tabs.resources_tab import ResourcesTab
from .tabs.dashboard_tab import DashboardTab
from .tabs.analyses_tab import AnalysesTab
from .solver_worker import SolverWorker


class MainWindow(QMainWindow):
    """Main application window."""
    
    # Signals
    project_changed = pyqtSignal(object)  # Project
    analysis_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_project: Optional[Project] = None
        self.projects: List[Project] = []
        self.solver_worker: Optional[SolverWorker] = None
        
        self.setup_ui()
        self.setup_menus()
        self.setup_status_bar()
        self.connect_signals()
        
        # Load any existing projects
        self.load_existing_projects()
    
    def setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle("Workplan Analysis")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Create project tree widget
        self.project_tree = ProjectTreeWidget()
        self.project_tree.setMinimumWidth(250)
        self.project_tree.setMaximumWidth(400)
        splitter.addWidget(self.project_tree)
        
        # Create main tab widget
        self.tab_widget = QTabWidget()
        splitter.addWidget(self.tab_widget)
        
        # Set splitter proportions
        splitter.setSizes([300, 1100])
        
        # Create tabs
        self.plan_tab = PlanTab()
        self.resources_tab = ResourcesTab()
        self.dashboard_tab = DashboardTab()
        self.analyses_tab = AnalysesTab()
        
        # Add tabs to widget
        self.tab_widget.addTab(self.plan_tab, "Plan")
        self.tab_widget.addTab(self.resources_tab, "Resources")
        self.tab_widget.addTab(self.dashboard_tab, "Dashboard")
        self.tab_widget.addTab(self.analyses_tab, "Analyses")
        
        # Initially disable tabs until project is loaded
        self.set_tabs_enabled(False)
    
    def setup_menus(self):
        """Set up application menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_project_action = QAction("&New Project...", self)
        new_project_action.setShortcut(QKeySequence.StandardKey.New)
        new_project_action.setStatusTip("Create a new project from CSV workplan")
        new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(new_project_action)
        
        file_menu.addSeparator()
        
        import_resources_action = QAction("&Import Resources...", self)
        import_resources_action.setStatusTip("Import resource configuration from YAML")
        import_resources_action.triggered.connect(self.import_resources)
        file_menu.addAction(import_resources_action)
        
        export_resources_action = QAction("&Export Resources...", self)
        export_resources_action.setStatusTip("Export current resource configuration to YAML")
        export_resources_action.triggered.connect(self.export_resources)
        file_menu.addAction(export_resources_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Project menu
        project_menu = menubar.addMenu("&Project")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.setStatusTip("Refresh current project")
        refresh_action.triggered.connect(self.refresh_project)
        project_menu.addAction(refresh_action)
        
        # Analysis menu
        analysis_menu = menubar.addMenu("&Analysis")
        
        run_analysis_action = QAction("&Run Analysis", self)
        run_analysis_action.setShortcut(QKeySequence("F5"))
        run_analysis_action.setStatusTip("Run feasibility analysis on current project")
        run_analysis_action.triggered.connect(self.run_analysis)
        analysis_menu.addAction(run_analysis_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.setStatusTip("About Workplan Analysis")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def connect_signals(self):
        """Connect signals between components."""
        # Project tree signals
        self.project_tree.project_selected.connect(self.on_project_selected)
        self.project_tree.analysis_selected.connect(self.on_analysis_selected)
        self.project_tree.project_duplicated.connect(self.on_project_duplicated)
        
        # Tab signals
        self.resources_tab.resources_changed.connect(self.on_resources_changed)
        self.dashboard_tab.analysis_requested.connect(self.on_analysis_requested)
        self.plan_tab.plan_changed.connect(self.on_plan_changed)
        
        # Internal signals
        self.project_changed.connect(self.on_project_changed)
        self.analysis_requested.connect(self.on_analysis_requested)
    
    def set_tabs_enabled(self, enabled: bool):
        """Enable or disable tabs based on project state."""
        for i in range(self.tab_widget.count()):
            self.tab_widget.setTabEnabled(i, enabled)
    
    def new_project(self):
        """Create a new project from CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Workplan CSV File",
            str(Path.home()),
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Load activities from CSV
            activities = DataLoader.load_workplan_csv(Path(file_path))
            
            # Validate data
            warnings = DataLoader.validate_workplan_data(activities)
            if warnings:
                warning_text = "\n".join(warnings)
                reply = QMessageBox.question(
                    self,
                    "Data Validation Warnings",
                    f"The following warnings were found:\n\n{warning_text}\n\nContinue anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # Create project name from file
            project_name = Path(file_path).stem
            
            # Check if project already exists
            existing_names = [p.name for p in self.projects]
            if project_name in existing_names:
                counter = 1
                while f"{project_name}_{counter}" in existing_names:
                    counter += 1
                project_name = f"{project_name}_{counter}"
            
            # Create new project with temporary path (will be updated after copying)
            project = Project(
                name=project_name,
                workplan_path=Path(file_path),
                activities=activities
            )
            
            # Ensure project directory exists
            project.ensure_project_dir()
            
            # Copy CSV file to project directory
            import shutil
            project_csv_path = project.project_dir / "workplan.csv"
            shutil.copy2(file_path, project_csv_path)
            
            # Update project to point to copied CSV
            project.workplan_path = project_csv_path
            
            # Create default resources file in project directory
            project_resources_path = project.project_dir / "resources.yml"
            if project.current_resources:
                DataLoader.save_resources_yaml(project.current_resources, project_resources_path)
            
            # Save the project
            project.save_project()
            
            # Add to projects list
            self.projects.append(project)
            
            # Update project tree
            self.project_tree.add_project(project)
            
            # Select the new project
            self.set_current_project(project)
            
            # Show summary
            summary = DataLoader.get_workplan_summary(activities)
            self.status_bar.showMessage(
                f"Created project '{project_name}': {summary.get('total_activities', 0)} activities, "
                f"{summary.get('total_occurrences', 0)} total occurrences (files copied to projects/{project_name}/)"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Creating Project",
                f"Failed to create project:\n\n{str(e)}"
            )
    
    def import_resources(self):
        """Import resource configuration from YAML file."""
        if not self.current_project:
            QMessageBox.information(self, "No Project", "Please select a project first.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Resource Configuration",
            str(Path.home()),
            "YAML Files (*.yml *.yaml);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            resources = DataLoader.load_resources_yaml(Path(file_path))
            self.current_project.current_resources = resources
            self.resources_tab.set_resources(resources)
            self.status_bar.showMessage("Resource configuration imported successfully")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import resource configuration:\n\n{str(e)}"
            )
    
    def export_resources(self):
        """Export current resource configuration to YAML file."""
        if not self.current_project or not self.current_project.current_resources:
            QMessageBox.information(self, "No Resources", "No resource configuration to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Resource Configuration",
            str(Path.home() / "resources.yml"),
            "YAML Files (*.yml *.yaml);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            DataLoader.save_resources_yaml(self.current_project.current_resources, Path(file_path))
            self.status_bar.showMessage(f"Resource configuration exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export resource configuration:\n\n{str(e)}"
            )
    
    def refresh_project(self):
        """Refresh the current project."""
        if self.current_project:
            self.set_current_project(self.current_project)
            self.status_bar.showMessage("Project refreshed")
    
    def run_analysis(self):
        """Run feasibility analysis on current project."""
        if not self.current_project:
            # Try to get the selected project from the tree as a fallback
            selected_project = self.project_tree.get_selected_project()
            if selected_project:
                self.set_current_project(selected_project)
                self.status_bar.showMessage(f"Selected project: {selected_project.name}")
            else:
                QMessageBox.information(self, "No Project", "Please select a project first.")
                return
        
        # Verify we have activities to analyse
        if not self.current_project.activities:
            QMessageBox.information(
                self, 
                "No Activities", 
                f"Project '{self.current_project.name}' has no activities to analyse."
            )
            return
        
        # Show which project we're analyzing
        self.status_bar.showMessage(f"Running analysis on project: {self.current_project.name}")
        self.analysis_requested.emit()
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Workplan Analysis",
            "Workplan Analysis v1.0.0\n\n"
            "A work-plan feasibility checker using constraint programming.\n\n"
            "Built with PyQt6 and OR-Tools."
        )
    
    def set_current_project(self, project: Project):
        """Set the current active project."""
        self.current_project = project
        self.project_changed.emit(project)
        self.set_tabs_enabled(True)
        
        # Update status bar to show current project
        self.status_bar.showMessage(f"Current project: {project.name}")
        
        # Switch to plan tab to show the loaded data
        self.tab_widget.setCurrentIndex(0)
    
    def load_existing_projects(self):
        """Load any existing projects from the file system."""
        try:
            existing_projects = Project.get_all_projects()
            for project in existing_projects:
                self.projects.append(project)
                self.project_tree.add_project(project)
            
            if existing_projects:
                self.status_bar.showMessage(f"Loaded {len(existing_projects)} existing project(s)")
        except Exception as e:
            print(f"Warning: Could not load existing projects: {e}")
    
    def on_project_selected(self, project: Project):
        """Handle project selection from tree."""
        # Find the matching project in our projects list to ensure object consistency
        matching_project = None
        for p in self.projects:
            if p.name == project.name and p.workplan_path == project.workplan_path:
                matching_project = p
                break
        
        if matching_project:
            self.set_current_project(matching_project)
        else:
            # If no match found, use the provided project and add it to our list
            self.projects.append(project)
            self.set_current_project(project)
    
    def on_analysis_selected(self, analysis):
        """Handle analysis selection from tree."""
        # Switch to dashboard tab and show the selected analysis
        self.tab_widget.setCurrentIndex(2)
        self.dashboard_tab.show_analysis(analysis)
    
    def on_project_changed(self, project: Project):
        """Handle project change signal."""
        # Update all tabs with new project data
        self.plan_tab.set_project(project)
        self.resources_tab.set_project(project)
        self.dashboard_tab.set_project(project)
        self.analyses_tab.set_project(project)
        
        # Update project tree
        self.project_tree.update_project(project)
    
    def on_resources_changed(self, resources: ResourceCapacity):
        """Handle resource configuration changes."""
        if self.current_project:
            self.current_project.current_resources = resources
            
            # Update Plan tab to reflect new working days calculation
            self.plan_tab.update_display()
            
            # Save resources to project directory
            try:
                project_resources_path = self.current_project.project_dir / "resources.yml"
                DataLoader.save_resources_yaml(resources, project_resources_path)
                # Auto-save project when resources change
                self.current_project.save_project()
            except Exception as e:
                print(f"Warning: Could not auto-save project: {e}")
    
    def on_analysis_requested(self):
        """Handle analysis request."""
        if not self.current_project:
            return
        
        # Check if solver is already running
        if self.solver_worker and self.solver_worker.isRunning():
            QMessageBox.information(
                self,
                "Analysis Running",
                "An analysis is already running. Please wait for it to complete."
            )
            return
        
        # Start the solver in a background thread
        self.solver_worker = SolverWorker(self.current_project)
        
        # Connect worker signals
        self.solver_worker.analysis_started.connect(self.on_analysis_started)
        self.solver_worker.analysis_progress.connect(self.on_analysis_progress)
        self.solver_worker.analysis_completed.connect(self.on_analysis_completed)
        self.solver_worker.analysis_failed.connect(self.on_analysis_failed)
        
        # Start the worker
        self.solver_worker.start()
    
    def on_analysis_started(self):
        """Handle analysis start."""
        self.status_bar.showMessage("Starting analysis...")
        
        # Switch to dashboard tab to show progress
        self.tab_widget.setCurrentIndex(2)
    
    def on_analysis_progress(self, message: str):
        """Handle analysis progress updates."""
        self.status_bar.showMessage(f"Analysis: {message}")
    
    def on_analysis_completed(self, result):
        """Handle analysis completion."""
        if not self.current_project:
            return
        
        # Add result to project
        self.current_project.analyses.append(result)
        
        # Auto-save project with new analysis
        try:
            self.current_project.save_project()
        except Exception as e:
            print(f"Warning: Could not auto-save project after analysis: {e}")
        
        # Update UI
        self.project_tree.update_project(self.current_project)
        self.dashboard_tab.show_analysis(result)
        self.analyses_tab.update_analyses_list()
        
        # Show completion message
        verdict = "FEASIBLE" if result.feasible else "INFEASIBLE"
        solve_time = result.solver_stats.get('solve_time', 0)
        
        self.status_bar.showMessage(
            f"Analysis complete: {verdict} (solved in {solve_time:.2f}s)"
        )
        
        # Clean up worker
        self.solver_worker = None
    
    def on_analysis_failed(self, error_message: str):
        """Handle analysis failure."""
        self.status_bar.showMessage("Analysis failed")
        
        QMessageBox.critical(
            self,
            "Analysis Error",
            f"The analysis failed with the following error:\n\n{error_message}"
        )
        
        # Clean up worker
        self.solver_worker = None
    
    def on_project_duplicated(self, duplicated_project: Project):
        """Handle project duplication."""
        # Add the duplicated project to our projects list
        self.projects.append(duplicated_project)
        
        # Set it as the current project
        self.set_current_project(duplicated_project)
        
        # Update status bar
        self.status_bar.showMessage(f"Project duplicated successfully: {duplicated_project.name}")
    
    def on_plan_changed(self):
        """Handle plan changes from the plan tab."""
        if self.current_project:
            # Update project tree to reflect changes
            self.project_tree.update_project(self.current_project)
            
            # Update other tabs that might be affected
            self.resources_tab.set_project(self.current_project)
            
            # Update status bar
            self.status_bar.showMessage(f"Plan modified: {self.current_project.name}")
