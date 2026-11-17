"""Modul Akuisisi & Loader Dataset BBBC005
Penanggung Jawab: Anggota 1 (A1 - Project Lead & Data Engineer)

Fungsi:
1. Parsing metadata nama file BBBC005 (C, F, s, w).
2. Membaca metadata resmi dari BBBC005_results_bray.csv.
3. Melakukan stratified sampling (144 citra w2 dan 36 mask F1).
4. Mengekstrak dan memuat citra TIF mikroskopi.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import zipfile
import cv2
import numpy as np
import pandas as pd

# Konfigurasi Strata Eksperimen Terverifikasi (Dokumen Perencanaan Hal. 9-10)
STRATA_C = {
    "rendah": [1, 6],
    "sedang": [27, 52],
    "tinggi": [74, 100],
}
SELECTED_C = [1, 6, 27, 52, 74, 100]
SELECTED_F = [1, 7, 17, 32]
SAMPLES_PER_STRATA = 6  # s01 s.d. s06


def parse_filename_metadata(filename: str) -> Dict[str, int]:
    """Ekstraksi metadata dari format penamaan standar BBBC005.

    Contoh nama file: SIMCEPImages_A01_C1_F1_s01_w2.TIF
    Return dict: {'cell_count': 1, 'blur': 1, 'sample_id': 1, 'channel': 2}
    """
    pattern = r"SIMCEPImages_[A-Z0-9]+_C(?P<C>\d+)_F(?P<F>\d+)_s(?P<s>\d+)_w(?P<w>\d+)\.TIF"
    match = re.search(pattern, filename, re.IGNORECASE)
    if not match:
        raise ValueError(f"Format nama file tidak cocok dengan pola BBBC005: {filename}")
    return {
        "cell_count": int(match.group("C")),
        "blur": int(match.group("F")),
        "sample_id": int(match.group("s")),
        "channel": int(match.group("w")),
    }


def load_metadata_csv(csv_path: Path | str) -> pd.DataFrame:
    """Membaca dan menyaring kolom penting dari BBBC005_results_bray.csv."""
    df = pd.read_csv(csv_path)
    return df


def filter_stratified_subset(
    df: pd.DataFrame,
    c_values: Optional[List[int]] = None,
    f_values: Optional[List[int]] = None,
    max_sample_id: int = SAMPLES_PER_STRATA,
    channel: str = "w2",
) -> pd.DataFrame:
    """Menyaring 144 baris citra representatif sesuai strata kepadatan dan blur."""
    if c_values is None:
        c_values = SELECTED_C
    if f_values is None:
        f_values = SELECTED_F

    # Kolom file target berdasarkan channel
    col_name = "Image_FileName_Nuclei" if channel == "w2" else "Image_FileName_CellBody"

    # Filter berdasarkan nilai C dan F
    filtered = df[
        df["Image_Metadata_ActualCellCount"].astype(int).isin(c_values)
        & df["Image_Metadata_BlurFilterSize"].astype(int).isin(f_values)
    ].copy()

    # Ekstrak sample_id dan batasi ke sample_id <= max_sample_id
    filtered["sample_id"] = filtered[col_name].apply(
        lambda fname: parse_filename_metadata(fname)["sample_id"]
    )
    subset = filtered[filtered["sample_id"] <= max_sample_id].copy()
    return subset.sort_values(by=["Image_Metadata_ActualCellCount", "Image_Metadata_BlurFilterSize", "sample_id"])


def extract_subset_from_zip(
    zip_path: Path | str,
    target_filenames: List[str],
    output_dir: Path | str,
) -> int:
    """Mengekstrak hanya file citra target dari dalam ZIP tanpa mengekstrak 1.8 GB penuh."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    target_set = set(target_filenames)
    extracted_count = 0

    with zipfile.ZipFile(zip_path, "r") as z:
        for zip_info in z.infolist():
            filename = Path(zip_info.filename).name
            if filename in target_set:
                source = z.open(zip_info)
                target_file = output_dir / filename
                with open(target_file, "wb") as f_out:
                    f_out.write(source.read())
                extracted_count += 1

    return extracted_count


def load_image(image_path: Path | str, as_float: bool = True) -> np.ndarray:
    """Memuat citra TIF 8-bit grayscale.

    Jika as_float=True, rentang intensitas dikonversi ke [0.0, 1.0] float64.
    """
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Citra tidak ditemukan atau gagal dimuat: {image_path}")
    if as_float:
        return img.astype(np.float64) / 255.0
    return img


def load_mask(mask_path: Path | str) -> np.ndarray:
    """Memuat ground-truth binary mask (0 untuk background, 1 untuk foreground)."""
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise FileNotFoundError(f"Mask tidak ditemukan: {mask_path}")
    return (mask > 0).astype(np.uint8)
