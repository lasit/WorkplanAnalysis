#!/usr/bin/env python3
"""
Workplan Analysis - Main Application Entry Point
A work-plan feasibility checker using constraint programming.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Workplan Analysis")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Workplan Analysis")
    
    # Set application properties for cross-platform consistency
    try:
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    except AttributeError:
        # Attribute may not exist in older Qt versions
        pass
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
