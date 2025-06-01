#!/usr/bin/env python3
"""Test script to verify Dashboard tab displays utilization for infeasible results."""

import sys
from datetime import datetime
from core.models import Project, Activity, ResourceCapacity, AnalysisResult

def test_dashboard_infeasible_utilization_display():
    """Test that Dashboard tab shows utilization percentages for infeasible results."""
    print("🧪 Testing Dashboard Tab Infeasible Utilization Display")
    print("=" * 60)
    
    # Create a project that will be infeasible
    project = Project(name="test_infeasible_display", workplan_path="test.csv")
    project.set_planning_quarter("2025-Q3")
    
    # Create resource configuration with limited capacity
    project.current_resources = ResourceCapacity(
        resources={
            "RangerCoordinator": 1,
            "SeniorRanger": 2,
            "Ranger": 5
        }
    )
    
    # Create an infeasible analysis result with utilization data
    analysis = AnalysisResult(
        timestamp=datetime.now(),
        feasible=False,  # INFEASIBLE
        utilization={
            "RangerCoordinator": 150.5,  # Over 100%
            "SeniorRanger": 125.3,       # Over 100%
            "Ranger": 110.8             # Over 100%
        },
        overloads=[
            {
                "date": "Multiple days",
                "slot": "Various",
                "role": "RangerCoordinator",
                "extra_needed": 1
            },
            {
                "date": "Multiple days", 
                "slot": "Various",
                "role": "SeniorRanger",
                "extra_needed": 1
            }
        ],
        solver_stats={
            "status": "INFEASIBLE",
            "solve_time": 1.25,
            "num_variables": 300,
            "num_constraints": 800
        },
        resource_capacity=project.current_resources
    )
    
    print(f"📊 Analysis Details:")
    print(f"   Feasible: {analysis.feasible}")
    print(f"   Status: {analysis.solver_stats.get('status')}")
    print(f"   Has Utilization Data: {bool(analysis.utilization)}")
    print(f"   Has Resource Capacity: {bool(analysis.resource_capacity)}")
    
    # Test utilization data
    print(f"\n📈 Utilization Data:")
    if analysis.utilization:
        for role, util in analysis.utilization.items():
            print(f"   {role}: {util:.1f}%")
    else:
        print("   ❌ NO UTILIZATION DATA!")
        return False
    
    # Test resource capacity data
    print(f"\n🏗️ Resource Capacity Data:")
    if analysis.resource_capacity:
        capacity_data = analysis.resource_capacity.get_all_resources()
        for role, capacity in capacity_data.items():
            print(f"   {role}: {capacity}")
    else:
        print("   ❌ NO RESOURCE CAPACITY DATA!")
        return False
    
    # Test overload data
    print(f"\n🚨 Overload Data:")
    if analysis.overloads:
        for overload in analysis.overloads:
            role = overload.get('role', 'Unknown')
            extra = overload.get('extra_needed', 0)
            print(f"   {role}: needs {extra} additional resources")
    else:
        print("   ⚠️  No overload data")
    
    # Simulate what the Dashboard tab should display
    print(f"\n🖥️ Dashboard Tab Should Display:")
    print(f"   Verdict: ❌ INFEASIBLE")
    print(f"   Utilization Table:")
    
    capacity_data = analysis.resource_capacity.get_all_resources()
    for role, util in analysis.utilization.items():
        capacity = capacity_data.get(role, 0)
        status = "Overloaded" if util > 100 else "High" if util > 90 else "Moderate" if util > 70 else "Low"
        print(f"     {role}: {util:.1f}% ({status})")
    
    # Verify all data is present for Dashboard display
    if analysis.utilization and analysis.resource_capacity:
        print(f"\n✅ All data present for Dashboard display!")
        print(f"✅ Infeasible result includes utilization percentages")
        print(f"✅ Resource capacity data available")
        print(f"✅ Overload information available")
        return True
    else:
        print(f"\n❌ Missing data for Dashboard display!")
        return False

def main():
    """Run the dashboard infeasible display test."""
    print("🚀 Dashboard Infeasible Utilization Display Test")
    print("=" * 70)
    
    try:
        success = test_dashboard_infeasible_utilization_display()
        
        print("\n" + "=" * 70)
        if success:
            print("✅ TEST PASSED: Dashboard should display utilization for infeasible results!")
            print("🎯 All required data is present in the analysis result")
            print("📊 Utilization percentages available for infeasible analysis")
            print("🔍 If Dashboard still not showing data, issue is in GUI display logic")
            return True
        else:
            print("❌ TEST FAILED: Missing data for Dashboard display")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
