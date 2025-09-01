#!/usr/bin/env python3
"""
Hu Matrix Generator
==================

This module generates Hu matrix from Hv matrix with the property:
- Every column of Hu lies in the span of the columns of Hv

This means each column of Hu can be expressed as a linear combination of Hv columns.

Usage:
    python hu_generator.py
    or import and use generate_hu_from_hv(Hv)
"""

import numpy as np
import sys


def is_in_span(vector, basis_matrix):
    """
    Check if vector lies in the span of basis_matrix columns.
    
    Args:
        vector: Target vector to check
        basis_matrix: Matrix whose columns form the basis
        
    Returns:
        bool: True if vector is in span, False otherwise
    """
    if basis_matrix.size == 0:
        return False
    
    # Try to solve: basis_matrix * x = vector
    try:
        solution = np.linalg.lstsq(basis_matrix, vector, rcond=None)[0]
        # Check if the solution is exact (within numerical precision)
        reconstructed = basis_matrix @ solution
        return np.allclose(reconstructed, vector, atol=1e-10)
    except np.linalg.LinAlgError:
        return False


def generate_linear_combination(basis_matrix, target_vector=None):
    """
    Generate a vector that lies in the span of basis_matrix columns.
    
    Args:
        basis_matrix: Matrix whose columns form the basis
        target_vector: Optional target vector to approximate
        
    Returns:
        np.ndarray: Vector in the span of basis_matrix
    """
    if basis_matrix.size == 0:
        return np.zeros(6, dtype=int)
    
    # Generate random coefficients for linear combination
    n_cols = basis_matrix.shape[1]
    coeffs = np.random.randint(0, 2, n_cols)
    
    # Compute linear combination
    result = (basis_matrix @ coeffs) % 2
    
    return result


def generate_hu_from_hv(Hv, hu_cols=32, seed=None):
    """
    Generate Hu matrix from Hv matrix.
    
    Property: Every column of Hu lies in the span of the columns of Hv.
    
    Args:
        Hv: Hv matrix (6x13)
        hu_cols: Number of columns for Hu matrix (default: 6)
        seed: Random seed for reproducibility
        
    Returns:
        tuple: (Hu, success) where Hu is the generated matrix and success is bool
    """
    if seed is not None:
        np.random.seed(seed)
    
    print(f"Generating Hu matrix ({Hv.shape[0]}x{hu_cols}) from Hv matrix ({Hv.shape[0]}x{Hv.shape[1]})...")
    print("Property: Every column of Hu lies in the span of Hv columns")
    
    # Initialize Hu matrix
    Hu = np.zeros((Hv.shape[0], hu_cols), dtype=int)
    
    for col_idx in range(hu_cols):        
        max_attempts = 1000
        for attempt in range(max_attempts):
            # Generate a vector in the span of Hv
            candidate = generate_linear_combination(Hv)
            
            # Skip zero vector
            if np.all(candidate == 0):
                continue
            
            # Check if this vector is already in Hu (avoid duplicates within Hu)
            is_duplicate_in_hu = False
            for existing_col in range(col_idx):
                if np.array_equal(candidate, Hu[:, existing_col]):
                    is_duplicate_in_hu = True
                    break
            
            # Check if this vector already exists in Hv (avoid duplicates with Hv)
            is_duplicate_in_hv = False
            for hv_col in range(Hv.shape[1]):
                if np.array_equal(candidate, Hv[:, hv_col]):
                    is_duplicate_in_hv = True
                    break
            
            if not is_duplicate_in_hu and not is_duplicate_in_hv:
                # Verify it's in the span of Hv
                if is_in_span(candidate, Hv):
                    Hu[:, col_idx] = candidate
                    break
                else:
                    print(f"    Warning: Generated vector not in span of Hv")
        
        if attempt == max_attempts - 1:
            print(f"    Failed to generate column {col_idx + 1} after {max_attempts} attempts")
            return None, False
    
    return Hu, True


def validate_hu_properties(Hu, Hv):
    """
    Validate that Hu matrix satisfies all required properties.
    
    Args:
        Hu: Hu matrix to validate
        Hv: Hv matrix for reference
        
    Returns:
        bool: True if all properties satisfied, False otherwise
    """
    print("\nValidating Hu matrix properties...")
    
    # Check dimensions
    if Hu.shape[0] != Hv.shape[0]:
        print(f"✗ Row dimension mismatch: Hu has {Hu.shape[0]} rows, Hv has {Hv.shape[0]}")
        return False
    print(f"✓ Dimensions correct: {Hu.shape}")
    
    # Check that all columns are in span of Hv
    all_in_span = True
    for col_idx in range(Hu.shape[1]):
        if not is_in_span(Hu[:, col_idx], Hv):
            print(f"✗ Column {col_idx + 1} of Hu is not in span of Hv")
            all_in_span = False
    
    if all_in_span:
        print("✓ All columns of Hu are in span of Hv")
    else:
        print("✗ Some columns of Hu are not in span of Hv")
        return False
    
    # Check for duplicates between Hu and Hv
    has_duplicates_with_hv = False
    for hu_col_idx in range(Hu.shape[1]):
        for hv_col_idx in range(Hv.shape[1]):
            if np.array_equal(Hu[:, hu_col_idx], Hv[:, hv_col_idx]):
                print(f"✗ Column {hu_col_idx + 1} of Hu is identical to column {hv_col_idx + 1} of Hv")
                has_duplicates_with_hv = True
    
    if not has_duplicates_with_hv:
        print("✓ No duplicate columns between Hu and Hv")
    else:
        print("✗ Found duplicate columns between Hu and Hv")
        return False
    
    return True


def generate_hu_entry_point(Hv, hu_cols=32, seed=None, output_dir=None, verbose=True):
    """
    Entry point function for Hu matrix generation.
    
    Args:
        Hv: Hv matrix
        hu_cols: Number of columns for Hu matrix
        seed: Random seed for reproducibility
        output_dir: Directory to save output files
        verbose: Whether to print progress information
        
    Returns:
        Hu matrix if successful, None if failed
    """
    if verbose:
        print("="*60)
        print("HU MATRIX GENERATION")
        print("="*60)
    
    try:
        # Generate Hu matrix
        Hu, success = generate_hu_from_hv(Hv, hu_cols=hu_cols, seed=seed)
        
        if success and Hu is not None:
            # Validate properties
            if validate_hu_properties(Hu, Hv):
                if verbose:
                    print("\n" + "="*50)
                    print("GENERATED HU MATRIX")
                    print("="*50)
                    print(f"Hu matrix ({Hu.shape[0]}x{Hu.shape[1]}):")
                    print(Hu)
                    print(f"\nMatrix properties:")
                    print(f"- Rank of Hu: {np.linalg.matrix_rank(Hu)}")
                    print(f"- All columns in span of Hv: ✓")
                
                return Hu
            else:
                if verbose:
                    print("✗ Hu matrix validation failed!")
                return None
        else:
            if verbose:
                print("✗ Hu matrix generation failed!")
            return None
            
    except Exception as e:
        if verbose:
            print(f"✗ Error generating Hu matrix: {e}")
        return None
