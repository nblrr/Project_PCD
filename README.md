# Proyek PCD: Penghitungan Sel via Marker-Controlled Watershed pada Citra BBBC005

> **Analisis Pengaruh Strategi Pembentukan Marker terhadap Akurasi Marker-Controlled Watershed untuk Penghitungan Sel pada Citra Mikroskopis BBBC005**  
> Proyek Akhir Mata Kuliah Pengolahan Citra Digital (PCD)  
> Program Studi Informatika — Universitas Sebelas Maret (UNS)

---

## 1. Ringkasan Proyek

Penelitian ini bertujuan untuk mengatasi permasalahan **sel yang saling menempel atau bertumpang-tindih (*touching/overlapping cells*)** pada citra mikroskopi fluoresensi. Pendekatan segmentasi ambang biner global (*Otsu Thresholding*) cenderung mengenali kluster sel sebagai satu objek tunggal, menyebabkan galat *under-counting* yang signifikan.

Proyek ini menginvestigasi perbandingan matematis **3 strategi pembentukan marker** pada *Euclidean Distance Transform* (EDT) sebelum proses *Marker-Controlled Watershed* (Vincent & Soille, 1991):
1. **M1 — Local Maxima Peak Finding** (variasi radius supresi $r_{\min}$)
2. **M2 — $h$-Maxima Transform** (variasi ketinggian supresi kedalaman $h$)
3. **M3 — Distance Thresholding & Morphological Erosion** (variasi iterasi erosi $n_{\text{iter}}$)
4. **Baseline (B) — Otsu Thresholding + Connected Components** (tanpa watershed)

Evaluasi diuji secara komprehensif terhadap variasi kepadatan sel ($C = 1 \dots 100$) dan tingkat defokus optik ($F = 1, 7, 17, 32$).

---

## 2. Pembagian Peran & Tanggung Jawab Tim (4 Orang)

Proyek ini mengadopsi arsitektur modular di mana setiap anggota memegang kepemilikan modul kode, skenario eksperimen, dan bagian bab paper IEEE:

| Anggota | Peran & Fokus | Modul Kode (`src/`) | Eksperimen Utama | Bab Paper IEEE |
|---|---|---|---|---|
| **A1** | **Project Lead & Data Engineer** | `dataset.py`, `download_subset.py`, `run_experiments.py` | **Eksperimen 1** (Perbandingan metode global & tabel metrik) | **Bab I** (Pendahuluan) + **Bab IV** (Tabel Komparasi) |
| **A2** | **Preprocessing & Baseline Engineer** | `preprocessing.py`, `baseline.py` | **Eksperimen 4** (Kualitas segmentasi mask IoU/Dice $F_1$) | **Bab II** (Metodologi: Preprocessing & Baseline) + Abstrak |
| **A3** | **Marker & Watershed Engineer** | `markers.py` (M1, M2, M3), `watershed.py` | **Eksperimen 2** (Sensitivitas kepadatan sel & tuning parameter) | **Bab II** (Metodologi: Marker Strategies & Watershed) |
| **A4** | **Evaluation & Visualization Engineer** | `metrics.py`, `visualizer.py` | **Eksperimen 3** (Ketahanan terhadap blur & plotting grafik) | **Bab III** (Setup Eksperimen) + **Bab V** (Kesimpulan) |

---

## 3. Dataset Benchmark: BBBC005

Dataset yang digunakan berasal dari **Broad Bioimage Benchmark Collection (BBBC005 v1)**:
* Citra mikroskopi sintetis sel mamalia berdimensi $696 \times 520$ piksel (grayscale 8-bit).
* Kanal yang dianalisis: **`w2` (nuclei stain fluoresensi)** sebagai input utama segmentasi sel.
* **Protokol Sampling Terstratifikasi:** Untuk efisiensi komputasi CPU dan kepatuhan Git, eksperimen menggunakan **144 citra representatif**:
  * **Kepadatan Rendah:** $C \in \{1, 6\}$ (kontak sel jarang).
  * **Kepadatan Sedang:** $C \in \{27, 52\}$ (kontak moderat).
  * **Kepadatan Tinggi:** $C \in \{74, 100\}$ (kluster rapat).
  * **Level Blur Fokus:** $F \in \{1, 7, 17, 32\}$.
  * **Sampel:** 6 replika sampel per strata ($s01 \dots s06$).
* **Subset Mask Ground-Truth:** 36 citra pada kondisi fokus tajam ($F_1$) untuk evaluasi spasial IoU dan Dice.

---

## 4. Panduan Instalasi & Menjalankan Proyek

### A. Prasyarat Sistem
* Python 3.10 atau versi lebih baru.
* Lingkungan komputasi CPU standar (tidak memerlukan GPU).

