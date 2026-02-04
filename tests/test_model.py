import numpy as np
import pytest
from ispeo.model import ModelParameters, feeding_rate, ode_system, specific_rates

@pytest.fixture
def default_params():
    return ModelParameters(
        mu_max=0.6, Ks=0.1, Kb=5.0, Ks_p=0.5,
        Y_xs=0.5, Y_ps=0.2, Y_bx=0.1,
        ms=0.05, q_bd=0.01, q_p=0.0, # q_p here is just a placeholder, calculated in func
        alpha=0.1, beta=0.02,
        Sf=500.0, ti=10.0,
        k1=0.01, b=0.005, k2=0.0
    )

def test_feeding_rate(default_params):
    p = default_params
    # t < ti
    assert feeding_rate(0, p) == p.b
    assert feeding_rate(5, p) == p.k1 * 5 + p.b
    
    # t = ti
    Fi = p.k1 * p.ti + p.b
    assert feeding_rate(10, p) == Fi
    
    # t > ti
    assert feeding_rate(12, p) == Fi + p.k2 * (12 - 10)

def test_rates_before_induction(default_params):
    p = default_params
    # High substrate, no product/byproduct
    y = np.array([1.0, 100.0, 0.0, 0.0, 1.0]) 
    
    mu, qP = specific_rates(5.0, y, p)
    
    # mu should be close to mu_max given high S and no B
    assert mu == pytest.approx(p.mu_max * (100/(0.1+100)), rel=1e-3)
    # qP must be 0 before induction
    assert qP == 0.0

def test_rates_after_induction(default_params):
    p = default_params
    y = np.array([1.0, 100.0, 0.0, 0.0, 1.0])
    
    mu, qP = specific_rates(15.0, y, p)
    
    # qP should follow Luedeking-Piret
    expected_qP = (p.alpha * mu + p.beta) * (100 / (0.5 + 100))
    assert qP == pytest.approx(expected_qP)
    assert qP > 0

def test_ode_derivatives(default_params):
    p = default_params
    # t=5 (growth), X=1, S=20, V=1
    y = np.array([1.0, 20.0, 0.0, 0.0, 1.0])
    
    dydt = ode_system(5.0, y, p)
    
    dX, dS, dP, dB, dV = dydt
    
    F = p.k1 * 5.0 + p.b
    assert dV == F
    assert dP == 0 - (F/1.0)*0 # qP*X - D*P, P=0, qP=0
