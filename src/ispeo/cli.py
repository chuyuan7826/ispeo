import click
import pandas as pd
import yaml
from pathlib import Path
from ispeo.io import load_parameters, load_initial_conditions, load_data
from ispeo.simulator import Simulator
from ispeo.fitting import Fitter
from ispeo.strategy import StrategyOptimizer
import sys

@click.group()
def cli():
    """ispeo — simulate, fit, and optimize squalene production in E. coli"""
    pass

import os

@cli.command()
@click.option('--param', required=True, type=click.Path(exists=True), help='YAML file containing kinetic and operational parameters.')
@click.option('--init', required=True, type=click.Path(exists=True), help='YAML file containing initial state variables.')
@click.option('--time', required=True, type=float, help='Total simulation time in hours.')
@click.option('--step', default=0.1, help='Time step for reporting output (default: 0.1h).')
@click.option('--output', default='.', type=click.Path(), help='Directory to save the simulation results.')
@click.option('--plot', is_flag=True, help='Flag to generate and save a visualization of the state variables.')
def simulate(param, init, time, step, output, plot):
    """Run a forward simulation of the fermentation process."""
    try:
        os.makedirs(output, exist_ok=True)
        params = load_parameters(param)
        init_state = load_initial_conditions(init)
        
        sim = Simulator()
        df = sim.solve(params, init_state, time, step)
        
        # Add derived metrics (mu, qP)
        df = sim.calculate_metrics(df, params)
        
        csv_path = Path(output) / 'simulation.csv'
        df.to_csv(csv_path, index=False)
        click.echo(f"Simulation completed. Results saved to {csv_path}")
        
        if plot:
            from ispeo.visualization import plot_simulation
            plot_path = Path(output) / 'simulation.png'
            plot_simulation(df, str(plot_path))
            click.echo(f"Plot saved to {plot_path}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--data', required=True, type=click.Path(exists=True), help='CSV file containing experimental time-course data.')
@click.option('--param-init', required=True, type=click.Path(exists=True), help='YAML file with initial guesses and bounds.')
@click.option('--fixed-param', required=True, type=click.Path(exists=True), help='YAML file with fixed parameters.')
@click.option('--output', default='.', type=click.Path(), help='Directory to save the fitted parameters.')
@click.option('--plot', is_flag=True, help='Flag to show the fit quality.')
def fit(data, param_init, fixed_param, output, plot):
    """Estimate kinetic parameters by minimizing error against experimental data."""
    try:
        os.makedirs(output, exist_ok=True)
        exp_data = load_data(data)
        base_params = load_parameters(fixed_param)
        
        # Assume first row of data is initial condition
        # (Or we could require an init file, but data usually implies it)
        init_state = load_initial_conditions(fixed_param.replace('params.yml', 'init.yml')) 
        # Fallback: simplistic extraction from first row of data
        if init_state is None:
             row0 = exp_data.iloc[0]
             from ispeo.model import State
             init_state = State(X=row0['X'], S=row0['S'], P=row0['P'], B=row0['B'], V=row0['V'])

        with open(param_init, 'r') as f:
            p_init = yaml.safe_load(f)

        sim = Simulator()
        fitter = Fitter(sim)
        
        click.echo("Starting parameter estimation...")
        opt_params, cost = fitter.fit(exp_data, p_init, base_params, init_state)
        
        # Save results
        from dataclasses import asdict
        import numpy as np
        
        # Convert NumPy types to native Python floats for clean YAML output
        params_dict = asdict(opt_params)
        clean_params = {k: float(v) if isinstance(v, (np.floating, float)) else v for k, v in params_dict.items()}
        
        out_path = Path(output) / 'fitted_params.yml'
        with open(out_path, 'w') as f:
            yaml.dump(clean_params, f, default_flow_style=False)
        
        click.echo(f"Optimization complete. Cost: {cost:.4f}")
        click.echo(f"Parameters saved to {out_path}")
        
        # R^2 Evaluation
        t_total = exp_data['time'].max()
        sim_df = sim.solve(opt_params, init_state, t_total)
        r2 = fitter.calculate_r2(exp_data, sim_df)
        click.echo("\nFit Quality (R^2):")
        for k, v in r2.items():
            click.echo(f"  {k}: {v:.4f}")

        if plot:
            from ispeo.visualization import plot_simulation
            plot_path = Path(output) / 'fit_plot.png'
            plot_simulation(sim_df, str(plot_path), exp_data=exp_data)
            click.echo(f"Fit plot saved to {plot_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        # sys.exit(1) # Debugging

@cli.command()
@click.option('--param', required=True, type=click.Path(exists=True), help='Baseline parameters.')
@click.option('--objective', required=True, type=click.Choice(['max_product', 'max_biomass']), help='Target objective.')
@click.option('--bounds', required=True, type=click.Path(exists=True), help='Search ranges.')
@click.option('--opt-ti', is_flag=True, help='Optimize induction time.')
@click.option('--opt-k1', is_flag=True, help='Optimize growth feed slope.')
@click.option('--opt-k2', is_flag=True, help='Optimize production feed slope.')
@click.option('--opt-b', is_flag=True, help='Optimize initial feed rate.')
@click.option('--opt-sf', is_flag=True, help='Optimize feed substrate concentration.')
@click.option('--max-volume', default=5.0, help='Maximum working volume constraint [L].')
@click.option('--output', default='.', type=click.Path(), help='Directory to save optimization results.')
@click.option('--plot', is_flag=True, help='Flag to visualize the comparison between baseline and optimized strategies.')
def optimize(param, objective, bounds, opt_ti, opt_k1, opt_k2, opt_b, opt_sf, max_volume, output, plot):
    """Find optimal operational strategy."""
    try:
        os.makedirs(output, exist_ok=True)
        base_params = load_parameters(param)
        # Assuming init.yml is in same dir or standard location
        init_file = Path(param).parent / 'init.yml'
        init_state = load_initial_conditions(str(init_file))
        
        with open(bounds, 'r') as f:
            all_bounds = yaml.safe_load(f)
            
        # Select active bounds based on flags
        active_bounds = {}
        if opt_ti and 'ti' in all_bounds: active_bounds['ti'] = all_bounds['ti']
        if opt_k1 and 'k1' in all_bounds: active_bounds['k1'] = all_bounds['k1']
        if opt_k2 and 'k2' in all_bounds: active_bounds['k2'] = all_bounds['k2']
        if opt_b and 'b' in all_bounds: active_bounds['b'] = all_bounds['b']
        if opt_sf and 'Sf' in all_bounds: active_bounds['Sf'] = all_bounds['Sf']
        
        if not active_bounds:
            click.echo("No parameters selected for optimization! Use flags like --opt-ti.")
            return

        sim = Simulator()
        opt = StrategyOptimizer(sim)
        
        click.echo(f"Optimizing {objective} using parameters: {list(active_bounds.keys())}...")
        
        # Hardcoded t_total for optimization horizon, or could be arg
        # Using a standard 48h for now as typical fed-batch
        t_horizon = 48.0
        
        best_params, best_val = opt.optimize(base_params, active_bounds, objective, init_state, t_horizon, max_volume)
        
        summary = f"""
Optimization Results:
Objective: {objective}
Best Value: {best_val:.4f}
Optimized Parameters:
"""
        for k in active_bounds.keys():
            val = getattr(best_params, k)
            summary += f"  {k}: {val:.4f}\n"
            
        click.echo(summary)
        
        summary_path = Path(output) / 'optimization_summary.txt'
        with open(summary_path, 'w') as f:
            f.write(summary)
            
        # Also save the full optimized parameters for easy reuse
        from dataclasses import asdict
        import numpy as np
        
        params_dict = asdict(best_params)
        clean_params = {k: float(v) if isinstance(v, (np.floating, float)) else v for k, v in params_dict.items()}
        
        params_path = Path(output) / 'optimized_params.yml'
        with open(params_path, 'w') as f:
            yaml.dump(clean_params, f, default_flow_style=False)
            
        click.echo(f"Results saved to {summary_path}")
        click.echo(f"Optimized parameters saved to {params_path}")

        if plot:
            from ispeo.visualization import plot_optimization_comparison
            
            # Run Baseline Simulation
            click.echo("Running baseline simulation for comparison...")
            base_df = sim.solve(base_params, init_state, t_horizon)
            
            # Run Optimized Simulation
            click.echo("Running optimized simulation...")
            opt_df = sim.solve(best_params, init_state, t_horizon)
            
            plot_path = Path(output) / 'optimization_comparison.png'
            plot_optimization_comparison(base_df, opt_df, str(plot_path))
            click.echo(f"Comparison plot saved to {plot_path}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
