from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class ModelParameters:
    # Kinetic parameters
    mu_max: float
    Ks: float
    Kb: float
    Ks_p: float
    Y_xs: float
    Y_ps: float
    Y_bx: float
    ms: float
    q_bd: float
    q_p: float
    alpha: float
    beta: float

    # Operational parameters
    Sf: float
    ti: float
    k1: float
    b: float
    k2: float

@dataclass(frozen=True)
class State:
    X: float
    S: float
    P: float
    B: float
    V: float

    def to_array(self) -> np.ndarray:
        return np.array([self.X, self.S, self.P, self.B, self.V])

    @classmethod
    def from_array(cls, y: np.ndarray):
        return cls(X=y[0], S=y[1], P=y[2], B=y[3], V=y[4])

def feeding_rate(t: float, params: ModelParameters) -> float:
    """Calculates feed rate F(t) [L/h] based on piecewise linear policy."""
    if t < params.ti:
        return params.k1 * t + params.b
    else:
        # F_i is the feed rate at the moment of induction
        Fi = params.k1 * params.ti + params.b
        return Fi + params.k2 * (t - params.ti)

def specific_rates(t: float, y: np.ndarray, params: ModelParameters) -> tuple[float, float]:
    """Calculates specific growth rate (mu) and product synthesis rate (qP)."""
    S = max(0.0, y[1]) # Prevent negative concentrations in rate calc
    B = max(0.0, y[3])

    # Growth rate mu with substrate limitation and product inhibition
    # Note: Using B (acetate) for inhibition term 1/(1 + B/Kb)
    mu = params.mu_max * (S / (params.Ks + S)) * (1.0 / (1.0 + B / params.Kb))

    # Product synthesis rate qP
    if t < params.ti:
        qP = 0.0
    else:
        # Luedeking-Piret kinetics
        qP = (params.alpha * mu + params.beta) * (S / (params.Ks_p + S))
        
    return mu, qP

def ode_system(t: float, y: np.ndarray, params: ModelParameters) -> np.ndarray:
    """
    Defines the system of ODEs for fed-batch fermentation.
    y = [X, S, P, B, V]
    """
    # Clip negative concentrations for physical realism in derivative calculation
    # (Though solver handles state, rates depend on physical values)
    X = max(0.0, y[0])
    S = max(0.0, y[1])
    P = max(0.0, y[2])
    B = max(0.0, y[3])
    V = max(1e-6, y[4]) # Volume cannot be zero

    F = feeding_rate(t, params)
    D = F / V # Dilution rate

    mu, qP = specific_rates(t, y, params)

    # dX/dt = mu*X - D*X
    dX = (mu - D) * X

    # dS/dt = D*(Sf - S) - qS*X
    # qS = mu/Yxs + ms + qP/Yps
    qS = (mu / params.Y_xs) + params.ms + (qP / params.Y_ps)
    dS = D * (params.Sf - S) - qS * X

    # dP/dt = qP*X - D*P
    dP = qP * X - D * P

    # dB/dt = qB*X - D*B
    # qB = Ybx*mu - q_bd (net production rate)
    dB = (params.Y_bx * mu - params.q_bd) * X - D * B

    # dV/dt = F
    dV = F

    return np.array([dX, dS, dP, dB, dV])
