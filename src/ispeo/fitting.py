import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from typing import Dict, List, Tuple
from ispeo.model import ModelParameters, State
from ispeo.simulator import Simulator
from dataclasses import replace, asdict

class Fitter:
    def __init__(self, simulator: Simulator):
        self.sim = simulator

    def _update_params(self, base_params: ModelParameters, param_names: List[str], param_values: np.ndarray) -> ModelParameters:
        """Helper to create a new ModelParameters object with updated values."""
        updates = dict(zip(param_names, param_values))
        return replace(base_params, **updates)

    def objective(self, 
                  current_values: np.ndarray, 
                  param_names: List[str], 
                  base_params: ModelParameters, 
                  init_state: State, 
                  exp_data: pd.DataFrame) -> np.ndarray:
        
        # Update parameters
        current_params = self._update_params(base_params, param_names, current_values)
        
        # Run simulation
        t_total = exp_data['time'].max()
        try:
            sim_df = self.sim.solve(current_params, init_state, t_total)
        except RuntimeError:
            # If simulation fails (unstable parameters), return large residuals
            return np.ones(len(exp_data) * 5) * 1e6

        # Interpolate simulation results to experimental time points
        # We need to calculate residuals for X, S, P, B, V
        residuals = []
        for col in ['X', 'S', 'P', 'B', 'V']:
            sim_vals = np.interp(exp_data['time'], sim_df['time'], sim_df[col])
            # Weighting: Normalize by data range or max to balance contributions
            # Simple approach: (sim - exp)
            res = sim_vals - exp_data[col].values
            residuals.extend(res)
            
        return np.array(residuals)

    def fit(self, 
            exp_data: pd.DataFrame, 
            param_init: Dict[str, List[float]], 
            base_params: ModelParameters,
            init_state: State) -> Tuple[ModelParameters, float]:
        
        param_names = list(param_init.keys())
        x0 = [v[0] for v in param_init.values()]
        lb = [v[1] for v in param_init.values()]
        ub = [v[2] for v in param_init.values()]
        
        # Validate that we have a complete parameter set
        test_params = self._update_params(base_params, param_names, np.array(x0))
        params_dict = asdict(test_params)
        missing_params = [k for k, v in params_dict.items() if np.isnan(v)]
        
        if missing_params:
            raise ValueError(f"The following parameters are undefined (NaN): {missing_params}. "
                             f"Please provide them in 'fixed-param' or 'param-init'.")

        # Handle scaling: avoid 0 scale for parameters starting at 0
        x_scale = [val if val != 0 else 1.0 for val in x0]

        res = least_squares(
            fun=self.objective,
            x0=x0,
            bounds=(lb, ub),
            x_scale=x_scale,  # Scaling is CRITICAL for mixed-magnitude parameters
            args=(param_names, base_params, init_state, exp_data),
            method='trf',
            verbose=1,
            max_nfev=5000 # Increased limit for better convergence on complex landscapes
        )
        
        optimized_params = self._update_params(base_params, param_names, res.x)
        return optimized_params, res.cost

    def calculate_r2(self, exp_data: pd.DataFrame, sim_df: pd.DataFrame) -> Dict[str, float]:
        """Calculates R^2 for each state variable."""
        r2_scores = {}
        for col in ['X', 'S', 'P', 'B', 'V']:
            y_true = exp_data[col].values
            y_pred = np.interp(exp_data['time'], sim_df['time'], sim_df[col])
            
            ss_res = np.sum((y_true - y_pred) ** 2)
            ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
            
            if ss_tot == 0:
                r2 = 1.0 if ss_res == 0 else 0.0
            else:
                r2 = 1 - (ss_res / ss_tot)
            r2_scores[col] = r2
            
        return r2_scores
