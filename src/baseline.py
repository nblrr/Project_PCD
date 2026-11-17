"""Modul Segmentasi Foreground & Baseline Otsu
Penanggung Jawab: Anggota 2 (A2 - Preprocessing & Baseline Engineer)

Fungsi:
1. Segmentasi ambang global Otsu (1979).
2. Pembersihan morfologi (Opening, Closing, Hole Filling, Area Filtering).
3. Metode Baseline (B): Otsu + Connected Components tanpa Watershed.
"""

from typing import Tuple
import numpy as np
import scipy.ndimage as ndi
from skimage.filters import threshold_otsu
from skimage.measure import label
from skimage.morphology import disk, binary_opening, binary_closing


def otsu_thresholding(img: np.ndarray) -> Tuple[np.ndarray, float]:
    """Menghitung ambang batas Otsu dan menghasilkan mask biner awal.

    Args:
        img: Citra input float64 [0.0, 1.0].
    Returns:
        binary_mask: Array boolean/uint8 di mana True adalah objek sel.
        thresh_val: Nilai ambang t* optimal Otsu.
    """
    thresh_val = threshold_otsu(img)
    binary_mask = (img > thresh_val).astype(np.uint8)
    return binary_mask, float(thresh_val)


def morphological_cleanup(
    binary_mask: np.ndarray,
    opening_radius: int = 2,
    closing_radius: int = 2,
    min_area: int = 15,
) -> np.ndarray:
    """Membersihkan bintik derau kecil dan mengisi lubang intra-sel.

    Tahapan:
    1. Binary Opening (erosi -> dilasi) menghapus noise latar belakang.
    2. Binary Hole Filling menutup rongga dalam sel.
    3. Area filtering membuang komponen terlalu kecil.
    """
    selem = disk(opening_radius)
    cleaned = binary_opening(binary_mask, selem)
    cleaned = ndi.binary_fill_holes(cleaned).astype(np.uint8)

    # Area filtering menggunakan connected components
    labeled, num_features = ndi.label(cleaned)
    component_sizes = np.bincount(labeled.ravel())
    too_small = component_sizes < min_area
    too_small_mask = too_small[labeled]
    cleaned[too_small_mask] = 0

    return cleaned


def baseline_otsu_counting(
    img: np.ndarray,
    opening_radius: int = 2,
    min_area: int = 15,
) -> Tuple[int, np.ndarray, np.ndarray]:
    """Metode Baseline (B): Otsu Thresholding + Connected Components.

    Tanpa pemisahan watershed. Berfungsi sebagai kontrol pembanding untuk
    mengevaluasi keparahan under-counting pada sel yang saling menempel.

    Returns:
        cell_count: Estimasi jumlah sel.
        labeled_mask: Peta label komponen terhubung.
        binary_mask: Mask biner foreground hasil pembersihan.
    """
    binary_mask, _ = otsu_thresholding(img)
    cleaned_mask = morphological_cleanup(binary_mask, opening_radius=opening_radius, min_area=min_area)
    labeled_mask, num_cells = ndi.label(cleaned_mask)
    return int(num_cells), labeled_mask, cleaned_mask
