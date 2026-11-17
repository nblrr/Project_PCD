"""Orkestrator Eksperimen & Pipeline Runner
Penanggung Jawab: Anggota 1 (A1 - Project Lead & Data Engineer)

Fungsi:
Menjalankan 4 skenario eksperimen secara batch deterministik,
mengumpulkan metrik kuantitatif (MAE, MAPE, RMSE, Pearson r, IoU, Dice),
mengekspor tabel CSV, dan menghasilkan seluruh grafik publikasi ilmiah.
"""

from pathlib import Path
import shutil
import time
from typing import Dict, List
import numpy as np
import pandas as pd

from src.dataset import (
    load_metadata_csv,
    filter_stratified_subset,
    parse_filename_metadata,
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
    prep_img = preprocess_pipeline(img, sigma=sigma, apply_stretching=False)

    # Foreground mask Otsu & pembersihan morfologi
    bin_mask, thresh_val = otsu_thresholding(prep_img)
    cleaned_mask = morphological_cleanup(bin_mask)

    # 1. Baseline: Otsu + Connected Components
    count_base, labels_base, _ = baseline_otsu_counting(prep_img)

    # EDT (Euclidean Distance Transform)
    dist_map = compute_distance_transform(cleaned_mask)

    # 2. Strategi M1: Local Maxima Peak Finding
    markers_m1, _ = marker_strategy_m1_local_maxima(dist_map, min_distance=m1_r_min)
    labels_m1, count_m1 = apply_marker_controlled_watershed(dist_map, markers_m1, cleaned_mask)

    # 3. Strategi M2: h-Maxima Transform
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
        "cleaned_mask": cleaned_mask,
        "labels_base": labels_base,
        "labels_m1": labels_m1,
        "labels_m2": labels_m2,
        "labels_m3": labels_m3,
        "raw_img": img,
        "dist_map": dist_map,
        "markers_m2": markers_m2,
    }


