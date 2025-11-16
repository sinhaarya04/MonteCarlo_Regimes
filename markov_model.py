"""
Markov chain model for regime switching simulation.
"""

import numpy as np
from typing import Optional


def simulate_regimes(
    T: int,
    transition_matrix: np.ndarray,
    initial_state: int = 0
) -> np.ndarray:
    """
    Simulate a sequence of regime states using a Markov chain.
    
    Parameters
    ----------
    T : int
        Number of time steps to simulate
    transition_matrix : np.ndarray
        Transition probability matrix (n_states x n_states).
        transition_matrix[i, j] = P(state_{t+1} = j | state_t = i)
    initial_state : int
        Initial regime state (default: 0 = Normal)
    
    Returns
    -------
    np.ndarray
        Array of regime indices of length T
    """
    n_states = transition_matrix.shape[0]
    regimes = np.zeros(T, dtype=int)
    regimes[0] = initial_state
    
    # Validate transition matrix (rows should sum to 1)
    row_sums = transition_matrix.sum(axis=1)
    if not np.allclose(row_sums, 1.0):
        raise ValueError("Transition matrix rows must sum to 1.0")
    
    # Simulate regime sequence
    for t in range(1, T):
        current_state = regimes[t - 1]
        # Sample next state from transition probabilities
        next_state = np.random.choice(
            n_states,
            p=transition_matrix[current_state, :]
        )
        regimes[t] = next_state
    
    return regimes


def create_default_transition_matrix(
    p_normal_to_stress: float = 0.05,
    p_stress_to_normal: float = 0.20,
    p_stress_to_crisis: float = 0.10,
    p_crisis_to_stress: float = 0.15
) -> np.ndarray:
    """
    Create a default 3-state transition matrix (Normal, Stress, Crisis).
    
    Parameters
    ----------
    p_normal_to_stress : float
        Probability of transitioning from Normal to Stress
    p_stress_to_normal : float
        Probability of transitioning from Stress to Normal
    p_stress_to_crisis : float
        Probability of transitioning from Stress to Crisis
    p_crisis_to_stress : float
        Probability of transitioning from Crisis to Stress
    
    Returns
    -------
    np.ndarray
        3x3 transition matrix
    """
    # Normal state transitions
    p_normal_stay = 1.0 - p_normal_to_stress
    normal_row = np.array([p_normal_stay, p_normal_to_stress, 0.0])
    
    # Stress state transitions
    p_stress_stay = 1.0 - p_stress_to_normal - p_stress_to_crisis
    stress_row = np.array([p_stress_to_normal, p_stress_stay, p_stress_to_crisis])
    
    # Crisis state transitions (tends to persist, then go back to Stress)
    p_crisis_stay = 1.0 - p_crisis_to_stress
    crisis_row = np.array([0.0, p_crisis_to_stress, p_crisis_stay])
    
    transition_matrix = np.array([normal_row, stress_row, crisis_row])
    
    return transition_matrix

