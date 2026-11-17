"""Modul Marker-Controlled Watershed Segmentation
Penanggung Jawab: Anggota 3 (A3 - Marker & Watershed Engineer)

Fungsi:
1. Rekonstruksi fungsi topografi permukaan (inversi EDT).
2. Simulasi perendaman (immersion) Vincent & Soille (1991).
3. Segmentasi objek sel individual dan penghitungan jumlah sel akhir.
"""

from typing import Tuple
import numpy as np
from skimage.segmentation import watershed


def apply_marker_controlled_watershed(
    distance_map: np.ndarray,
    markers: np.ndarray,
    mask: np.ndarray,
) -> Tuple[np.ndarray, int]:
    """Menjalankan segmentasi Marker-Controlled Watershed.

    Topografi dibentuk dari inversi peta jarak:
        surface = -distance_map
    di mana titik pusat sel menjadi lembah terdalam (basins) dan batas antar-sel
    menjadi punggungan (watershed ridges). Proses flooding dibatasi hanya
    di dalam wilayah mask foreground Otsu.

    Args:
        distance_map: Peta jarak Euclidean hasil EDT.
        markers: Array marker berlabel unik (1, 2, ..., M).
        mask: Mask biner constraint foreground (Otsu).
    Returns:
        labels: Peta segmentasi sel berlabel individual (0 = background).
        cell_count: Jumlah total sel yang berhasil disegmentasi.
    """
    # Inversi jarak sebagai surface topografi
    surface = -distance_map

    # Jalankan simulasi watershed
    labels = watershed(surface, markers=markers, mask=mask)

    # Hitung jumlah sel unik (mengabaikan background label 0)
    unique_labels = np.unique(labels)
    unique_cells = [lbl for lbl in unique_labels if lbl != 0]
    cell_count = len(unique_cells)

    return labels, cell_count