def main():
    print("=" * 65)
    print("== [A1] Menjalankan Pipeline Batch Eksperimen Cell Counting BBBC005 ==")
    print("=" * 65)

    images_dir = Path("data/images")
    masks_dir = Path("data/masks")

    out_dirs = [
        Path("results"),
        Path("results/figures"),
        Path("result_paper"),
    ]
    for d in out_dirs:
        d.mkdir(parents=True, exist_ok=True)

    image_files = sorted(list(images_dir.glob("*.TIF")))
    total_images = len(image_files)
    if total_images == 0:
        print("[ERROR] Tidak ada citra di folder data/images. Jalankan src.download_subset dulu.")
        return

    print(f"Total citra terdeteksi: {total_images} citra.")

    records = []
    spatial_records = []
    representative_sample = None

    start_time = time.time()

    for idx, img_path in enumerate(image_files, start=1):
        meta = parse_filename_metadata(img_path.name)
        cell_count = meta["cell_count"]
        blur = meta["blur"]
        sample_id = meta["sample_id"]

        res = run_single_image_pipeline(img_path, gt_count=cell_count)

        # Simpan sampel representatif untuk kolase visual (C=27 atau C=53 pada F=1)
        if blur == 1 and cell_count in [27, 53] and sample_id == 1 and representative_sample is None:
            representative_sample = res

        # Catat prediksi masing-masing metode
        methods = {
            "Baseline (Otsu)": res["pred_baseline"],
            "M1 (Local Maxima)": res["pred_m1"],
            "M2 (h-Maxima)": res["pred_m2"],
            "M3 (Erosion)": res["pred_m3"],
        }

        for method_name, pred_val in methods.items():
            err = pred_val - cell_count
            abs_err = abs(err)
            records.append({
                "filename": img_path.name,
                "cell_count": cell_count,
                "blur": blur,
                "sample_id": sample_id,
                "method": method_name,
                "gt_count": cell_count,
                "pred_count": pred_val,
                "error": err,
                "abs_error": abs_err,
            })

        # Eksperimen 4: Evaluasi Spasial IoU & Dice jika citra memiliki mask F1
        mask_path = masks_dir / img_path.name
        if mask_path.exists():
            gt_mask = load_mask(mask_path)
            # Evaluasi mask foreground
            sp_base = calculate_spatial_metrics(res["cleaned_mask"], gt_mask)
            sp_m1 = calculate_spatial_metrics(res["labels_m1"] > 0, gt_mask)
            sp_m2 = calculate_spatial_metrics(res["labels_m2"] > 0, gt_mask)
            sp_m3 = calculate_spatial_metrics(res["labels_m3"] > 0, gt_mask)

            spatial_records.append({
                "filename": img_path.name,
                "cell_count": cell_count,
                "sample_id": sample_id,
                "iou_baseline": sp_base["iou"],
                "dice_baseline": sp_base["dice"],
                "iou_m1": sp_m1["iou"],
                "dice_m1": sp_m1["dice"],
                "iou_m2": sp_m2["iou"],
                "dice_m2": sp_m2["dice"],
                "iou_m3": sp_m3["iou"],
                "dice_m3": sp_m3["dice"],
            })

        if idx % 24 == 0 or idx == total_images:
            elapsed = time.time() - start_time
            print(f"[{idx:3d}/{total_images:3d}] citra diproses ({elapsed:.1f}s)...")

    # 1. Konversi ke DataFrame
    df_long = pd.DataFrame(records)
    df_spatial = pd.DataFrame(spatial_records)

    # 2. Hitung Metrik Global Ringkasan (Tabel Eksperimen 1)
    summary_rows = []
    for method_name, grp in df_long.groupby("method", sort=False):
        metrics = calculate_counting_metrics(grp["gt_count"].values, grp["pred_count"].values)
        summary_rows.append({
            "method": method_name,
            "mae": round(metrics["mae"], 3),
            "mape": round(metrics["mape"], 2),
            "rmse": round(metrics["rmse"], 3),
            "pearson_r": round(metrics["pearson_r"], 4),
            "osr": round(metrics["osr"], 4),
            "usr": round(metrics["usr"], 4),
        })

    summary_df = pd.DataFrame(summary_rows)

    # Simpan hasil CSV
    df_long.to_csv("results/metrics_detailed.csv", index=False)
    summary_df.to_csv("results/metrics_summary.csv", index=False)
    summary_df.to_csv("results/metrics.csv", index=False)
    if not df_spatial.empty:
        df_spatial.to_csv("results/metrics_spatial_f1.csv", index=False)

    print("\n" + "=" * 65)
    print("HASIL EVALUASI GLOBAL (Eksperimen 1: Komparasi Metode)")
    print("=" * 65)
    print(summary_df.to_string(index=False))

    if not df_spatial.empty:
        print("\n" + "=" * 65)
        print("HASIL EVALUASI SPASIAL F1 (Eksperimen 4: IoU & Dice)")
        print("=" * 65)
        spatial_summary = pd.DataFrame([
            {"method": "Baseline (Otsu)", "mean_iou": round(df_spatial["iou_baseline"].mean(), 4), "mean_dice": round(df_spatial["dice_baseline"].mean(), 4)},
            {"method": "M1 (Local Maxima)", "mean_iou": round(df_spatial["iou_m1"].mean(), 4), "mean_dice": round(df_spatial["dice_m1"].mean(), 4)},
            {"method": "M2 (h-Maxima)", "mean_iou": round(df_spatial["iou_m2"].mean(), 4), "mean_dice": round(df_spatial["dice_m2"].mean(), 4)},
            {"method": "M3 (Erosion)", "mean_iou": round(df_spatial["iou_m3"].mean(), 4), "mean_dice": round(df_spatial["dice_m3"].mean(), 4)},
        ])
        print(spatial_summary.to_string(index=False))
        spatial_summary.to_csv("results/spatial_summary.csv", index=False)

    # 3. Pemicu Plotting Visualisasi (Tugas A4)
    print("\nMenghasilkan visualisasi grafik dan kolase tahapan...")
    plot_method_comparison_bar(summary_df, "results/figures/fig1_method_comparison_bar.png")
    plot_density_analysis_line(df_long, "results/figures/fig2_density_analysis.png")
    plot_blur_degradation_line(df_long, "results/figures/fig3_blur_degradation.png")

    if representative_sample is not None:
        plot_pipeline_stages(
            raw_img=representative_sample["raw_img"],
            distance_map=representative_sample["dist_map"],
            markers=representative_sample["markers_m2"],
            ws_labels=representative_sample["labels_m2"],
            title="Tahapan Segmentasi Marker-Controlled Watershed (M2 h-Maxima)",
            output_path="results/figures/fig4_segmentation_examples.png",
        )

    # Salin figur ke results/figures
    total_time = time.time() - start_time
    print(f"\n[SUKSES] Seluruh eksperimen selesai dieksekusi dalam {total_time:.2f} detik!")
    print("Hasil kuantitatif tersimpan di: results/metrics_summary.csv")
    print("Grafik tersimpan di: results/figures/")


if __name__ == "__main__":
    main()
