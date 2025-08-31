import numpy as np
import pandas as pd

def return_H_V() -> np.ndarray:
    """Create and return the user-provided redundancy matrix H_V (6×13) with columns sorted by value"""
    return np.array([
        [0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1],
        [0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1],
        [0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1],
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    ])


def return_H_U() -> np.ndarray:
    """Return the hard-coded H_U matrix (6×32) as linear combinations of H_V"""
    return np.array([
        [1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1],
        [0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1],
        [0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ])


def display_H_matrix(H_matrix: np.ndarray) -> None:
    """Display the H matrix in a formatted way using pandas"""
    print("H Matrix:")
    print("=" * 80)
    
    H_df = pd.DataFrame(
        H_matrix,
        index=[f'Row {i+1}' for i in range(6)],
        columns=[f'Col {i+1}' for i in range(45)]
    )
    print(H_df)
    print(f"\nStructure: Info part (Col 1-32) | Redundancy part (Col 33-45)")