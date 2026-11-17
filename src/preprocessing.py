"""Modul Preprocessing Citra Mikroskopis
Penanggung Jawab: Anggota 2 (A2 - Preprocessing & Baseline Engineer)

Fungsi:
1. Normalisasi intensitas & contrast stretching.
2. Gaussian smoothing (low-pass filtering) untuk pereduksian derau.
"""

from typing import Tuple
import numpy as np
import scipy.ndimage as ndi


def contrast_stretching(
    img: np.ndarray,
    percentiles: Tuple[float, float] = (2.0, 98.0),
) -> np.ndarray:
    """Melakukan normalisasi intensitas berbasis persentil (contrast stretching).

    Args:
        img: Citra grayscale float64 dalam rentang [0.0, 1.0].
        percentiles: Tuple (p_low, p_high), default (2, 98).
    Returns:
        Citra ternormalisasi float64 [0.0, 1.0].
    """
    p_low, p_high = np.percentile(img, percentiles)
    if p_high - p_low == 0:
        return img
    stretched = np.clip((img - p_low) / (p_high - p_low), 0.0, 1.0)
    return stretched


def gaussian_smoothing(
    img: np.ndarray,
    sigma: float = 1.0,
) -> np.ndarray:
    """Menerapkan Gaussian filter 2D untuk mereduksi derau sebelum binerisasi.

    Rumus: G(x, y) = (1 / 2*pi*sigma^2) * exp(-(x^2 + y^2) / (2*sigma^2))
    
    Args:
        img: Citra input float64.
        sigma: Standar deviasi kernel Gaussian (dikalibrasi berdasarkan level blur F).
    Returns:
        Citra hasil smoothing float64.
    """
    return ndi.gaussian_filter(img, sigma=sigma)


def preprocess_pipeline(
    img: np.ndarray,
    sigma: float = 1.0,
    apply_stretching: bool = False,
) -> np.ndarray:
    """Pipeline terpadu preprocessing citra input."""
    processed = img.copy()
    if apply_stretching:
        processed = contrast_stretching(processed)
    processed = gaussian_smoothing(processed, sigma=sigma)
    return processed
