"""
Utility functions for the MASLD vs Healthy Ultrasound ML Results Viewer.
Handles data loading, validation, and demo data generation.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Dict
import json


def load_index_csv(results_root: Path) -> Optional[pd.DataFrame]:
    """Load index.csv from explainability_reports folder."""
    index_path = results_root / "explainability_reports" / "index.csv"
    if not index_path.exists():
        return None
    try:
        df = pd.read_csv(index_path)
        # Ensure case_id is string
        if 'case_id' in df.columns:
            df['case_id'] = df['case_id'].astype(str)
        return df
    except Exception as e:
        print(f"Error loading index.csv: {e}")
        return None


def load_case_mapping(results_root: Path) -> Optional[pd.DataFrame]:
    """Load case_mapping.csv from explainability_reports folder."""
    mapping_path = results_root / "explainability_reports" / "case_mapping.csv"
    if not mapping_path.exists():
        return None
    try:
        df = pd.read_csv(mapping_path)
        if 'case_id' in df.columns:
            df['case_id'] = df['case_id'].astype(str)
        return df
    except Exception as e:
        print(f"Error loading case_mapping.csv: {e}")
        return None


def get_explainability_image_path(results_root: Path, case_id: str) -> Optional[Path]:
    """Get path to explainability image for a case if it exists."""
    image_path = results_root / "explainability_reports" / f"{case_id}.png"
    if image_path.exists():
        return image_path
    return None


def load_metrics_summary(results_root: Path) -> Optional[pd.DataFrame]:
    """Load patient_metrics_summary.csv if it exists."""
    metrics_path = results_root / "patient_metrics_summary.csv"
    if not metrics_path.exists():
        return None
    try:
        return pd.read_csv(metrics_path)
    except Exception:
        return None


def load_run_config(results_root: Path) -> Optional[Dict]:
    """Load run_config.json if it exists."""
    config_path = results_root / "run_config.json"
    if not config_path.exists():
        return None
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def validate_results_structure(results_root: Path) -> Tuple[bool, list]:
    """
    Validate that required files exist in results_root.
    Returns (is_valid, missing_files).
    """
    required = [
        "explainability_reports/index.csv",
        "explainability_reports/case_mapping.csv"
    ]
    missing = []
    for req in required:
        path = results_root / req
        if not path.exists():
            missing.append(req)
    return len(missing) == 0, missing


def generate_demo_data() -> pd.DataFrame:
    """
    Generate synthetic demo data for UI preview.
    Clearly labeled as DEMO data, not real patient data.
    """
    np.random.seed(42)
    n_cases = 20
    
    # Generate demo case IDs
    case_ids = [f"Case-{i:02d}" for i in range(1, n_cases + 1)]
    
    # Generate synthetic data
    folds = np.random.choice([0, 1, 2], size=n_cases)
    y_true = np.random.choice([0, 1], size=n_cases, p=[0.1, 0.9])  # Mostly positive class
    p_calibrated = np.random.beta(2, 5, size=n_cases) if np.random.random() > 0.5 else np.random.beta(5, 2, size=n_cases)
    uncertainty_std = np.random.uniform(0.02, 0.15, size=n_cases)
    
    # Assign risk bands based on probability
    risk_bands = []
    for p in p_calibrated:
        if p < 0.3:
            risk_bands.append("LOW")
        elif p < 0.6:
            risk_bands.append("LOW-MOD")
        elif p < 0.8:
            risk_bands.append("MODERATE")
        else:
            risk_bands.append("HIGH")
    
    df = pd.DataFrame({
        'case_id': case_ids,
        'patient_id': [f"DEMO-{i}" for i in range(1, n_cases + 1)],  # Clearly demo
        'fold': folds,
        'y_true': y_true,
        'p_calibrated': p_calibrated,
        'uncertainty_std': uncertainty_std,
        'risk_band': risk_bands
    })
    
    return df


def filter_dataframe(
    df: pd.DataFrame,
    risk_bands: list = None,
    y_true_values: list = None,
    folds: list = None,
    prob_min: float = None,
    prob_max: float = None,
    uncert_min: float = None,
    uncert_max: float = None
) -> pd.DataFrame:
    """Filter dataframe based on various criteria."""
    filtered = df.copy()
    
    if risk_bands and len(risk_bands) > 0:
        filtered = filtered[filtered['risk_band'].isin(risk_bands)]
    
    if y_true_values is not None and len(y_true_values) > 0:
        filtered = filtered[filtered['y_true'].isin(y_true_values)]
    
    if folds and len(folds) > 0:
        filtered = filtered[filtered['fold'].isin(folds)]
    
    if prob_min is not None:
        filtered = filtered[filtered['p_calibrated'] >= prob_min]
    
    if prob_max is not None:
        filtered = filtered[filtered['p_calibrated'] <= prob_max]
    
    if uncert_min is not None:
        filtered = filtered[filtered['uncertainty_std'] >= uncert_min]
    
    if uncert_max is not None:
        filtered = filtered[filtered['uncertainty_std'] <= uncert_max]
    
    return filtered


def get_risk_band_color(risk_band: str) -> str:
    """Get color for risk band status chip."""
    colors = {
        "LOW": "#28a745",      # Green
        "LOW-MOD": "#ffc107",  # Yellow
        "MODERATE": "#fd7e14", # Orange
        "HIGH": "#dc3545"      # Red
    }
    return colors.get(risk_band, "#6c757d")


def compute_summary_metrics(df: pd.DataFrame) -> Dict:
    """Compute summary metrics from index dataframe."""
    if df.empty:
        return {}
    
    metrics = {
        'n_cases': len(df),
        'n_masld': int(df['y_true'].sum()) if 'y_true' in df.columns else 0,
        'n_healthy': int((df['y_true'] == 0).sum()) if 'y_true' in df.columns else 0,
        'mean_probability': float(df['p_calibrated'].mean()) if 'p_calibrated' in df.columns else 0.0,
        'mean_uncertainty': float(df['uncertainty_std'].mean()) if 'uncertainty_std' in df.columns else 0.0,
    }
    
    # Risk band distribution
    if 'risk_band' in df.columns:
        risk_counts = df['risk_band'].value_counts().to_dict()
        metrics['risk_band_dist'] = risk_counts
    
    return metrics

