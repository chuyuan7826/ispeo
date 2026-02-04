import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from ispeo.model import ModelParameters, State, ode_system, specific_rates

class Simulator:
    def solve(self, params: ModelParameters, init_state: State, t_total: float, t_step: float = 0.1) -> pd.DataFrame:
        """
        Runs the simulation in two stages to handle the discontinuity at t = ti.
        Stage 1: [0, ti] (Growth phase)
        Stage 2: [ti, t_total] (Production phase)
        """
        
        results = []
        
        # --- Stage 1: 0 to ti ---
        t_span1 = (0, min(params.ti, t_total))
        t_eval1 = np.arange(t_span1[0], t_span1[1], t_step)
        # Handle case where t_step doesn't exactly hit ti
        if len(t_eval1) > 0 and t_eval1[-1] < t_span1[1]:
             t_eval1 = np.append(t_eval1, t_span1[1])
        elif len(t_eval1) == 0: # Case where t_total is extremely small
             t_eval1 = np.array([0.0, min(params.ti, t_total)])

        sol1 = solve_ivp(
            fun=lambda t, y: ode_system(t, y, params),
            t_span=t_span1,
            y0=init_state.to_array(),
            t_eval=t_eval1,
            method='LSODA' 
        )
        
        if not sol1.success:
            raise RuntimeError(f"Integration failed in Stage 1: {sol1.message}")
            
        results.append(pd.DataFrame(sol1.y.T, index=sol1.t, columns=['X', 'S', 'P', 'B', 'V']))
        
        # If total time is less than induction time, we are done
        if t_total <= params.ti:
            final_df = results[0]
            final_df.index.name = 'time'
            return final_df.reset_index()

        # --- Stage 2: ti to t_total ---
        # Use final state of Stage 1 as initial condition for Stage 2
        y0_stage2 = sol1.y[:, -1]
        
        t_span2 = (params.ti, t_total)
        # Generate points, but ensure we don't exceed t_total
        t_eval2 = np.arange(t_span2[0], t_span2[1] + t_step/1000, t_step)
        t_eval2 = t_eval2[t_eval2 <= t_span2[1]] # Clamp to strictly <= t_total
        
        # Ensure we start exactly at ti if missing
        if len(t_eval2) == 0 or t_eval2[0] != params.ti:
             t_eval2 = np.insert(t_eval2, 0, params.ti)
        
        # Ensure we end at t_total if missing
        if t_eval2[-1] < t_span2[1]:
            t_eval2 = np.append(t_eval2, t_span2[1])

        sol2 = solve_ivp(
            fun=lambda t, y: ode_system(t, y, params),
            t_span=t_span2,
            y0=y0_stage2,
            t_eval=t_eval2,
            method='LSODA'
        )

        if not sol2.success:
            raise RuntimeError(f"Integration failed in Stage 2: {sol2.message}")

        results.append(pd.DataFrame(sol2.y.T, index=sol2.t, columns=['X', 'S', 'P', 'B', 'V']))

        # Combine and cleanup
        full_df = pd.concat(results)
        # Remove duplicate index (at ti) if any
        full_df = full_df[~full_df.index.duplicated(keep='first')]
        full_df.index.name = 'time'
        
        return full_df.reset_index()

    def calculate_metrics(self, df: pd.DataFrame, params: ModelParameters) -> pd.DataFrame:
        """Adds specific rates (mu, qP) to the results DataFrame."""
        mu_list = []
        qP_list = []
        
        for idx, row in df.iterrows():
            t = row['time']
            y = row[['X', 'S', 'P', 'B', 'V']].values
            mu, qP = specific_rates(t, y, params)
            mu_list.append(mu)
            qP_list.append(qP)
            
        df['mu'] = mu_list
        df['qP'] = qP_list
        return df
