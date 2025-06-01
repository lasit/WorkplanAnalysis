#!/usr/bin/env python3
"""
Test script to verify the complete workflow works correctly.
"""

from pathlib import Path
from core.models import Project
from core.data_loader import DataLoader
from core.solver import WorkplanSolver

def test_full_workflow():
    """Test the complete workflow from data loading to analysis."""
    print("Testing Complete Workplan Analysis Workflow")
    print("=" * 60)
    
    # Step 1: Load sample data
    csv_path = Path("sample_workplan.csv")
    yaml_path = Path("sample_resources.yml")
    
    if not csv_path.exists() or not yaml_path.exists():
        print("❌ Sample files not found")
        return
    
    try:
        # Step 2: Load and validate data
        print("Step 1: Loading data...")
        activities = DataLoader.load_workplan_csv(csv_path)
        resources = DataLoader.load_resources_yaml(yaml_path)
        
        print(f"✅ Loaded {len(activities)} activities")
        print(f"✅ Loaded resources: RC={resources.ranger_coordinator}, SR={resources.senior_ranger}, R={resources.ranger}")
        
        # Step 3: Create project
        print("\nStep 2: Creating project...")
        project = Project(
            name="workflow_test",
            workplan_path=csv_path,
            activities=activities,
            current_resources=resources
        )
        print(f"✅ Created project: {project.name}")
        
        # Step 4: Run analysis
        print("\nStep 3: Running analysis...")
        solver = WorkplanSolver()
        result = solver.analyze_project(project, time_limit_seconds=15)
        
        print(f"✅ Analysis completed")
        print(f"   Feasible: {'YES' if result.feasible else 'NO'}")
        print(f"   Timestamp: {result.timestamp}")
        print(f"   Solver status: {result.solver_stats.get('status', 'Unknown')}")
        print(f"   Solve time: {result.solver_stats.get('solve_time', 0):.3f}s")
        
        # Step 5: Display results
        print("\nStep 4: Analysis results...")
        if result.utilization:
            print("   Resource Utilization:")
            for role, util in result.utilization.items():
                status = ""
                if util > 100:
                    status = " (OVERLOADED)"
                elif util > 90:
                    status = " (High)"
                elif util > 70:
                    status = " (Moderate)"
                else:
                    status = " (Low)"
                print(f"     {role}: {util:.1f}%{status}")
        
        if result.overloads:
            print("   Capacity Overloads:")
            for overload in result.overloads:
                print(f"     {overload}")
        
        # Step 6: Add to project and verify
        print("\nStep 5: Adding result to project...")
        project.analyses.append(result)
        print(f"✅ Project now has {len(project.analyses)} analysis(es)")
        
        latest = project.get_latest_analysis()
        if latest:
            print(f"✅ Latest analysis: {latest.timestamp}")
        
        print(f"\n🎉 Complete workflow test successful!")
        print(f"   The GUI application should now be able to:")
        print(f"   1. Load the sample project (File → New Project)")
        print(f"   2. Configure resources (Resources tab)")
        print(f"   3. Run analysis (Dashboard tab → Run Analysis button or F5)")
        print(f"   4. View results (Dashboard tab)")
        print(f"   5. Browse analysis history (Analyses tab)")
        
    except Exception as e:
        print(f"❌ Error in workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_workflow()
