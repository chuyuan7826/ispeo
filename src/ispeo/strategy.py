import numpy as np
from scipy.optimize import differential_evolution
from typing import Dict, List, Tuple
from ispeo.model import ModelParameters, State
from ispeo.simulator import Simulator
from dataclasses import replace

class StrategyOptimizer:
    def __init__(self, simulator: Simulator):
        self.sim = simulator

    def optimize(self, 
                 base_params: ModelParameters, 
                 bounds: Dict[str, List[float]], 
                 objective_type: str,
                 init_state: State,
                 t_total: float,
                 max_volume: float = 5.0) -> Tuple[ModelParameters, float]:
        
        param_names = list(bounds.keys())
        bounds_list = [(v[0], v[1]) for v in bounds.values()]
        
        def cost_func(x):
            updates = dict(zip(param_names, x))
            params = replace(base_params, **updates)
            
            try:
                df = self.sim.solve(params, init_state, t_total)
                
                # Volume Constraint Violation
                if df['V'].max() > max_volume:
                    return 1e6 # Penalty
                
                final_row = df.iloc[-1]
                
                if objective_type == "max_product":
                    return -final_row['P'] # Minimize negative product
                elif objective_type == "max_biomass":
                    return -final_row['X']
                else:
                    return 0.0
            except:
                return 1e6 # Penalty for failure

        result = differential_evolution(
            func=cost_func,
            bounds=bounds_list,
            strategy='best1bin',
            maxiter=100,
            popsize=15,
            tol=0.01,
            mutation=(0.5, 1),
            recombination=0.7
        )
        
        updates = dict(zip(param_names, result.x))
        return replace(base_params, **updates), -result.fun
