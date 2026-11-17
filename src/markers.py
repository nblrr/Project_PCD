"""Modul Strategi Pembentukan Marker
Penanggung Jawab: Anggota 3 (A3 - Marker & Watershed Engineer)

Fungsi:
1. Menghitung Euclidean Distance Transform (EDT).
2. Strategi M1: Local Maxima Peak Finding (parameter: r_min).
3. Strategi M2: h-Maxima Transform / Peak Suppression (parameter: h).
4. Strategi M3: Distance Thresholding & Morphological Erosion (parameter: n_iter).
"""

from typing import Tuple
import numpy as np
import scipy.ndimage as ndi
from skimage.feature import peak_local_max
from skimage.morphology import h_maxima


def compute_distance_transform(binary_mask: np.ndarray) -> np.ndarray:
    """Menghitung Euclidean Distance Transform (EDT) pada foreground mask.

    Rumus: D(p) = min_{q in Background} ||p - q||_2
    Nilai puncak lokal merepresentasikan pusat massa/geometri sel.
    """
    return ndi.distance_transform_edt(binary_mask)


def marker_strategy_m1_local_maxima(
    distance_map: np.ndarray,
    min_distance: int = 8,
    threshold_rel: float = 0.2,
) -> Tuple[np.ndarray, int]:
    """Strategi M1: Deteksi puncak lokal langsung pada peta jarak EDT.

    Args:
        distance_map: Peta jarak Euclidean.
        min_distance: Radius supresi antarpuncak (divariasikan {5, 8, 12}).
        threshold_rel: Ambang batas relatif terhadap nilai maksimum EDT.
    Returns:
        markers: Array integer berisi label unik untuk setiap benih sel.
        num_markers: Jumlah marker yang terdeteksi.
    """
    coordinates = peak_local_max(
        distance_map,
        min_distance=min_distance,
        threshold_rel=threshold_rel,
    )
    markers = np.zeros(distance_map.shape, dtype=np.int32)
    for idx, (r, c) in enumerate(coordinates, start=1):
        markers[r, c] = idx
    return markers, len(coordinates)


def marker_strategy_m2_h_maxima(
    distance_map: np.ndarray,
    h: float = 3.0,
) -> Tuple[np.ndarray, int]:
    """Strategi M2: h-Maxima Transform untuk menekan false peaks lokal.

    HMAX_h(f) = f - R^delta_f(f - h), di mana semua puncak lokal dengan kedalaman
    kurang dari h ditekan secara morfologis menggunakan rekonstruksi geodesik.

    Args:
        distance_map: Peta jarak Euclidean.
        h: Ketinggian supresi puncak (divariasikan {1, 3, 5}).
    Returns:
        markers: Array integer berlabel unik.
        num_markers: Jumlah marker terdeteksi.
    """
    h_max = h_maxima(distance_map, h=h)
    markers, num_markers = ndi.label(h_max)
    return markers, int(num_markers)


def marker_strategy_m3_morphological_erosion(
    binary_mask: np.ndarray,
    n_iter: int = 6,
) -> Tuple[np.ndarray, int]:
    """Strategi M3: Erosi morfologi biner berulang untuk memisahkan jembatan sel.

    Formula: (A (-) B)(x) = {p : B_p subseteq A}, diulang n_iter kali.

    Args:
        binary_mask: Mask biner foreground.
        n_iter: Jumlah iterasi erosi (divariasikan {3, 6, 10}).
    Returns:
        markers: Array integer berlabel unik hasil erosi.
        num_markers: Jumlah marker terdeteksi.
    """
    eroded = ndi.binary_erosion(binary_mask, iterations=n_iter)
    markers, num_markers = ndi.label(eroded)
    return markers, int(num_markers)
