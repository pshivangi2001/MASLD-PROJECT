"""
Data loading utilities for MASLD Results Viewer.
Handles file loading, validation, and demo data generation.
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
        if 'case_id' in df.columns:
            df['case_id'] = df['case_id'].astype(str)
        return df
    except Exception:
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
    except Exception:
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
    """Validate that required files exist. Returns (is_valid, missing_files)."""
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


def check_artifacts(results_root: Path) -> Dict[str, bool]:
    """Check which artifacts are available without exposing paths."""
    artifacts = {
        'index_csv': (results_root / "explainability_reports" / "index.csv").exists(),
        'case_mapping': (results_root / "explainability_reports" / "case_mapping.csv").exists(),
        'metrics_summary': (results_root / "patient_metrics_summary.csv").exists(),
        'run_config': (results_root / "run_config.json").exists(),
        'calibration_plots': (results_root / "calibration_plots").exists() and len(list((results_root / "calibration_plots").glob("*.png"))) > 0,
        'roc_curves': (results_root / "roc_curves_patient_level.png").exists(),
        'pr_curves': (results_root / "pr_curves_patient_level.png").exists(),
        'confusion_matrix': (results_root / "confusion_matrices_patient_level.png").exists(),
    }
    
    # Check for case images
    explain_dir = results_root / "explainability_reports"
    if explain_dir.exists():
        case_images = list(explain_dir.glob("Case-*.png"))
        artifacts['case_images'] = len(case_images) > 0
        artifacts['case_image_count'] = len(case_images)
    else:
        artifacts['case_images'] = False
        artifacts['case_image_count'] = 0
    
    return artifacts


def generate_demo_data() -> pd.DataFrame:
    """Generate synthetic demo data for UI preview."""
    np.random.seed(42)
    n_cases = 25
    
    case_ids = [f"Case-{i:02d}" for i in range(1, n_cases + 1)]
    folds = np.random.choice([0, 1, 2], size=n_cases)
    y_true = np.random.choice([0, 1], size=n_cases, p=[0.15, 0.85])
    p_calibrated = np.random.beta(3, 4, size=n_cases)
    uncertainty_std = np.random.uniform(0.02, 0.15, size=n_cases)
    
    risk_bands = []
    for p in p_calibrated:
        if p < 0.3:
            risk_bands.append("LOW")
        elif p < 0.5:
            risk_bands.append("LOW-MOD")
        elif p < 0.75:
            risk_bands.append("MODERATE")
        else:
            risk_bands.append("HIGH")
    
    df = pd.DataFrame({
        'case_id': case_ids,
        'patient_id': [f"DEMO-{i}" for i in range(1, n_cases + 1)],
        'fold': folds,
        'y_true': y_true,
        'p_calibrated': p_calibrated,
        'uncertainty_std': uncertainty_std,
        'risk_band': risk_bands
    })
    
    return df


def load_all_data(results_root: Path, demo_mode: bool = False):
    """Load all data with caching."""
    if demo_mode:
        return {
            'index_df': generate_demo_data(),
            'case_mapping': None,
            'metrics_summary': None,
            'run_config': None,
            'artifacts': {
                'index_csv': True,
                'case_mapping': True,
                'case_images': False,
                'case_image_count': 0,
                'metrics_summary': False,
                'run_config': False,
                'calibration_plots': False,
                'roc_curves': False,
                'pr_curves': False,
                'confusion_matrix': False,
            },
            'is_demo': True
        }
    
    index_df = load_index_csv(results_root)
    case_mapping = load_case_mapping(results_root)
    metrics_summary = load_metrics_summary(results_root)
    run_config = load_run_config(results_root)
    artifacts = check_artifacts(results_root)
    
    return {
        'index_df': index_df,
        'case_mapping': case_mapping,
        'metrics_summary': metrics_summary,
        'run_config': run_config,
        'artifacts': artifacts,
        'is_demo': False
    }


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

