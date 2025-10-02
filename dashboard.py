"""
Streamlit Dashboard for Ablation Analysis
Vehicle Routing Problem with Time Windows (VRPTW) Experiments
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from data_loader import (
    load_ablation_data, 
    get_available_instances, 
    get_iteration_data,
    get_summary_stats
)

# Page configuration
st.set_page_config(
    page_title="VRPTW Ablation Analysis Dashboard",
    page_icon="🚛",
    layout="wide"
)

# Title and description
st.title("🚛 VRPTW Ablation Analysis Dashboard")
st.markdown("Interactive visualization of Vehicle Routing Problem with Time Windows ablation experiments")

# Load data with caching
@st.cache_data
def load_data():
    return load_ablation_data()

try:
    df = load_data()
    if df.empty:
        st.error("No data loaded. Please check the data directory.")
        st.stop()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar controls
st.sidebar.header("🔧 Controls")

# Customer count filter
available_num_cust = sorted(df['num_cust'].unique())
selected_num_cust = st.sidebar.selectbox(
    "Number of Customers:",
    available_num_cust,
    index=len(available_num_cust)-1 if available_num_cust else 0
)

# Condition filter
available_conditions = sorted(df['condition'].unique())
selected_condition = st.sidebar.selectbox(
    "Ablation Condition:",
    available_conditions,
    index=0 if available_conditions else 0
)

# Instance filter
available_instances = get_available_instances(df, selected_num_cust, selected_condition)
if not available_instances:
    st.sidebar.error(f"No instances found for {selected_num_cust} customers and {selected_condition} condition")
    st.stop()

selected_instance = st.sidebar.selectbox(
    "Instance:",
    available_instances,
    index=0
)

# Visualization type
viz_type = st.sidebar.selectbox(
    "Visualization Type:",
    ["LP Convergence (Iterations)", "LP Convergence (Time)", "Time Graph Evolution", "NG Graph Evolution"],
    index=0
)

# Get data for selected instance and condition
iteration_data = get_iteration_data(df, selected_instance, selected_condition)
summary_stats = get_summary_stats(df, selected_instance, selected_condition)

if iteration_data is None or iteration_data.empty:
    st.error(f"No iteration data found for {selected_instance} with {selected_condition} condition")
    st.stop()

# Statistics sidebar
st.sidebar.header("📊 Statistics")
for stat_name, stat_value in summary_stats.items():
    if pd.notna(stat_value):
        if stat_name in ['Root LP', 'Final LB', 'ILP Objective', 'LB Improvement']:
            st.sidebar.metric(stat_name, f"{stat_value:.2f}")
        elif stat_name in ['ILP Time', 'Total LP Time']:
            st.sidebar.metric(stat_name, f"{stat_value:.3f}s")
        else:
            st.sidebar.metric(stat_name, f"{stat_value}")

# Main visualization area
st.header(f"📈 {viz_type}")
st.subheader(f"Instance: {selected_instance} | Condition: {selected_condition} | Customers: {selected_num_cust}")

def create_lp_convergence_plot(data, time_based=False):
    """Create LP convergence plot (iteration or time-based)"""
    fig = go.Figure()
    
    x_col = 'cumulative_time' if time_based else 'iteration'
    x_title = 'Cumulative Time (seconds)' if time_based else 'Iteration'
    
    # Filter out NaN values
    valid_data = data.dropna(subset=['lblp_lower', x_col])
    
    if valid_data.empty:
        st.warning("No valid data for LP convergence plot")
        return fig
    
    # LP Lower Bound
    if 'lblp_lower' in valid_data.columns:
        fig.add_trace(go.Scatter(
            x=valid_data[x_col],
            y=valid_data['lblp_lower'],
            mode='lines+markers',
            name='LP Lower Bound',
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        ))
    
    # Upper Bound (if available)
    if 'ub_lp' in valid_data.columns:
        ub_data = valid_data.dropna(subset=['ub_lp'])
        if not ub_data.empty:
            fig.add_trace(go.Scatter(
                x=ub_data[x_col],
                y=ub_data['ub_lp'],
                mode='lines+markers',
                name='Upper Bound',
                line=dict(color='red', width=2),
                marker=dict(size=6)
            ))
    
    # Mark when cuts start (if applicable)
    if 'cut_TOT_gen_cut' in valid_data.columns:
        first_cut_iter = valid_data[valid_data['cut_TOT_gen_cut'] > 0]
        if not first_cut_iter.empty:
            cut_start = first_cut_iter.iloc[0][x_col]
            fig.add_vline(
                x=cut_start,
                line_dash="dash",
                line_color="green",
                annotation_text="Cuts Start"
            )
    
    fig.update_layout(
        title=f"LP Convergence ({'Time-based' if time_based else 'Iteration-based'})",
        xaxis_title=x_title,
        yaxis_title="Objective Value",
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_graph_evolution_plot(data, graph_type="time"):
    """Create graph size evolution plot"""
    fig = go.Figure()
    
    # Define columns based on graph type
    if graph_type.lower() == "time":
        start_col = 'start_timeGraph'
        compress_col = 'compress_timeGraph'
        split_col = 'split_timeGraph'
        title_prefix = "Time Graph"
    else:  # NG graph
        start_col = 'start_ngGraph'
        compress_col = 'compress_ngGraph'
        split_col = 'split_ngGraph'
        title_prefix = "NG Graph"
    
    # Filter out NaN values for iteration column
    valid_data = data.dropna(subset=['iteration'])
    
    if valid_data.empty:
        st.warning(f"No valid data for {title_prefix} evolution plot")
        return fig
    
    # Add traces for each stage
    for col, name, color in [
        (start_col, f'{title_prefix} Start', 'blue'),
        (compress_col, f'{title_prefix} Compress', 'orange'),
        (split_col, f'{title_prefix} Split', 'green')
    ]:
        if col in valid_data.columns:
            stage_data = valid_data.dropna(subset=[col])
            if not stage_data.empty:
                fig.add_trace(go.Scatter(
                    x=stage_data['iteration'],
                    y=stage_data[col],
                    mode='lines+markers',
                    name=name,
                    line=dict(color=color, width=2),
                    marker=dict(size=6)
                ))
    
    # Mark when cuts start (if applicable)
    if 'cut_TOT_gen_cut' in valid_data.columns:
        first_cut_iter = valid_data[valid_data['cut_TOT_gen_cut'] > 0]
        if not first_cut_iter.empty:
            cut_start = first_cut_iter.iloc[0]['iteration']
            fig.add_vline(
                x=cut_start,
                line_dash="dash",
                line_color="red",
                annotation_text="Cuts Start"
            )
    
    fig.update_layout(
        title=f"{title_prefix} Size Evolution",
        xaxis_title="Iteration",
        yaxis_title="Graph Size",
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

# Create and display the appropriate visualization
if viz_type == "LP Convergence (Iterations)":
    fig = create_lp_convergence_plot(iteration_data, time_based=False)
elif viz_type == "LP Convergence (Time)":
    fig = create_lp_convergence_plot(iteration_data, time_based=True)
elif viz_type == "Time Graph Evolution":
    fig = create_graph_evolution_plot(iteration_data, graph_type="time")
elif viz_type == "NG Graph Evolution":
    fig = create_graph_evolution_plot(iteration_data, graph_type="ng")

st.plotly_chart(fig, use_container_width=True)

# Data exploration section
with st.expander("🔍 Raw Iteration Data"):
    st.subheader("Iteration-level Data")
    
    # Display key columns
    display_cols = ['iteration', 'lblp_lower', 'ub_lp', 'lp_time_LB', 'lp_time_project', 'cumulative_time']
    
    # Add graph size columns if they exist
    for col in ['start_timeGraph', 'compress_timeGraph', 'split_timeGraph', 
                'start_ngGraph', 'compress_ngGraph', 'split_ngGraph']:
        if col in iteration_data.columns:
            display_cols.append(col)
    
    # Add cutting plane columns if they exist
    for col in ['cut_tot_cut_value', 'cut_TOT_gen_cut', 'cut_tot_time_opt']:
        if col in iteration_data.columns:
            display_cols.append(col)
    
    # Filter to available columns
    available_display_cols = [col for col in display_cols if col in iteration_data.columns]
    
    if available_display_cols:
        st.dataframe(iteration_data[available_display_cols], use_container_width=True)
    else:
        st.warning("No displayable columns found in iteration data")

# Comparison section
st.header("🔄 Compare Conditions")

# Multi-select for conditions
comparison_conditions = st.multiselect(
    "Select conditions to compare:",
    available_conditions,
    default=[selected_condition] if len(available_conditions) > 1 else available_conditions[:1]
)

if len(comparison_conditions) > 1:
    # Create comparison plot
    fig_comparison = go.Figure()
    
    colors = px.colors.qualitative.Set1
    
    for i, condition in enumerate(comparison_conditions):
        comp_data = get_iteration_data(df, selected_instance, condition)
        if comp_data is not None and not comp_data.empty:
            valid_data = comp_data.dropna(subset=['lblp_lower', 'iteration'])
            if not valid_data.empty:
                fig_comparison.add_trace(go.Scatter(
                    x=valid_data['iteration'],
                    y=valid_data['lblp_lower'],
                    mode='lines+markers',
                    name=f'{condition}',
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=4)
                ))
    
    fig_comparison.update_layout(
        title=f"LP Lower Bound Comparison - {selected_instance}",
        xaxis_title="Iteration",
        yaxis_title="LP Lower Bound",
        showlegend=True,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_comparison, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("*VRPTW Ablation Analysis Dashboard - Vehicle Routing Problem with Time Windows*")