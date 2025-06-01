# Workplan Analysis

A PyQt6-based desktop application for analyzing the feasibility of quarterly work plans using constraint programming.

## Overview

Workplan Analysis is a work-plan feasibility checker that evaluates whether a quarterly Miradi work-plan can be delivered by the available staff resources. It provides clear **Feasible/Infeasible** verdicts plus detailed utilization metrics.

## Features

### Current Implementation (Phase 1 - GUI Framework)

✅ **Complete GUI Framework**
- Main window with project tree sidebar
- Tabbed interface (Plan, Resources, Dashboard, Analyses)
- Cross-platform PyQt6 implementation

✅ **Data Management**
- CSV workplan import and validation
- YAML resource configuration
- Project-based organization
- Data validation and summary statistics

✅ **User Interface Components**
- **Plan Tab**: Display workplan activities with summary statistics
- **Resources Tab**: Edit resource capacity and public holidays
- **Dashboard Tab**: Ready for analysis results display
- **Analyses Tab**: Analysis history management

✅ **Sample Data**
- 30 sample activities for 2025-Q3
- Realistic resource requirements
- Sample resource configuration

### Completed Features (Phase 2 - Solver Integration)

✅ **Constraint Programming Solver**
- OR-Tools CP-SAT implementation
- 240 time slots (60 days × 4 quarter-day slots)
- Feasibility analysis with overload detection
- Threaded solver execution (non-blocking GUI)

✅ **Analysis Results**
- Utilization calculations per role
- Overload identification and reporting
- Solver statistics and performance metrics
- Real-time progress updates

✅ **Analysis Management**
- Analysis history storage
- Project-based analysis organization
- Dashboard visualization
- Analysis comparison capabilities

## Installation

### Prerequisites

- Python 3.9 or higher
- PyQt6
- pandas
- PyYAML
- OR-Tools
- matplotlib

### Cross-Platform Support

✅ **macOS** - Original development platform  
✅ **Windows 11** - Fully tested and compatible  
✅ **Linux** - Should work (PyQt6 cross-platform)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python3 main.py
```

## Windows 11 Support

This project has been fully tested and verified on Windows 11. Windows-specific files have been created for easy setup:

- **`start_app.bat`** - Windows launcher script (double-click to run)
- **`install_dependencies.bat`** - Dependency installation script
- **`WINDOWS_SETUP.md`** - Detailed Windows setup guide

For Windows users, simply double-click `start_app.bat` to launch the application.

## Usage

### Loading a Project

1. **File → New Project...** or `Cmd+N`
2. Select a CSV workplan file (use `sample_workplan.csv` for testing)
3. Review any validation warnings
4. The project will appear in the sidebar

### Configuring Resources

1. Switch to the **Resources** tab
2. Adjust staff capacity for each role:
   - Ranger Coordinator
   - Senior Ranger
   - Ranger
3. Add public holidays if needed
4. Click **Save Resource Configuration**

### Sample Data

The project includes sample data for testing:

- **sample_workplan.csv**: 30 activities for Q3 2025
  - 166 total occurrences
  - Mixed duration activities (0.25, 0.5, 1.0 days)
  - Realistic resource requirements

- **sample_resources.yml**: Default resource configuration
  - 1 Ranger Coordinator, 2 Senior Rangers, 5 Rangers
  - 4 slots per day (quarter-day granularity)
  - One public holiday (2025-08-25)

## Data Format

### Workplan CSV Format

```csv
ActivityID,ActivityName,Quarter,Frequency,Duration,RangerCoordinator,SeniorRanger,Ranger
A01,Weed Control Patrol,2025-Q3,7,0.25,0,2,3
```

**Fields:**
- `ActivityID`: Unique identifier
- `ActivityName`: Descriptive name
- `Quarter`: Planning quarter (e.g., "2025-Q3")
- `Frequency`: Number of times to execute (≥1)
- `Duration`: Time in days (0.25, 0.5, or 1.0)
- `RangerCoordinator`, `SeniorRanger`, `Ranger`: Staff required per role

### Resource Configuration YAML

```yaml
RangerCoordinator: 1
SeniorRanger: 2
Ranger: 5
slots_per_day: 4
public_holidays:
- '2025-08-25'
```

## Architecture

```
workplan_analysis/
├── main.py                    # Application entry point
├── requirements.txt           # Dependencies
├── core/                      # Business logic
│   ├── models.py             # Data models
│   └── data_loader.py        # CSV/YAML handling
├── gui/                       # User interface
│   ├── main_window.py        # Main application window
│   ├── project_tree.py       # Project sidebar
│   └── tabs/                 # Tab implementations
│       ├── plan_tab.py       # Workplan display
│       ├── resources_tab.py  # Resource editing
│       ├── dashboard_tab.py  # Results visualization
│       └── analyses_tab.py   # Analysis history
└── tests/                     # Test files
```

## Testing

Run the data loading test:
```bash
python3 test_data_loading.py
```

This verifies that the sample CSV and YAML files load correctly.

## Development Status

**Phase 1: GUI Framework** ✅ **COMPLETE**
- Full PyQt6 interface implementation
- Data loading and validation
- Project management
- Resource configuration

**Phase 2: Solver Integration** 🔄 **NEXT**
- OR-Tools CP-SAT constraint programming
- Feasibility analysis
- Utilization calculations
- Results visualization

**Phase 3: Advanced Features** 📋 **PLANNED**
- Analysis export (PDF/CSV)
- Advanced scheduling options
- Performance optimizations
- Packaging and distribution

## Technical Details

### Core Concepts

- **Project**: Container for workplan and resource scenarios
- **Analysis**: One solver run with specific resource configuration
- **Occurrence**: Single execution of an activity (after frequency expansion)
- **Slot**: Quarter-day (2-hour) time unit
- **Capacity**: Simultaneous staff availability per role per slot

### Constraint Programming Model

The solver will use:
- **Variables**: Boolean `start[job,slot]` for 240 time slots
- **Constraints**: Each job scheduled exactly once, capacity limits respected
- **Objective**: Feasibility search, then minimize overload if infeasible

## Contributing

The project follows a modular architecture with clear separation between:
- Data models (`core/models.py`)
- Business logic (`core/data_loader.py`)
- User interface (`gui/`)
- Future solver implementation

## License

This project is part of a work-plan feasibility analysis system for resource management in conservation and ranger operations.
