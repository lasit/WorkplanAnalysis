"""Background worker for running solver analysis."""

from PyQt6.QtCore import QThread, pyqtSignal
from core.solver import WorkplanSolver
from core.models import Project, AnalysisResult


class SolverWorker(QThread):
    """Worker thread for running constraint programming analysis."""
    
    # Signals
    analysis_started = pyqtSignal()
    analysis_progress = pyqtSignal(str)  # Progress message
    analysis_completed = pyqtSignal(object)  # AnalysisResult
    analysis_failed = pyqtSignal(str)  # Error message
    
    def __init__(self, project: Project, time_limit: int = 30):
        super().__init__()
        self.project = project
        self.time_limit = time_limit
        self.solver = WorkplanSolver()
    
    def run(self):
        """Run the analysis in the background thread."""
        try:
            self.analysis_started.emit()
            self.analysis_progress.emit("Initializing solver...")
            
            # Run the analysis
            self.analysis_progress.emit("Expanding activities into occurrences...")
            self.analysis_progress.emit("Building constraint programming model...")
            self.analysis_progress.emit("Solving...")
            
            result = self.solver.analyze_project(self.project, self.time_limit)
            
            self.analysis_progress.emit("Analysis complete!")
            self.analysis_completed.emit(result)
            
        except Exception as e:
            self.analysis_failed.emit(str(e))
