# VRPTW Ablation Dashboard

Interactive visualization dashboard for Vehicle Routing Problem with Time Windows (VRPTW) ablation experiments. This Streamlit-based tool allows researchers to explore and analyze the effects of different algorithmic components on solver performance.

![VRPTW Dashboard](docs/screenshots/dashboard-preview.png)

## Features

- 📊 **LP Convergence Analysis**: Track LP bounds evolution over iterations and time
- 📈 **Graph Size Evolution**: Monitor Time Graph and NG Graph sizes through optimization phases
- 🔄 **Ablation Comparison**: Compare performance across different experimental conditions
- 📉 **Interactive Visualizations**: Zoom, pan, and explore data with Plotly charts
- 📋 **Real-time Statistics**: View key metrics including LP bounds, solve times, and iteration counts

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/DataGems/VRPTW-Ablation-Dashboard.git
cd VRPTW-Ablation-Dashboard
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run dashboard.py
```

### 4. Open in Browser
Navigate to `http://localhost:8501` in your web browser

## Dashboard Overview

### Ablation Conditions
The dashboard analyzes several experimental conditions:
- **normal**: Baseline algorithm with all components enabled
- **cuts_off_graphs_on**: Cutting planes disabled, graph operations enabled
- **no_ub_use_remove**: Upper bound usage disabled
- **no_cuts_or_graphs**: Both cuts and graph operations disabled

### Visualization Types
1. **LP Convergence (Iterations)**: Shows LP lower/upper bound progression over iterations
2. **LP Convergence (Time)**: Time-based view of bound convergence
3. **Time Graph Evolution**: Tracks time graph size through start→compress→split phases
4. **NG Graph Evolution**: Monitors neighborhood graph size evolution

### Interactive Controls
- **Customer Count Filter**: Select instances with 25, 50, or 100 customers
- **Ablation Condition**: Choose which experimental condition to analyze
- **Instance Selection**: Pick specific Solomon instances (C101, R101, RC101, etc.)
- **Comparison Mode**: Compare multiple conditions side-by-side

## Data Structure

The dashboard processes JSON experiment files with the following structure:

```json
{
  "lblp_lower": [191.3, 191.3, ...],           // LP lower bounds by iteration
  "ub_lp": [195.2, 193.1, ...],               // Upper bounds by iteration
  "lp_time_LB": [0.012, 0.015, ...],          // LP solve times
  "prob_sizes_at_start": [{"timeGraph": 27, "ngGraph": 27}, ...],
  "cuttingPlaneBendInfo": [...],              // Cutting plane information
  "ROOT_LP_PRIOR_ADDING_CUTS": 191.3,         // Initial LP value
  "OUR_ilp_objective": 191.3,                 // Final ILP objective
  "OUR_ilp_time": 0.006                       // Total solve time
}
```

## Research Context

This dashboard supports research in vehicle routing optimization, specifically analyzing:
- Effects of cutting planes on LP bound tightness
- Graph compression strategies for large-scale instances
- Trade-offs between solution time and quality
- Impact of various algorithmic components

## Related Work

- Original Solomon benchmark instances: [Solomon (1987)](https://www.sintef.no/projectweb/top/vrptw/solomon-benchmark/)
- Related visualization: [Solomon Instance Viewer](https://github.com/DataGems/Solomon_Instance_Viewer)

## Citation

If you use this dashboard in your research, please cite:
```bibtex
@software{vrptw_ablation_dashboard,
  author = {Your Name},
  title = {VRPTW Ablation Dashboard},
  year = {2024},
  url = {https://github.com/DataGems/VRPTW-Ablation-Dashboard}
}
```

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Contact

For questions or support, please open an issue on GitHub.