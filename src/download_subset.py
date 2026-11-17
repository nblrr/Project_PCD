"""Script Pengunduhan / Ekstraksi Selektif Dataset BBBC005
Penanggung Jawab: Anggota 1 (A1 - Project Lead & Data Engineer)

Fungsi:
Mengunduh atau mengekstrak hanya subset terstratifikasi (144 citra w2 dan 36 mask F1)
tanpa perlu memproses seluruh dataset mentah 1.8 GB.
"""

from pathlib import Path
import sys
import pandas as pd

from src.dataset import (
    load_metadata_csv,
    filter_stratified_subset,
    extract_subset_from_zip,
)


def prepare_local_subset(
    dataset_dir: Path | str = "research/dataset",
    output_dir: Path | str = "data",
):
    """Menyiapkan 144 citra w2 dan mask F1 dari ZIP lokal ke direktori data/."""
    dataset_path = Path(dataset_dir)
    images_zip = dataset_path / "BBBC005_v1_images.zip"
    csv_path = dataset_path / "BBBC005_results_bray.csv"
    gt_zip = dataset_path / "BBBC005_v1_ground_truth.zip"
    gt_dir = dataset_path / "BBBC005_v1_ground_truth" / "BBBC005_v1_ground_truth"

    out_images = Path(output_dir) / "images"
    out_masks = Path(output_dir) / "masks"
    out_images.mkdir(parents=True, exist_ok=True)
    out_masks.mkdir(parents=True, exist_ok=True)

    print("== [A1] Menyiapkan Subset Eksperimen BBBC005 ==")

    # 1. Baca metadata
    df = load_metadata_csv(csv_path)
    subset_df = filter_stratified_subset(df, channel="w2")
    target_filenames = subset_df["Image_FileName_Nuclei"].tolist()
    print(f"Total citra target strata: {len(target_filenames)} citra (channel w2).")

    # 2. Ekstrak citra w2 dari ZIP lokal jika ada
    if images_zip.exists():
        print(f"Mengekstrak {len(target_filenames)} citra dari {images_zip.name}...")
        extracted = extract_subset_from_zip(images_zip, target_filenames, out_images)
        print(f"Berhasil mengekstrak {extracted} citra ke {out_images}.")
    else:
        print(f"[PERINGATAN] File {images_zip} tidak ditemukan. Gunakan download selektif.")

    # 3. Ekstrak mask F1 untuk evaluasi segmentasi spasial
    subset_f1 = subset_df[subset_df["Image_Metadata_BlurFilterSize"] == 1]
    mask_filenames = subset_f1["Image_FileName_Nuclei"].tolist()
    print(f"Menyiapkan {len(mask_filenames)} mask ground-truth F1...")

    copied_masks = 0
    if gt_zip.exists():
        print(f"Mengekstrak {len(mask_filenames)} mask dari {gt_zip.name}...")
        copied_masks = extract_subset_from_zip(gt_zip, mask_filenames, out_masks)
        print(f"Berhasil mengekstrak {copied_masks} mask ke {out_masks}.")
    elif gt_dir.exists():
        for fname in mask_filenames:
            src_mask = gt_dir / fname
            if src_mask.exists():
                dst_mask = out_masks / fname
                dst_mask.write_bytes(src_mask.read_bytes())
                copied_masks += 1
        print(f"Berhasil menyiapkan {copied_masks} mask dari folder ke {out_masks}.")
    else:
        print(f"[PERINGATAN] File {gt_zip} atau folder {gt_dir} tidak ditemukan.")

    print("== Persiapan data selesai! ==")


if __name__ == "__main__":
    prepare_local_subset()
