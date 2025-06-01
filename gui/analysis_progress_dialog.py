"""Analysis progress dialog with cancellation capability."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QProgressBar, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QMovie
from typing import Optional
import time


class AnalysisProgressDialog(QDialog):
    """Dialog showing analysis progress with cancellation capability."""
    
    # Signals
    cancel_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_time = time.time()
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Analysis in Progress")
        self.setModal(True)
        self.setFixedSize(450, 300)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("🔧 Running Workplan Analysis")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Status label
        self.status_label = QLabel("Initializing analysis...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Progress bar (indeterminate)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Elapsed time
        self.time_label = QLabel("Elapsed time: 0s")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.time_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Progress log
        log_label = QLabel("Progress Log:")
        log_font = QFont()
        log_font.setBold(True)
        log_label.setFont(log_font)
        layout.addWidget(log_label)
        
        self.progress_log = QTextEdit()
        self.progress_log.setMaximumHeight(80)
        self.progress_log.setReadOnly(True)
        self.progress_log.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Monaco', 'Consolas', monospace;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.progress_log)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel Analysis")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Add initial log entry
        self.add_log_entry("Analysis started...")
    
    def setup_timer(self):
        """Set up timer for updating elapsed time."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_time)
        self.timer.start(1000)  # Update every second
    
    def update_elapsed_time(self):
        """Update the elapsed time display."""
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        
        if minutes > 0:
            time_text = f"Elapsed time: {minutes}m {seconds}s"
        else:
            time_text = f"Elapsed time: {seconds}s"
        
        self.time_label.setText(time_text)
        
        # Change color if taking too long
        if elapsed > 30:
            self.time_label.setStyleSheet("color: #ff6b35; font-size: 11px; font-weight: bold;")
        elif elapsed > 15:
            self.time_label.setStyleSheet("color: #f39c12; font-size: 11px; font-weight: bold;")
    
    def update_status(self, message: str):
        """Update the status message."""
        self.status_label.setText(message)
        self.add_log_entry(message)
    
    def add_log_entry(self, message: str):
        """Add an entry to the progress log."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.progress_log.append(log_entry)
        
        # Auto-scroll to bottom
        scrollbar = self.progress_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_cancel_clicked(self):
        """Handle cancel button click."""
        self.cancel_button.setText("Cancelling...")
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
        """)
        
        self.update_status("Cancellation requested...")
        self.add_log_entry("User requested cancellation")
        self.cancel_requested.emit()
    
    def analysis_completed(self, success: bool, message: str = ""):
        """Called when analysis is completed."""
        self.timer.stop()
        
        if success:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    text-align: center;
                    font-weight: bold;
                }
                QProgressBar::chunk {
                    background-color: #28a745;
                    border-radius: 3px;
                }
            """)
            self.update_status("✅ Analysis completed successfully!")
            self.cancel_button.setText("Close")
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    text-align: center;
                    font-weight: bold;
                }
                QProgressBar::chunk {
                    background-color: #dc3545;
                    border-radius: 3px;
                }
            """)
            error_msg = f"❌ Analysis failed: {message}" if message else "❌ Analysis failed"
            self.update_status(error_msg)
            self.cancel_button.setText("Close")
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
        
        self.cancel_button.setEnabled(True)
        self.cancel_button.clicked.disconnect()
        self.cancel_button.clicked.connect(self.accept)
    
    def analysis_cancelled(self):
        """Called when analysis is cancelled."""
        self.timer.stop()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #ffc107;
                border-radius: 3px;
            }
        """)
        self.update_status("⚠️ Analysis cancelled by user")
        self.cancel_button.setText("Close")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.cancel_button.setEnabled(True)
        self.cancel_button.clicked.disconnect()
        self.cancel_button.clicked.connect(self.accept)
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.timer.isActive():
            # Analysis is still running, request cancellation
            self.on_cancel_clicked()
            event.ignore()  # Don't close yet
        else:
            event.accept()
