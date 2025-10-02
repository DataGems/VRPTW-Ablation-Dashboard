"""
Data loader for ablation analysis dashboard.
Processes JSON experiment files from Sept_19/WillRezAbl directory structure.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import re
from typing import Dict, List, Optional, Union
import streamlit as st


def parse_custom_json(json_text: str) -> dict:
    """
    Enhanced JSON parsing function that handles NaN and Infinity values.
    Similar to the R function in ablation.qmd.
    """
    # Replace problematic values with null
    json_text_fixed = json_text
    json_text_fixed = re.sub(r'\bNaN\b', 'null', json_text_fixed)
    json_text_fixed = re.sub(r'\bInfinity\b', 'null', json_text_fixed)
    json_text_fixed = re.sub(r'\b-Infinity\b', 'null', json_text_fixed)
    json_text_fixed = re.sub(r'\b-?Inf\b', 'null', json_text_fixed)
    
    return json.loads(json_text_fixed)


def read_one_file(file_path: Union[str, Path]) -> dict:
    """
    Read a single JSON file with error handling.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return parse_custom_json(content)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}


def extract_instance_name(filename: str) -> str:
    """
    Extract instance name from filename, handling various formats.
    Based on the R function extract_instance in ablation.qmd.
    """
    # Remove file extension
    base_name = re.sub(r'\.(txt|json)$', '', filename)
    
    # Handle special cases
    if base_name.startswith("BACK_jy_"):
        # BACK_jy_rc108.txt -> rc108_BACK
        instance_part = base_name.replace("BACK_jy_", "")
        return f"{instance_part}_BACK"
    elif base_name.endswith("_better"):
        # jy_rc108_better.json -> rc108_better
        instance_part = base_name.replace("jy_", "").replace("_better", "")
        return f"{instance_part}_better"
    elif base_name.startswith("jy_"):
        # jy_c101.txt -> c101
        return base_name.replace("jy_", "")
    
    # Fallback: return the base name
    return base_name


