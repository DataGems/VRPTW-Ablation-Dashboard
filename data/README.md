# Data Directory

This directory should contain the ablation experiment data for the VRPTW dashboard.

## Expected Data Structure

The dashboard expects data in the following directory structure:

```
data/
└── WillRezAbl/
    ├── C1_numCust_25/
    │   ├── normal/
    │   │   ├── jy_C101
    │   │   ├── jy_C102
    │   │   └── ...
    │   ├── cuts_off_graphs_on/
    │   └── ...
    ├── C1_numCust_50/
    ├── C1_numCust_100/
    ├── C2_numCust_100/
    ├── R1_numCust_50/
    ├── R1_numCust_100/
    ├── RC1_numCust_25/
    ├── RC1_numCust_50/
    ├── RC1_numCust_100/
    ├── RC2_numCust_25/
    └── RC2_numCust_50/
```

## Data Format

Each file (e.g., `jy_C101`) should be a JSON file containing experiment results with the following structure:

### Required Fields
- `lblp_lower`: Array of LP lower bounds by iteration
- `ROOT_LP_PRIOR_ADDING_CUTS`: Root LP value before cuts
- `OUR_ilp_objective`: ILP objective value
- `OUR_ilp_time`: ILP solve time

### Optional Fields
- `ub_lp`: Array of upper bounds by iteration
- `lp_time_LB`: Array of LP solve times
- `lp_time_project`: Array of projection times
- `prob_sizes_at_start`: Array of graph sizes at start
- `prob_sizes_after_compress`: Array of graph sizes after compression
- `prob_sizes_after_split`: Array of graph sizes after split
- `cuttingPlaneBendInfo`: Array of cutting plane information

## Setup Instructions

1. **Copy your experiment data** into the `WillRezAbl` subdirectory
2. **Update the data path** in `data_loader.py` if your data is in a different location
3. **Verify data loading** by running the dashboard and checking for any error messages

## Data Privacy

⚠️ **Important**: This directory should contain experimental data only. Do not commit sensitive or proprietary information to the public repository.

Consider adding `data/WillRezAbl/` to `.gitignore` if the data should not be publicly shared.

## Configuration

To use a different data location, modify the `base_dir` parameter in `data_loader.py`:

```python
# Change this line in data_loader.py
def load_ablation_data(base_dir: str = "data/WillRezAbl"):
```