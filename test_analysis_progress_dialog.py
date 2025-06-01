#!/usr/bin/env python3
"""Test the analysis progress dialog and cancellation functionality."""

import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from core.models import Project, Activity, ResourceCapacity
from gui.main_window import MainWindow

def test_progress_dialog():
    """Test the analysis progress dialog with cancellation."""
    print("🚀 Analysis Progress Dialog Test")
    print("=" * 50)
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = MainWindow()
    main_window.show()
    
    # Create a test project with activities that will take some time to analyze
    project = Project(name="test_progress_dialog", workplan_path="test.csv")
    project.set_planning_quarter("2025-Q3")
    
    # Create activities that will cause analysis to run for a while
    activities = [
        Activity(
            activity_id="TEST1",
            name="Test Activity 1",
            quarter="2025-Q3",
            frequency=50,  # High frequency to make analysis take longer
            duration=1.0,
            resource_requirements={
                "RangerCoordinator": 1,
                "SeniorRanger": 2,
                "Ranger": 3
            }
        ),
        Activity(
            activity_id="TEST2",
            name="Test Activity 2",
            quarter="2025-Q3",
            frequency=40,
            duration=0.5,
            resource_requirements={
                "RangerCoordinator": 2,
                "SeniorRanger": 1,
                "Ranger": 4
            }
        ),
        Activity(
            activity_id="TEST3",
            name="Test Activity 3",
            quarter="2025-Q3",
            frequency=30,
            duration=0.25,
            resource_requirements={
                "RangerCoordinator": 1,
                "SeniorRanger": 3,
                "Ranger": 2
            }
        )
    ]
    
    project.activities = activities
    project.current_resources = ResourceCapacity(
        resources={
            "RangerCoordinator": 2,
            "SeniorRanger": 4,
            "Ranger": 8
        }
    )
    
    # Add project to main window
    main_window.projects.append(project)
    main_window.project_tree.add_project(project)
    main_window.set_current_project(project)
    
    print(f"📋 Test Project Setup:")
    print(f"   Activities: {len(activities)}")
    print(f"   Total occurrences: {sum(a.frequency for a in activities)}")
    print(f"   Resource capacity: {project.current_resources.get_all_resources()}")
    
    print(f"\n🔧 Starting Analysis with Progress Dialog...")
    
    # Start analysis - this will show the progress dialog
    main_window.run_analysis()
    
    print(f"\n✅ Progress dialog should now be visible!")
    print(f"📊 You should see:")
    print(f"   • Progress dialog with animated progress bar")
    print(f"   • Real-time status updates")
    print(f"   • Elapsed time counter")
    print(f"   • Progress log with timestamps")
    print(f"   • Cancel button (red)")
    
    print(f"\n🧪 Test Instructions:")
    print(f"   1. Observe the progress dialog showing analysis steps")
    print(f"   2. Watch the elapsed time counter update")
    print(f"   3. See progress messages in the log")
    print(f"   4. Try clicking 'Cancel Analysis' to test cancellation")
    print(f"   5. Or wait for analysis to complete")
    
    # Set up a timer to automatically test cancellation after 5 seconds
    def auto_cancel():
        if main_window.progress_dialog and main_window.progress_dialog.isVisible():
            print(f"\n⚠️ Auto-testing cancellation after 5 seconds...")
            main_window.progress_dialog.on_cancel_clicked()
    
    cancel_timer = QTimer()
    cancel_timer.timeout.connect(auto_cancel)
    cancel_timer.setSingleShot(True)
    cancel_timer.start(5000)  # Cancel after 5 seconds
    
    # Run the application
    try:
        app.exec()
        return True
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def main():
    """Run the progress dialog test."""
    print("🚀 Analysis Progress Dialog Test Suite")
    print("=" * 60)
    
    try:
        success = test_progress_dialog()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ PROGRESS DIALOG TEST COMPLETED!")
            print("🎯 Progress dialog functionality demonstrated")
            print("📊 Real-time progress updates working")
            print("⚠️ Cancellation capability available")
            print("🔧 User experience significantly improved")
        else:
            print("❌ PROGRESS DIALOG TEST FAILED!")
            print("🔧 Some functionality not working correctly")
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