def process_iteration_data(data: dict) -> pd.DataFrame:
    """
    Extract iteration-level data from experiment JSON.
    Similar to iter_data_efficiency function in ablation.qmd.
    """
    if 'lblp_lower' not in data:
        print("Warning: lblp_lower not found")
        return pd.DataFrame()
    
    iterations = len(data.get('lblp_lower', []))
    if iterations == 0:
        print("Warning: No iterations found")
        return pd.DataFrame()
    
    # Initialize results dataframe
    results_df = pd.DataFrame({'iteration': range(1, iterations + 1)})
    
    # Core arrays to extract
    core_arrays = [
        'lblp_lower', 'ub_lp', 'did_compress',
        'lp_time_project', 'lp_time_LB', 'time_compress'
    ]
    
    for array_name in core_arrays:
        if array_name in data and len(data[array_name]) == iterations:
            results_df[array_name] = data[array_name]
        else:
            # Add column with NAs if missing
            results_df[array_name] = [np.nan] * iterations
    
    # Process problem sizes
    stage_names = ['prob_sizes_at_start', 'prob_sizes_after_compress', 'prob_sizes_after_split']
    stage_suffixes = ['start', 'compress', 'split']
    
    for stage_name, suffix in zip(stage_names, stage_suffixes):
        if stage_name in data:
            stage_data = data[stage_name]
            
            # Handle if it's a list of dictionaries
            if isinstance(stage_data, list) and len(stage_data) == iterations:
                time_graph_values = []
                ng_graph_values = []
                
                for item in stage_data:
                    if isinstance(item, dict):
                        time_graph_values.append(item.get('timeGraph', np.nan))
                        ng_graph_values.append(item.get('ngGraph', np.nan))
                    else:
                        time_graph_values.append(np.nan)
                        ng_graph_values.append(np.nan)
                
                results_df[f'{suffix}_timeGraph'] = time_graph_values
                results_df[f'{suffix}_ngGraph'] = ng_graph_values
            else:
                # Missing or wrong structure
                results_df[f'{suffix}_timeGraph'] = [np.nan] * iterations
                results_df[f'{suffix}_ngGraph'] = [np.nan] * iterations
        else:
            # Field completely missing
            results_df[f'{suffix}_timeGraph'] = [np.nan] * iterations
            results_df[f'{suffix}_ngGraph'] = [np.nan] * iterations
    
    # Process cutting plane info
    if 'cuttingPlaneBendInfo' in data:
        cut_data = data['cuttingPlaneBendInfo']
        
        if isinstance(cut_data, list) and len(cut_data) == iterations:
            results_df['cut_tot_cut_value'] = [
                item.get('tot_cut_value', np.nan) if isinstance(item, dict) else np.nan 
                for item in cut_data
            ]
            results_df['cut_TOT_gen_cut'] = [
                item.get('TOT_gen_cut', np.nan) if isinstance(item, dict) else np.nan 
                for item in cut_data
            ]
            results_df['cut_tot_time_opt'] = [
                item.get('tot_time_opt', np.nan) if isinstance(item, dict) else np.nan 
                for item in cut_data
            ]
            results_df['cut_max_time_opt'] = [
                item.get('max_time_opt', np.nan) if isinstance(item, dict) else np.nan 
                for item in cut_data
            ]
        else:
            # Missing or wrong structure
            for col in ['cut_tot_cut_value', 'cut_TOT_gen_cut', 'cut_tot_time_opt', 'cut_max_time_opt']:
                results_df[col] = [np.nan] * iterations
    else:
        # Field completely missing
        for col in ['cut_tot_cut_value', 'cut_TOT_gen_cut', 'cut_tot_time_opt', 'cut_max_time_opt']:
            results_df[col] = [np.nan] * iterations
    
    # Add cumulative time
    if 'lp_time_LB' in results_df.columns and 'lp_time_project' in results_df.columns:
        results_df['cumulative_time'] = (
            results_df['lp_time_LB'].fillna(0) + results_df['lp_time_project'].fillna(0)
        ).cumsum()
    else:
        results_df['cumulative_time'] = [np.nan] * iterations
    
    return results_df


