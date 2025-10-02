# VRPTW Ablation Analysis Dashboard

Interactive Streamlit dashboard for visualizing Vehicle Routing Problem with Time Windows (VRPTW) ablation experiments.

## Features

- **LP Convergence Visualization**: View LP lower bound convergence over iterations or time
- **Graph Evolution Tracking**: Monitor Time Graph and NG Graph size evolution during optimization
- **Ablation Condition Comparison**: Compare different experimental conditions side-by-side
- **Interactive Filtering**: Filter by customer count, ablation condition, and instance
- **Real-time Statistics**: View key metrics and performance indicators

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Dashboard**
   ```bash
   streamlit run dashboard.py
   ```

3. **Access Dashboard**
   - Open your browser to `http://localhost:8501`
   - Use the sidebar controls to explore different instances and conditions

## Data Structure

The dashboard expects data in the following directory structure:
```
Sept_19/WillRezAbl/
├── C1_numCust_25/
│   ├── normal/
│   ├── cuts_off_graphs_on/
│   └── ...
├── C1_numCust_50/
├── C1_numCust_100/
└── ...
```

Each condition directory contains JSON files with experiment results including:
- LP bounds (`lblp_lower`, `ub_lp`)
- Timing data (`lp_time_LB`, `lp_time_project`)
- Graph sizes (`start_timeGraph`, `compress_timeGraph`, `split_timeGraph`)
- Cutting plane information

## Visualization Types

### LP Convergence (Iterations)
Shows how LP lower and upper bounds evolve over iterations, with markers for when cutting planes begin.

### LP Convergence (Time)
Same as above but with cumulative time on the x-axis instead of iterations.

### Time Graph Evolution
Tracks the size evolution of the Time Graph representation through start, compress, and split phases.

### NG Graph Evolution
Tracks the size evolution of the NG (Neighborhood Graph) representation through optimization phases.

## Interactive Features

- **Sidebar Filtering**: Filter by customer count, condition, and instance
- **Statistics Panel**: Real-time metrics including LP bounds, solve times, and iterations
- **Condition Comparison**: Multi-select comparison of different ablation conditions
- **Raw Data Explorer**: Expandable section to view iteration-level data tables
- **Responsive Design**: Charts automatically resize to fit the browser window

## File Structure

- `dashboard.py` - Main Streamlit application
- `data_loader.py` - Data processing and loading functions
- `requirements.txt` - Python package dependencies
- `README.md` - This documentation file