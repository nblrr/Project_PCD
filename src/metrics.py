"""Modul Evaluasi Kuantitatif & Metrik Akurasi
Penanggung Jawab: Anggota 4 (A4 - Evaluation & Visualization Engineer)

Fungsi:
1. Menghitung metrik akurasi penghitungan sel: MAE, MAPE, RMSE, Pearson r.
2. Menghitung rasio over-segmentasi (OSR) dan under-segmentasi (USR).
3. Menghitung metrik kualitas segmentasi spasial: IoU (Jaccard) & Dice (F1-Score).
"""

from typing import Dict, List, Tuple
import numpy as np
from scipy.stats import pearsonr


def calculate_counting_metrics(
    y_true: List[int] | np.ndarray,
    y_pred: List[int] | np.ndarray,
) -> Dict[str, float]:
    """Menghitung metrik penghitungan sel global: MAE, MAPE, RMSE, dan Pearson r."""
    y_t = np.array(y_true, dtype=np.float64)
    y_p = np.array(y_pred, dtype=np.float64)
    n = len(y_t)

    if n == 0:
        return {"mae": 0.0, "mape": 0.0, "rmse": 0.0, "r": 0.0}

    # Error absolut & kuadrat
    abs_errors = np.abs(y_t - y_p)
    mae = float(np.mean(abs_errors))
    rmse = float(np.sqrt(np.mean((y_t - y_p) ** 2)))

    # MAPE (hindari pembagian nol)
    safe_yt = np.where(y_t == 0, 1e-6, y_t)
    mape = float(np.mean(abs_errors / safe_yt) * 100.0)

    # Pearson correlation r
    if np.all(y_t == y_t[0]) or np.all(y_p == y_p[0]):
        r_val = 0.0
    else:
        r_val, _ = pearsonr(y_t, y_p)
        r_val = float(r_val)

    # Over & Under segmentation ratios
    over_count = np.sum(np.maximum(0, y_p - y_t))
    under_count = np.sum(np.maximum(0, y_t - y_p))
    total_true = np.sum(y_t)
    osr = float(over_count / total_true) if total_true > 0 else 0.0
    usr = float(under_count / total_true) if total_true > 0 else 0.0

    return {
        "mae": mae,
        "mape": mape,
        "rmse": rmse,
        "pearson_r": r_val,
        "osr": osr,
        "usr": usr,
    }


def calculate_spatial_metrics(
    pred_mask: np.ndarray,
    gt_mask: np.ndarray,
) -> Dict[str, float]:
    """Menghitung metrik kesesuaian biner foreground: IoU dan Dice Coefficient.

    Formula:
        IoU  = |A n B| / |A u B|
        Dice = 2 * |A n B| / (|A| + |B|)
    """
    pred_bin = (pred_mask > 0).astype(bool)
    gt_bin = (gt_mask > 0).astype(bool)

    intersection = np.logical_and(pred_bin, gt_bin).sum()
    union = np.logical_or(pred_bin, gt_bin).sum()
    pred_sum = pred_bin.sum()
    gt_sum = gt_bin.sum()

    iou = float(intersection / union) if union > 0 else 1.0
    dice = float((2.0 * intersection) / (pred_sum + gt_sum)) if (pred_sum + gt_sum) > 0 else 1.0

    return {
        "iou": iou,
        "dice": dice,
    }