@st.cache_data
def load_ablation_data(base_dir: str = "data/WillRezAbl") -> pd.DataFrame:
    """
    Load and process all ablation experiment data.
    """
    base_path = Path(base_dir)
    
    if not base_path.exists():
        st.error(f"Base directory {base_dir} does not exist")
        return pd.DataFrame()
    
    # Define datasets and conditions
    datasets = [
        "C1_numCust_25", "C1_numCust_50", "C1_numCust_100",
        "C2_numCust_100", 
        "R1_numCust_50", "R1_numCust_100",
        "RC1_numCust_25", "RC1_numCust_50", "RC1_numCust_100",
        "RC2_numCust_25", "RC2_numCust_50"
    ]
    
    base_conditions = ["normal", "cuts_off_graphs_on", "cuts_off_graph_on", "no_ub_use_remove", "no_cuts_or_graphs"]
    
    all_results = []
    
    for dataset in datasets:
        dataset_dir = base_path / dataset
        
        if not dataset_dir.exists():
            print(f"Warning: Dataset directory {dataset_dir} not found")
            continue
        
        # Get available conditions for this dataset
        available_conditions = [d.name for d in dataset_dir.iterdir() if d.is_dir()]
        conditions_to_process = [c for c in base_conditions if c in available_conditions]
        
        for condition in conditions_to_process:
            condition_dir = dataset_dir / condition
            
            if not condition_dir.exists():
                print(f"Warning: Directory {condition_dir} not found")
                continue
            
            # Find all files/directories starting with jy_
            files = list(condition_dir.glob("jy_*"))
            print(f"Processing {dataset}/{condition}: found {len(files)} files")
            
            for file_path in files:
                try:
                    # Handle both files and directories
                    if file_path.is_file():
                        data = read_one_file(file_path)
                    elif file_path.is_dir():
                        # Look for JSON files inside
                        json_files = list(file_path.glob("*.json")) + list(file_path.glob("*.txt"))
                        if json_files:
                            data = read_one_file(json_files[0])
                        else:
                            continue
                    else:
                        continue
                    
                    if not data:
                        continue
                    
                    # Extract iteration-level data
                    iteration_data = process_iteration_data(data)
                    
                    # Extract customer count
                    if "100" in dataset:
                        num_cust = 100
                    elif "50" in dataset:
                        num_cust = 50
                    else:
                        num_cust = 25
                    
                    # Extract instance type
                    instance_type_match = re.match(r'^([CR][12])', dataset)
                    instance_type = instance_type_match.group(1) if instance_type_match else "Unknown"
                    
                    # Create summary record
                    record = {
                        'dataset': dataset,
                        'num_cust': num_cust,
                        'instance_type': instance_type,
                        'condition': condition,
                        'instance': extract_instance_name(file_path.name),
                        'root_lp': data.get('ROOT_LP_PRIOR_ADDING_CUTS', np.nan),
                        'final_lb': data.get('lblp_lower', [np.nan])[-1] if data.get('lblp_lower') else np.nan,
                        'ilp_objective': data.get('OUR_ilp_objective', np.nan),
                        'ilp_time': data.get('OUR_ilp_time', np.nan),
                        'total_lp_time': sum([
                            sum(data.get('lp_time_LB', [])),
                            sum(data.get('lp_time_project', []))
                        ]),
                        'iterations': len(data.get('lblp_lower', [])),
                        'total_cuts': 0,  # Will calculate from iteration data if needed
                        'iteration_data': iteration_data
                    }
                    
                    # Calculate total cuts
                    if not iteration_data.empty and 'cut_TOT_gen_cut' in iteration_data.columns:
                        record['total_cuts'] = iteration_data['cut_TOT_gen_cut'].fillna(0).sum()
                    
                    all_results.append(record)
                    
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    continue
    
    if not all_results:
        st.error("No data loaded successfully")
        return pd.DataFrame()
    
    return pd.DataFrame(all_results)


def get_available_instances(df: pd.DataFrame, num_cust: int, condition: str) -> List[str]:
    """
    Get available instances for a given customer count and condition.
    """
    filtered = df[(df['num_cust'] == num_cust) & (df['condition'] == condition)]
    return sorted(filtered['instance'].unique())


def get_iteration_data(df: pd.DataFrame, instance: str, condition: str) -> Optional[pd.DataFrame]:
    """
    Get iteration-level data for a specific instance and condition.
    """
    filtered = df[(df['instance'] == instance) & (df['condition'] == condition)]
    
    if filtered.empty:
        return None
    
    # Get the first match (should be unique)
    iteration_data = filtered.iloc[0]['iteration_data']
    
    if isinstance(iteration_data, pd.DataFrame) and not iteration_data.empty:
        return iteration_data
    else:
        return None


def get_summary_stats(df: pd.DataFrame, instance: str, condition: str) -> Dict[str, float]:
    """
    Get summary statistics for an instance and condition.
    """
    filtered = df[(df['instance'] == instance) & (df['condition'] == condition)]
    
    if filtered.empty:
        return {}
    
    row = filtered.iloc[0]
    iteration_data = row['iteration_data']
    
    stats = {
        'Root LP': row.get('root_lp', np.nan),
        'Final LB': row.get('final_lb', np.nan),
        'ILP Objective': row.get('ilp_objective', np.nan),
        'ILP Time': row.get('ilp_time', np.nan),
        'Total LP Time': row.get('total_lp_time', np.nan),
        'Iterations': row.get('iterations', 0),
        'Total Cuts': row.get('total_cuts', 0)
    }
    
    # Add iteration-level statistics if available
    if isinstance(iteration_data, pd.DataFrame) and not iteration_data.empty:
        if 'lblp_lower' in iteration_data.columns:
            bounds = iteration_data['lblp_lower'].dropna()
            if not bounds.empty:
                stats['LB Improvement'] = bounds.iloc[-1] - bounds.iloc[0]
    
    return stats
