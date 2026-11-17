# PCD Final Project — Project Plan

## 1. Ringkasan Status Proyek

- **Topik Terpilih:** Analisis Pengaruh Strategi Pembentukan Marker terhadap Akurasi Marker-Controlled Watershed untuk Penghitungan Sel pada Citra Mikroskopis BBBC005
- **Fase Saat Ini:** 03 — Research Design & Methodology
- **Status:** In Progress
- **Metode Disetujui:** Pengolahan Citra Digital Klasik (Otsu Thresholding, Euclidean Distance Transform, 3 Strategi Marker, Marker-Controlled Watershed)
- **Dataset:** Broad Bioimage Benchmark Collection — BBBC005 (citra mikroskopi sel sintetis dengan variasi cell count 1–100 dan blur F1–F32)
- **Target Luaran:** Kode modular teruji, laporan eksperimen kuantitatif, artikel ilmiah IEEE Conference (A4 dua kolom, Bahasa Indonesia formal), dan materi presentasi/demo.

---

## 2. Fase Proyek & Progres

| Fase | Deskripsi | Status | Target Waktu |
|---|---|---|---|
| **01** | **Research Exploration & Ideation** | Selesai | Selesai |
| **02** | **Topic Selection & Validation** | Selesai | Selesai (Cell Counting Terpilih) |
| **03** | **Research Design & Methodology** | **In Progress** | Tahap Sekarang |
| **04** | **Implementation (Modular Codebase)** | Belum Dimulai | Menunggu Desain Selesai |
| **05** | **Experiments & Quantitative Evaluation** | Belum Dimulai | Setelah Implementasi Siap |
| **06** | **Scientific Paper Writing (IEEE Format)** | Belum Dimulai | Paralel/Pasca-Eksperimen |
| **07** | **Final Presentation & Deliverables** | Belum Dimulai | Fase Terakhir |

---

## 3. Work Breakdown Structure (WBS) & Rencana Pengerjaan

### Sprint 1: Phase 03 — Research Design & Methodology (Tahap Berjalan)
- [x] **Task 3.1 — Formalisasi Masalah & Research Questions:** Menetapkan 3 RQ inti (RQ1: Efektivitas MCW vs Baseline, RQ2: Perbandingan strategi marker, RQ3: Ketahanan terhadap defokus optik).
- [ ] **Task 3.2 — Protokol Pengambilan Sampel Dataset (Sampling Strategy):** Menentukan subset sampel citra BBBC005 terstratifikasi:
  - Rentang Kepadatan Sel: Rendah (1–20 sel), Sedang (21–50 sel), Tinggi (51–100 sel).
  - Variasi Fokus/Blur: $F_1$ (tajam, 100% fokus), $F_8$ (blur ringan), $F_{16}$ (blur sedang), $F_{32}$ (blur berat).
  - Ground-truth mask subset untuk evaluasi spasial IoU/Dice.
- [ ] **Task 3.3 — Spesifikasi Algoritma Matematis & Parameter:**
  - Pra-pemrosesan: Ukuran kernel Gaussian blur dan sigma adaptif.
  - Binerisasi: Formula Otsu global dan parameter opening/closing morfologi (struktur elemen disk/lingkaran).
  - Transformasi Jarak: Euclidean Distance Transform ($L_2$ norm).
  - Strategi Marker:
    - *Strategi A (Local Maxima / Peak Finding):* Ambang batas min_distance dan deteksi puncak.
    - *Strategi B (h-maxima Transform / Peak Suppression):* Supresi puncak kecil lokal dengan toleransi kedalaman $h$.
    - *Strategi C (Thresholded Distance + Morphological Erosion):* Binerisasi peta jarak pada persentase tertentu dari nilai maksimum dilanjutkan erosi struktural.
  - Watershed: Rekonstruksi topografi (inverted distance map vs morphological gradient) dan simulasi perendaman (*immersion*).
- [ ] **Task 3.4 — Desain Skema Data & Harness Evaluasi:** Menentukan format pencatatan log hasil eksperimen (CSV/JSON) yang memuat metadata citra, ground-truth count, predicted count, error absolut, error persentase, dan waktu komputasi.

---

