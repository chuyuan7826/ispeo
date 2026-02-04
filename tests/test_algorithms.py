import pandas as pd
import pytest
from ispeo.fitting import Fitter
from ispeo.strategy import StrategyOptimizer
from ispeo.simulator import Simulator
from ispeo.model import ModelParameters, State
from dataclasses import replace

@pytest.fixture
def base_setup():
    params = ModelParameters(
        mu_max=0.6, Ks=0.1, Kb=5.0, Ks_p=0.5,
        Y_xs=0.5, Y_ps=0.2, Y_bx=0.1,
        ms=0.05, q_bd=0.01, q_p=0.0,
        alpha=0.1, beta=0.02,
        Sf=500.0, ti=10.0,
        k1=0.01, b=0.005, k2=0.0
    )
    init = State(X=0.5, S=20.0, P=0.0, B=0.0, V=1.0)
    sim = Simulator()
    return params, init, sim

def test_fitting_recovery(base_setup):
    params, init, sim = base_setup
    
    # Generate synthetic data with known mu_max=0.6
    t_total = 10.0
    true_df = sim.solve(params, init, t_total)
    
    # Sample points for "experiment"
    exp_data = true_df.iloc[::10].copy() # Every 10th point
    
    # Perturb guess: mu_max=0.5
    fitter = Fitter(sim)
    param_init = {
        'mu_max': [0.5, 0.4, 0.8] # Guess, Min, Max
    }
    
    opt_params, cost = fitter.fit(exp_data, param_init, params, init)
    
    assert opt_params.mu_max == pytest.approx(0.6, rel=0.05)
    
    r2 = fitter.calculate_r2(exp_data, true_df)
    assert r2['X'] > 0.99

def test_strategy_optimization(base_setup):
    params, init, sim = base_setup
    
    optimizer = StrategyOptimizer(sim)
    
    # Optimize ti to maximize product
    bounds = {'ti': [5.0, 15.0]}
    
    # For test speed, use very loose tolerance/iters
    opt_params, val = optimizer.optimize(params, bounds, "max_product", init, t_total=20.0)
    
    assert 5.0 <= opt_params.ti <= 15.0
    assert val >= 0.0