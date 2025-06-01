#!/usr/bin/env python3
"""Test Dashboard tab show_analysis method directly."""

import sys
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from core.models import Project, ResourceCapacity, AnalysisResult
from gui.tabs.dashboard_tab import DashboardTab

def test_dashboard_show_analysis():
    """Test Dashboard tab show_analysis method with infeasible result."""
    print("🧪 Testing Dashboard Tab show_analysis Method")
    print("=" * 50)
    
    # Create QApplication (required for Qt widgets)
    app = QApplication(sys.argv)
    
    # Create Dashboard tab
    dashboard = DashboardTab()
    
    # Create an infeasible analysis result
    project = Project(name="test_dashboard", workplan_path="test.csv")
    project.current_resources = ResourceCapacity(
        resources={
            "RangerCoordinator": 1,
            "SeniorRanger": 2,
            "Ranger": 5
        }
    )
    
    analysis = AnalysisResult(
        timestamp=datetime.now(),
        feasible=False,  # INFEASIBLE
        utilization={
            "RangerCoordinator": 150.5,
            "SeniorRanger": 125.3,
            "Ranger": 110.8
        },
        overloads=[
            {
                "date": "Multiple days",
                "slot": "Various",
                "role": "RangerCoordinator",
                "extra_needed": 1
            }
        ],
        solver_stats={
            "status": "INFEASIBLE",
            "solve_time": 1.25
        },
        resource_capacity=project.current_resources
    )
    
    print(f"📊 Test Analysis:")
    print(f"   Feasible: {analysis.feasible}")
    print(f"   Utilization data: {bool(analysis.utilization)}")
    print(f"   Resource capacity: {bool(analysis.resource_capacity)}")
    
    # Test the show_analysis method
    try:
        print(f"\n🖥️ Calling dashboard.show_analysis()...")
        dashboard.show_analysis(analysis)
        
        # Check if utilization model has data
        model = dashboard.utilization_model
        row_count = model.rowCount()
        
        print(f"   Utilization table rows: {row_count}")
        
        if row_count > 0:
            print(f"   ✅ Utilization table has {row_count} rows")
            
            # Check the data in each row
            for row in range(row_count):
                role_index = model.index(row, 0)
                util_index = model.index(row, 1)
                status_index = model.index(row, 2)
                
                role = model.data(role_index)
                util = model.data(util_index)
                status = model.data(status_index)
                
                print(f"     Row {row}: {role} - {util} ({status})")
            
            print(f"   ✅ Dashboard table populated correctly!")
            return True
        else:
            print(f"   ❌ Utilization table is empty!")
            
            # Debug: Check if data was set
            print(f"   Debug: model.data_items = {model.data_items}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error calling show_analysis: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        app.quit()

def main():
    """Run the dashboard show_analysis test."""
    print("🚀 Dashboard show_analysis Test")
    print("=" * 40)
    
    try:
        success = test_dashboard_show_analysis()
        
        print("\n" + "=" * 40)
        if success:
            print("✅ TEST PASSED: Dashboard show_analysis works correctly!")
            print("🎯 Utilization table displays infeasible analysis data")
            return True
        else:
            print("❌ TEST FAILED: Dashboard show_analysis not working")
            print("🔧 Issue in Dashboard tab display logic")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