### Sprint 2: Phase 04 — Implementation (Kode Modular Python)
- [ ] **Task 4.1 — Dataset Loader & Parser (`src/dataset.py`):**
  - Parser regex untuk mengekstrak jumlah sel asli dan tingkat blur dari filename BBBC005 (`..._C<count>_F<blur>_...`).
  - Loader citra berbasis OpenCV/Scikit-image dan loader ground-truth mask.
  - Skrip automasi download sampling terarah (hanya mengunduh citra yang dibutuhkan untuk eksperimen).
- [ ] **Task 4.2 — Modul Pra-pemrosesan & Binerisasi (`src/preprocessing.py`):**
  - Konversi grayscale dan reduksi noise Gaussian filter.
  - Segmentasi foreground menggunakan metode Otsu thresholding.
  - Pembersihan noise latar dan penutupan lubang (*hole filling*) via morfologi closing/opening.
- [ ] **Task 4.3 — Modul Baseline Pipeline (`src/baseline.py`):**
  - Pipeline pembanding: Mask hasil Otsu langsung dihitung menggunakan *Connected Component Labeling* (tanpa pemisahan watershed).
- [ ] **Task 4.4 — Modul Ekstraksi Marker (`src/markers.py`):**
  - Implementasi Euclidean Distance Transform (EDT).
  - Implementasi Strategi A (Local Maxima dengan Scikit-image `peak_local_max`).
  - Implementasi Strategi B ($h$-maxima transform / suppression).
  - Implementasi Strategi C (Distance thresholding + morfologi).
- [ ] **Task 4.5 — Modul Marker-Controlled Watershed (`src/watershed.py`):**
  - Pemetaan topografi energi (inversi jarak).
  - Eksekusi watershed berlabel marker.
  - Rekonstruksi batas sel (*watershed ridge lines*).
- [ ] **Task 4.6 — Modul Pasca-pemrosesan (`src/postprocessing.py`):**
  - Eliminasi objek artefak berdasarkan batas minimum luas sel (*area thresholding*).
  - Filter sel yang terpotong batas bingkai citra (*border clearance*, opsional).
- [ ] **Task 4.7 — Modul Evaluasi Kuantitatif (`src/metrics.py`):**
  - Kalkulator MAE, MAPE, RMSE, koefisien korelasi Pearson ($r$).
  - Kalkulator Dice/IoU terhadap ground-truth mask (untuk subset $F_1$).
  - Deteksi dan kuantifikasi fenomena *over-segmentation* dan *under-segmentation*.
- [ ] **Task 4.8 — Batch Experiment Runner (`run_experiments.py`):**
  - Runner otomatis yang mengeksekusi semua metode terhadap seluruh sampel uji dan mengekspor hasil ke `results/metrics.csv`.
- [ ] **Task 4.9 — Modul Visualisasi & Demo (`src/visualizer.py`):**
  - Generator visual side-by-side: Citra Asli, Mask Otsu, Distance Map, Marker, Segmentasi Watershed, dan Ground Truth Overlay.

---

### Sprint 3: Phase 05 — Experiments & Evaluation
- [ ] **Task 5.1 — Eksekusi Eksperimen Komparatif:**
  - Menjalankan Baseline vs 3 Strategi Marker-Controlled Watershed pada sampel uji.
- [ ] **Task 5.2 — Analisis Kepadatan Sel (Density Breakdown):**
  - Menganalisis kurva error terhadap kepadatan sel (1–20, 21–50, 51–100 sel).
  - Membuktikan tingkat keparahan *under-counting* pada baseline akibat sel menempel.
- [ ] **Task 5.3 — Analisis Ketahanan terhadap Defokus Optik (Blur Breakdown):**
  - Menganalisis degradasi akurasi dari $F_1$, $F_8$, $F_{16}$, hingga $F_{32}$.
  - Mengidentifikasi titik kritis (*breaking point*) di mana peta jarak gagal mendeteksi marker sel yang kabur.
- [ ] **Task 5.4 — Evaluasi Mask Spasial (IoU/Dice):**
  - Menghitung akurasi batas sel pada subset citra tajam yang memiliki ground-truth mask.
- [ ] **Task 5.5 — Analisis Kasus Kegagalan (*Error Analysis*):**
  - Mengumpulkan dan memvisualisasikan contoh spesifik di mana terjadi over-segmentasi (sel tunggal terpecah jadi 2) atau under-segmentasi (dua sel gagal dipisahkan).

---

