import pandas as pd
import pytest
from ispeo.simulator import Simulator
from ispeo.model import ModelParameters, State

@pytest.fixture
def default_params():
    return ModelParameters(
        mu_max=0.6, Ks=0.1, Kb=5.0, Ks_p=0.5,
        Y_xs=0.5, Y_ps=0.2, Y_bx=0.1,
        ms=0.05, q_bd=0.01, q_p=0.0,
        alpha=0.1, beta=0.02,
        Sf=500.0, ti=10.0,
        k1=0.01, b=0.005, k2=0.0
    )

@pytest.fixture
def default_init():
    return State(X=0.5, S=20.0, P=0.0, B=0.0, V=1.0)

def test_simulation_run(default_params, default_init):
    sim = Simulator()
    t_total = 20.0
    df = sim.solve(default_params, default_init, t_total, t_step=1.0)
    
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[-1]['time'] == pytest.approx(t_total)
    
    # Check if induction worked (Product should be 0 before ti, >0 after)
    df_before = df[df['time'] < default_params.ti]
    df_after = df[df['time'] > default_params.ti]
    
    assert (df_before['P'] == 0).all()
    assert (df_after['P'] > 0).all()

def test_short_simulation(default_params, default_init):
    sim = Simulator()
    # Run only until before induction
    t_total = 5.0 
    df = sim.solve(default_params, default_init, t_total)
    
    assert df.iloc[-1]['time'] == pytest.approx(t_total)
    assert (df['P'] == 0).all()
