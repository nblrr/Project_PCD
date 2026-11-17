"""Modul Visualisasi & Plotting Eksperimen
Penanggung Jawab: Anggota 4 (A4 - Evaluation & Visualization Engineer)

Fungsi:
1. Plot perbandingan MAE antar-metode (fig1_method_comparison_bar.png).
2. Plot sensitivitas kepadatan sel C (fig2_density_analysis.png).
3. Plot degradasi blur optik F (fig3_blur_degradation.png).
4. Visualisasi kolase tahapan pemrosesan (input -> EDT -> marker -> watershed).
"""

from pathlib import Path
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_method_comparison_bar(
    summary_df: pd.DataFrame,
    output_path: Path | str = "results/figures/fig1_method_comparison_bar.png",
):
    """Menghasilkan bar chart MAE untuk 4 metode (Baseline, M1, M2, M3)."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(summary_df["method"], summary_df["mae"], color=["#7f7f7f", "#1f77b4", "#2ca02c", "#ff7f0e"])
    ax.set_title("Perbandingan MAE Antar-Strategi Marker (BBBC005 w2)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Metode", fontsize=10)
    ax.set_ylabel("Mean Absolute Error (sel)", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_density_analysis_line(
    df_results: pd.DataFrame,
    output_path: Path | str = "results/figures/fig2_density_analysis.png",
):
    """Line plot pengaruh kepadatan sel (C) terhadap MAE per metode."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))

    for method, grp in df_results.groupby("method"):
        agg = grp.groupby("cell_count")["abs_error"].mean()
        ax.plot(agg.index, agg.values, marker="o", label=method)

    ax.set_title("Pengaruh Kepadatan Sel terhadap Error Penghitungan", fontsize=12, fontweight="bold")
    ax.set_xlabel("Ground-Truth Cell Count (C)", fontsize=10)
    ax.set_ylabel("Mean Absolute Error (sel)", fontsize=10)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.7)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_blur_degradation_line(
    df_results: pd.DataFrame,
    output_path: Path | str = "results/figures/fig3_blur_degradation.png",
):
    """Line plot degradasi performa akibat tingkat blur optik (F)."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))

    for method, grp in df_results.groupby("method"):
        agg = grp.groupby("blur")["abs_error"].mean()
        ax.plot(agg.index, agg.values, marker="s", label=method)

    ax.set_title("Degradasi Akurasi Akibat Defokus Optik (Blur F)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Tingkat Blur Optik (F)", fontsize=10)
    ax.set_ylabel("Mean Absolute Error (sel)", fontsize=10)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.7)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_pipeline_stages(
    raw_img: np.ndarray,
    distance_map: np.ndarray,
    markers: np.ndarray,
    ws_labels: np.ndarray,
    title: str = "Tahapan Segmentasi Watershed",
    output_path: Path | str = "results/figures/fig4_segmentation_examples.png",
):
    """Menampilkan 4 subplot tahapan pemrosesan untuk laporan & paper."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    axes[0].imshow(raw_img, cmap="gray")
    axes[0].set_title("(a) Input w2 Citra Asli")
    axes[0].axis("off")

    axes[1].imshow(distance_map, cmap="jet")
    axes[1].set_title("(b) Euclidean Distance (EDT)")
    axes[1].axis("off")

    axes[2].imshow(markers > 0, cmap="magma")
    axes[2].set_title(f"(c) Marker Benih (N={len(np.unique(markers))-1})")
    axes[2].axis("off")

    axes[3].imshow(ws_labels, cmap="nipy_spectral")
    axes[3].set_title(f"(d) Watershed Labels (N={len(np.unique(ws_labels))-1})")
    axes[3].axis("off")

    plt.suptitle(title, fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
