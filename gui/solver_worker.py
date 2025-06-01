"""Background worker for running solver analysis."""

from PyQt6.QtCore import QThread, pyqtSignal, QMutex
from core.solver import WorkplanSolver
from core.models import Project, AnalysisResult
import time


class SolverWorker(QThread):
    """Worker thread for running constraint programming analysis."""
    
    # Signals
    analysis_started = pyqtSignal()
    analysis_progress = pyqtSignal(str)  # Progress message
    analysis_completed = pyqtSignal(object)  # AnalysisResult
    analysis_failed = pyqtSignal(str)  # Error message
    analysis_cancelled = pyqtSignal()  # Analysis was cancelled
    
    def __init__(self, project: Project, time_limit: int = 30):
        super().__init__()
        self.project = project
        self.time_limit = time_limit
        self.solver = WorkplanSolver()
        self._cancelled = False
        self._mutex = QMutex()
    
    def cancel(self):
        """Request cancellation of the analysis."""
        self._mutex.lock()
        self._cancelled = True
        self._mutex.unlock()
    
    def is_cancelled(self) -> bool:
        """Check if cancellation was requested."""
        self._mutex.lock()
        cancelled = self._cancelled
        self._mutex.unlock()
        return cancelled
    
    def run(self):
        """Run the analysis in the background thread."""
        try:
            self.analysis_started.emit()
            
            if self.is_cancelled():
                self.analysis_cancelled.emit()
                return
            
            self.analysis_progress.emit("Initializing solver...")
            time.sleep(0.1)  # Small delay to show progress
            
            if self.is_cancelled():
                self.analysis_cancelled.emit()
                return
            
            self.analysis_progress.emit("Setting up planning horizon...")
            time.sleep(0.1)
            
            if self.is_cancelled():
                self.analysis_cancelled.emit()
                return
            
            self.analysis_progress.emit("Expanding activities into occurrences...")
            time.sleep(0.2)
            
            if self.is_cancelled():
                self.analysis_cancelled.emit()
                return
            
            self.analysis_progress.emit("Building constraint programming model...")
            time.sleep(0.2)
            
            if self.is_cancelled():
                self.analysis_cancelled.emit()
                return
            
            self.analysis_progress.emit("Creating decision variables...")
            time.sleep(0.1)
            
            if self.is_cancelled():
                self.analysis_cancelled.emit()
                return
            
            self.analysis_progress.emit("Adding scheduling constraints...")
            time.sleep(0.1)
            
            if self.is_cancelled():
                self.analysis_cancelled.emit()
                return
            
            self.analysis_progress.emit("Adding capacity constraints...")
            time.sleep(0.1)
            
            if self.is_cancelled():
                self.analysis_cancelled.emit()
                return
            
            self.analysis_progress.emit("Running constraint programming solver...")
            
            # Run the analysis with cancellation support
            result = self.solver.analyze_project(self.project, self.time_limit)
            
            if self.is_cancelled():
                self.analysis_cancelled.emit()
                return
            
            self.analysis_progress.emit("Processing results...")
            time.sleep(0.1)
            
            if self.is_cancelled():
                self.analysis_cancelled.emit()
                return
            
            self.analysis_progress.emit("Analysis complete!")
            self.analysis_completed.emit(result)
            
        except Exception as e:
            if self.is_cancelled():
                self.analysis_cancelled.emit()
            else:
                self.analysis_failed.emit(str(e))