### B. Setup Virtual Environment
```bash
# 1. Clone repositori
git clone https://github.com/<username>/PCD_PROJECT.git
cd PCD_PROJECT

# 2. Buat virtual environment
python -m venv venv

# 3. Aktifkan environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# 4. Instal seluruh library dependensi
pip install -r requirements.txt
```

### C. Menyiapkan Subset Data (Tugas A1)
Ekstrak 144 citra target dari arsip ZIP lokal ke folder `data/`:
```bash
python -m src.download_subset
```

### D. Menjalankan Eksperimen End-to-End
```bash
python -m src.run_experiments
```
Output hasil pengukuran akan tersimpan di:
* `results/metrics.csv` (Tabel kuantitatif MAE, MAPE, RMSE, Pearson $r$, IoU, Dice).
* `results/figures/` (Grafik perbandingan metode, analisis densitas, degradasi blur, dan visualisasi tahapan).

---

## 5. Struktur Repositori

```text
PCD_PROJECT/
├── README.md                      # Dokumentasi utama proyek
├── requirements.txt               # Daftar dependensi library Python
├── .gitignore                     # Aturan filter file besar & lingkungan virtual
├── IDEA.md                        # Brief otoritatif latar belakang riset
├── PROJECT_PLAN.md                # Rencana kerja & WBS mingguan
├── AGENTS.md                      # Instruksi instruksional lingkungan riset
├── Dokumen_Perencanaan_Proyek_PCD_Cell_Counting.pdf  # Dokumen rencana 23 halaman
│
├── research/                      # Dokumen riset & metadata
│   ├── research_design_cell_counting.md # Spesifikasi detail metodologi
│   ├── paper rujukan/             # Paper ilmiah rujukan (Vincent 1991, Otsu 1979, dll.)
│   └── dataset/                   # File CSV metadata BBBC005
│       └── BBBC005_results_bray.csv
│
├── src/                           # Kode sumber modular
│   ├── __init__.py
│   ├── dataset.py                 # [A1] Data loader & stratified sampler
│   ├── download_subset.py         # [A1] Ekstraktor selektif subset data
│   ├── preprocessing.py           # [A2] Gaussian smoothing & contrast stretching
│   ├── baseline.py                # [A2] Otsu thresholding & connected components
│   ├── markers.py                 # [A3] Strategi marker M1, M2, dan M3
│   ├── watershed.py               # [A3] Marker-controlled watershed simulation
│   ├── metrics.py                 # [A4] Kalkulasi MAE, MAPE, RMSE, r, IoU, Dice
│   ├── visualizer.py              # [A4] Plotting grafik publikasi & kolase
│   └── run_experiments.py         # [A1] Runner eksperimen end-to-end
│
├── data/                          # Subset citra hasil ekstraksi (di-ignore dari git)
│   ├── images/                    # 144 file citra TIF w2
│   └── masks/                     # 36 file ground-truth mask F1
│
├── results/                       # Luaran eksperimen kuantitatif (di-track di git)
│   ├── metrics.csv                # Tabel hasil evaluasi
│   └── figures/                   # Grafik publikasi PNG (fig1 s.d. fig4)
│
└── paper/                         # Draf artikel ilmiah IEEE Conference
    └── ieee_draft.docx
```

---

## 6. Protokol Kolaborasi Git

1. **Strategi Percabangan (*Branching*):**
   * Branch `main`: Khusus kode stabil yang sudah diverifikasi.
   * Setiap anggota bekerja pada branch masing-masing:
     * `feature/dataset` (A1)
     * `feature/preprocessing` (A2)
     * `feature/markers` (A3)
     * `feature/metrics` (A4)
2. **Konvensi Pesan Commit:**
   Gunakan format: `[MODUL] Pesan deskripsi perubahan`  
   Contoh:  
   * `[dataset] implementasi parser metadata nama file BBBC005`  
   * `[markers] implementasi h-maxima transform dengan variasi parameter h`  
   * `[metrics] tambahkan kalkulasi pearson r dan rasio over-segmentasi`
3. **Penggabungan Kode (*Merge*):**  
   Penggabungan ke `main` dilakukan melalui *Pull Request* (PR) setelah dilakukan *peer review* silang oleh rekan tim.

---

## 7. Referensi Kunci

1. **L. Vincent & P. Soille (1991).** *Watersheds in digital spaces: an efficient algorithm based on immersion simulations.* IEEE TPAMI, 13(6), 583–598.
2. **N. Otsu (1979).** *A threshold selection method from gray-level histograms.* IEEE TSMC, 9(1), 62–66.
3. **V. Ljosa, K. L. Sokolnicki, & A. E. Carpenter (2012).** *Annotated high-throughput microscopy image sets for validation.* Nature Methods, 9(7), 637.
4. **R. C. Gonzalez & R. E. Woods (2018).** *Digital Image Processing*, 4th Edition, Pearson.
