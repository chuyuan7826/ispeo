import yaml
import pandas as pd
from pathlib import Path
from ispeo.model import ModelParameters, State

def load_parameters(path: str) -> ModelParameters:
    """Loads kinetic and operational parameters from a YAML file."""
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Handle empty file
    if data is None:
        data = {}

    # Handle both flat and nested structures for backward compatibility/robustness
    # Flatten if nested, otherwise assume flat
    flat_data = {}
    
    # Check for sections and merge if present
    if 'kinetic' in data:
        flat_data.update(data['kinetic'])
    if 'operation' in data:
        op = data['operation']
        flat_data.update(op)
        if 'feed' in op:
            flat_data.update(op['feed'])
    
    # If keys are at root level, update flat_data
    # This allows keys to be found even if they are at the root
    flat_data.update({k: v for k, v in data.items() if k not in ['kinetic', 'operation']})

    return ModelParameters(
        mu_max=float(flat_data.get('mu_max', float('nan'))),
        Ks=float(flat_data.get('Ks', float('nan'))),
        Kb=float(flat_data.get('Kb', float('nan'))),
        Ks_p=float(flat_data.get('Ks_p', float('nan'))),
        Y_xs=float(flat_data.get('Y_xs', float('nan'))),
        Y_ps=float(flat_data.get('Y_ps', float('nan'))),
        Y_bx=float(flat_data.get('Y_bx', float('nan'))),
        ms=float(flat_data.get('ms', float('nan'))),
        q_bd=float(flat_data.get('q_bd', float('nan'))),
        q_p=float(flat_data.get('q_p', 0.0)), # Default to 0 if missing, not NaN
        alpha=float(flat_data.get('alpha', float('nan'))),
        beta=float(flat_data.get('beta', float('nan'))),
        Sf=float(flat_data.get('Sf', float('nan'))),
        ti=float(flat_data.get('ti', float('nan'))),
        k1=float(flat_data.get('k1', float('nan'))),
        b=float(flat_data.get('b', float('nan'))),
        k2=float(flat_data.get('k2', float('nan')))
    )

from typing import Optional

def load_initial_conditions(path: str) -> Optional[State]:
    """Loads initial state variables from a YAML file."""
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        if data is None:
            return None
            
        return State(
            X=float(data['X']),
            S=float(data['S']),
            P=float(data['P']),
            B=float(data['B']),
            V=float(data['V'])
        )
    except (FileNotFoundError, KeyError, TypeError):
        return None

def load_data(path: str) -> pd.DataFrame:
    """Loads experimental data from a CSV file."""
    df = pd.read_csv(path)
    required_cols = {'time', 'X', 'S', 'P', 'B', 'V'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Data file must contain columns: {required_cols}")
    return df