### Sprint 4: Phase 06 — Scientific Paper Writing (Format IEEE Conference)
- [ ] **Task 6.1 — Penulisan Abstrak Dwibahasa & Pendahuluan:**
  - Abstrak Bahasa Indonesia dan Bahasa Inggris mencakup urgensi, metode klasik yang diajukan, dataset BBBC005, dan hasil kuantitatif ringkas.
  - Pendahuluan: latar belakang, limitasi penghitungan manual, problem sel berimpitan, pembatasan ruang lingkup non-DL, dan kontribusi riset.
- [ ] **Task 6.2 — Tinjauan Pustaka (Related Work):**
  - Sintesis perbandingan metode segmentasi klasik sel, watershed immersion (Vincent & Soille), dan benchmark mikroskopi BBBC005.
- [ ] **Task 6.3 — Metodologi & Formulasi Matematis:**
  - Penjelasan langkah demi langkah: Preprocessing, Otsu, EDT, 3 Strategi Marker, Watershed, dan Metrik Evaluasi.
  - Diagram alir pipeline sistem.
- [ ] **Task 6.4 — Hasil Eksperimen & Pembahasan:**
  - Tabel komparatif kuantitatif (MAE, MAPE, RMSE, $r$, IoU).
  - Grafik scatter plot (Ground Truth Count vs Predicted Count).
  - Grafik performa terhadap variasi blur dan densitas sel.
  - Gambar perbandingan visual segmentasi.
  - Diskusi ilmiah mendalam mengenai kekuatan dan kelemahan masing-masing strategi.
- [ ] **Task 6.5 — Kesimpulan & Daftar Pustaka:**
  - Kesimpulan berbasis data empiris, limitasi riset, dan saran pengembangan metode klasik di masa depan.
  - Daftar pustaka IEEE formal (DOI terverifikasi).

---

### Sprint 5: Phase 07 — Final Presentation & Packaging
- [ ] **Task 7.1 — Slide Presentasi:** Slide terstruktur (Latar Belakang, Metodologi, Demonstrasi Algoritma, Hasil Eksperimen, Kesimpulan).
- [ ] **Task 7.2 — Final Code Packaging & Dokumentasi:** Repositori bersih, file `README.md` dengan instruksi instalasi dan cara menjalankan replikasi eksperimen (`requirements.txt`).

---

## 4. Pembagian Peran Tim (3–4 Mahasiswa S1)

| Anggota Tim | Fokus Utama | Tanggung Jawab Spesifik |
|---|---|---|
| **Anggota 1 (Lead & Metodologi)** | Pipeline Segmentasi & Watershed | Arsitektur `watershed.py`, `markers.py`, formulasi matematis, dan bab metodologi paper. |
| **Anggota 2 (Data & Preprocessing)** | Dataset & Pipeline Baseline | Arsitektur `dataset.py`, `preprocessing.py`, `baseline.py`, automasi data, dan bab pendahuluan paper. |
| **Anggota 3 (Eksperimen & Metrik)** | Evaluasi Kuantitatif & Benchmark | Arsitektur `metrics.py`, `run_experiments.py`, visualisasi grafik/tabel, dan bab hasil paper. |
| **Anggota 4 (Opsional / UI-Demo)** | Visualizer & Dokumentasi Final | Arsitektur `visualizer.py`, analisis kasus kegagalan, penyiapan slide presentasi, dan audit format IEEE. |

---

## 5. Manajemen Risiko & Mitigasi

| Risiko | Dampak | Probabilitas | Tindakan Mitigasi |
|---|---|---|---|
| Ukuran file zip BBBC005 terlalu besar untuk diunduh penuh | Penyimpanan laptop penuh, waktu terbuang | Tinggi | Gunakan skrip sampling terarah untuk mengunduh subset citra yang merepresentasikan variasi cell count dan blur yang diuji. |
| Over-segmentasi parah pada citra dengan intensitas tidak rata | Nilai hitung sel melonjak jauh di atas GT | Sedang | Terapkan pra-pemrosesan Gaussian smoothing yang terkalibrasi dan gunakan strategi marker $h$-maxima / peak suppression. |
| Citra blur ekstrem ($F_{32}$) kehilangan batas sel sama sekali | Algoritma watershed gagal memisahkan sel | Tinggi | Dokumentasikan hal ini secara jujur sebagai batasan fisik optik (*optical breakdown limit*) dalam analisis paper; tidak merekayasa data. |
| Konflik format penulisan IEEE | Pengurangan nilai akademis | Rendah | Menggunakan template resmi IEEE Conference A4 dua kolom sejak draf awal penulisan. |
