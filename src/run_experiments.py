"""Orkestrator Eksperimen & Pipeline Runner
Penanggung Jawab: Anggota 1 (A1 - Project Lead & Data Engineer)

Fungsi:
Menjalankan 4 skenario eksperimen secara batch deterministik,
mengumpulkan metrik ke results/metrics.csv, dan memicu pembuatan grafik.
"""

from pathlib import Path
import time
import numpy as np
import pandas as pd

from src.dataset import (
    load_metadata_csv,
    filter_stratified_subset,
    load_image,
    load_mask,
)
from src.preprocessing import preprocess_pipeline
from src.baseline import baseline_otsu_counting, otsu_thresholding, morphological_cleanup
from src.markers import (
    compute_distance_transform,
    marker_strategy_m1_local_maxima,
    marker_strategy_m2_h_maxima,
    marker_strategy_m3_morphological_erosion,
)
from src.watershed import apply_marker_controlled_watershed
from src.metrics import calculate_counting_metrics, calculate_spatial_metrics
from src.visualizer import (
    plot_method_comparison_bar,
    plot_density_analysis_line,
    plot_blur_degradation_line,
    plot_pipeline_stages,
)


def run_single_image_pipeline(
    image_path: Path | str,
    gt_count: int,
    sigma: float = 1.0,
    m1_r_min: int = 8,
    m2_h: float = 3.0,
    m3_n_iter: int = 6,
) -> dict:
    """Menjalankan Baseline dan ketiga strategi marker pada satu citra."""
    img = load_image(image_path, as_float=True)
    prep_img = preprocess_pipeline(img, sigma=sigma)

    # Foreground mask Otsu
    bin_mask, _ = otsu_thresholding(prep_img)
    cleaned_mask = morphological_cleanup(bin_mask)

    # 1. Baseline: Otsu + Connected Components
    count_base, _, _ = baseline_otsu_counting(prep_img)

    # EDT
    dist_map = compute_distance_transform(cleaned_mask)

    # 2. Strategi M1: Local Maxima
    markers_m1, _ = marker_strategy_m1_local_maxima(dist_map, min_distance=m1_r_min)
    labels_m1, count_m1 = apply_marker_controlled_watershed(dist_map, markers_m1, cleaned_mask)

    # 3. Strategi M2: h-Maxima
    markers_m2, _ = marker_strategy_m2_h_maxima(dist_map, h=m2_h)
    labels_m2, count_m2 = apply_marker_controlled_watershed(dist_map, markers_m2, cleaned_mask)

    # 4. Strategi M3: Morphological Erosion
    markers_m3, _ = marker_strategy_m3_morphological_erosion(cleaned_mask, n_iter=m3_n_iter)
    labels_m3, count_m3 = apply_marker_controlled_watershed(dist_map, markers_m3, cleaned_mask)

    return {
        "gt_count": gt_count,
        "pred_baseline": count_base,
        "pred_m1": count_m1,
        "pred_m2": count_m2,
        "pred_m3": count_m3,
        "raw_img": img,
        "dist_map": dist_map,
        "markers_m2": markers_m2,
        "labels_m2": labels_m2,
    }


def main():
    print("== [A1] Menjalankan Pipeline Eksperimen Cell Counting BBBC005 ==")
    # Skrip ini akan dihubungkan saat subset citra di data/ sudah siap
    print("Modul orkestrator siap digunakan.")


if __name__ == "__main__":
    main()
