# Desain Riset & Metodologi Teknis: Penghitungan Sel via Marker-Controlled Watershed pada BBBC005

**Dokumen:** Spesifikasi Riset & Desain Eksperimen (Phase 03)  
**Topik:** Analisis Pengaruh Strategi Pembentukan Marker terhadap Akurasi Marker-Controlled Watershed untuk Penghitungan Sel pada Citra Mikroskopis BBBC005  
**Institusi:** Program Studi Informatika, Universitas Sebelas Maret (UNS)  

---

## 1. Pendahuluan & Landasan Teoretis

### 1.1 Masalah Pemisahan Sel Berimpitan (*Touching Cells*)
Pada citra mikroskopi fluoresensi, sel-sel biologis kerap tumbuh dalam kluster atau berdekatan sehingga batas antar-sel saling menempel (*touching* atau *partially overlapping*). Segmentasi berbasis ambang biner global (*global thresholding*, misal Otsu) akan mengenali kluster sel tersebut sebagai satu komponen terhubung (*single connected component*). Akibatnya, penghitungan jumlah sel menghasilkan galat negatif yang signifikan (*severe under-counting*).

### 1.2 Formulasi Matematis Algoritma

#### A. Otsu Global Thresholding
Memisahkan intensitas piksel citra $I(x, y) \in [0, L-1]$ menjadi dua kelas (latar belakang $C_0$ dengan ambang $[0, t]$ dan latar depan $C_1$ dengan ambang $[t+1, L-1]$) dengan memaksimalkan variansi antarkelas:
$$\sigma_B^2(t) = \omega_0(t) \omega_1(t) [\mu_0(t) - \mu_1(t)]^2$$
di mana $\omega_0, \omega_1$ adalah probabilitas kemunculan kelas, dan $\mu_0, \mu_1$ adalah rata-rata intensitas masing-masing kelas. Nilai ambang optimal $t^*$ adalah:
$$t^* = \arg\max_{0 \le t < L} \sigma_B^2(t)$$

#### B. Operasi Morfologi Pembersihan
Binary mask awal $B(x, y)$ dibersihkan menggunakan kombinasi operasi morfologi:
- **Opening:** $B \circ K = (B \ominus K) \oplus K$ (menghapus bintik derau kecil).
- **Closing:** $B \bullet K = (B \oplus K) \ominus K$ (menutup lubang kecil intra-seluler).
dengan elemen penstruktur $K$ berbentuk piringan (*disk-shaped structuring element*) berukuran kecil ($r = 2$ atau $3$ piksel).

#### C. Transformasi Jarak Euclidean (*Euclidean Distance Transform* / EDT)
Untuk setiap piksel latar depan $p = (x, y) \in \text{Foreground}$, jarak Euclidean minimum ke piksel latar belakang terdekat $q = (u, v) \in \text{Background}$ dihitung sebagai:
$$D(p) = \min_{q \in \text{Background}} \sqrt{(x - u)^2 + (y - v)^2}$$
Peta jarak $D$ memiliki nilai puncak lokal (*local maxima*) tepat di sekitar pusat geometris masing-masing sel, bahkan ketika batas luar kedua sel saling bersentuhan.

#### D. Tiga Strategi Pembentukan Marker
1. **Strategi A — Local Maxima Peak Finding:**
   Mendeteksi titik puncak lokal pada peta jarak $D(p)$ dengan jarak minimum antarpuncak $\delta_{\min}$:
   $$M_A = \{ p \mid D(p) = \max_{q \in \mathcal{N}_{\delta}(p)} D(q) \text{ dan } D(p) > T_{\text{dist}} \}$$
2. **Strategi B — $h$-Maxima Transform (Peak Suppression):**
   Menerapkan rekonstruksi morfologi geodesik untuk memangkas puncak-puncak kecil yang tingginya kurang dari $h$:
   $$\text{HMAX}_h(D) = \mathcal{R}_D(D - h)$$
   Marker diperoleh dari puncak regional dari $\text{HMAX}_h(D)$. Strategi ini sangat efektif mencegah over-segmentasi pada sel yang memiliki tekstur permukaan tidak rata.
3. **Strategi C — Distance Thresholding & Morphological Erosion:**
   Membuat ambang batas adaptif pada peta jarak:
   $$B_{\text{core}} = \{ p \mid D(p) \ge \alpha \cdot \max(D) \}$$
   diikuti oleh erosi morfologi ringan untuk memisahkan jembatan tipis antarsel, kemudian melakukan *connected component labeling* sebagai marker.

#### E. Marker-Controlled Watershed (Immersion Simulation)
Fungsi topografi dibentuk dari inversi peta jarak:
$$g(p) = \max(D) - D(p)$$
atau kombinasi gradien morfologi. Marker regional yang dihasilkan diberi label unik $1, 2, \dots, M$. Proses perendaman air (*immersion*) dimulai dari lokasi marker dan menyebar menaiki permukaan topografi $g(p)$. Garis pertemuan antarcekungan air (*watershed lines*) ditetapkan sebagai batas pemisah sel.

---

## 2. Dataset Benchmark: BBBC005

### 2.1 Spesifikasi Citra
- **Sumber:** Broad Bioimage Benchmark Collection (BBBC005 v1).
- **Jenis Citra:** Citra mikroskopi fluoresensi sel mamalia sintetis (simulasi).
- **Dimensi:** $520 \times 696$ piksel, grayscale 8-bit.
- **Variasi Eksperimental:**
  - Jumlah sel (*cell count*): 1 hingga 100 sel per frame citra.
  - Tingkat kekaburan fokus (*defocus blur*): $F \in \{1, 2, 4, 8, 16, 32, 48, 64\}$ piksel lebar fungsi sebaran titik (*point spread function* / PSF).
- **Format Penamaan File:**
  Contoh: `SIMCEPImages_A01_w1_C25_F1_s01_w1.TIF`
  - `C25`: Ground-truth cell count = 25 sel.
  - `F1`: Tingkat blur fokus optik = 1 (fokus tajam).

### 2.2 Desain Protokol Stratified Sampling
Untuk menghindari pengunduhan dataset secara masif dan menjaga efisiensi eksperimen di komputer mahasiswa, dirancang subset pengujian terstratifikasi (*stratified representative test suite*) sebanyak 60 citra:
1. **Berdasarkan Kepadatan Sel:**
   - Densitas Rendah: $C \in \{5, 10, 15, 20\}$ (kontak antarsel minimal).
   - Densitas Sedang: $C \in \{30, 40, 50\}$ (kontak antarsel moderat).
   - Densitas Tinggi: $C \in \{65, 80, 100\}$ (kluster sel rapat dan saling tumpang-tindih).
2. **Berdasarkan Variasi Defokus Optik:**
   - $F_1$: Citra tajam (kontrol ideal).
   - $F_8$: Blur ringan.
   - $F_{16}$: Blur sedang.
   - $F_{32}$: Blur berat.
3. **Subset Evaluasi Segmentasi Spasial (Ground Truth Masks):**
   - Menggunakan 20 citra pada fokus tajam ($F_1$) yang dilengkapi file mask biner ground truth resmi dari BBBC005.

---

## 3. Desain Arsitektur Perangkat Lunak (`src/`)

Struktur kode dirancang modular dan berbasis pustaka standar saintifik Python:

```
PCD_PROJECT/
├── IDEA.md
├── PROJECT_PLAN.md
├── AGENTS.md
├── research/
│   ├── 01_project_ideas.md
│   ├── 02_literature_review.md
│   ├── 03_dataset_catalog.md
│   ├── 04_idea_comparison.md
│   ├── 05_recommendations.md
│   └── 06_research_design_cell_counting.md
├── data/
│   ├── images/              # Citra BBBC005 terstratifikasi
│   └── masks/               # Ground truth masks F1
├── src/
│   ├── __init__.py
│   ├── dataset.py           # Loader, regex parser metadata, automated sampler
│   ├── preprocessing.py     # Gaussian filter, Otsu thresholding, morfologi
│   ├── baseline.py          # Otsu + Connected Components (tanpa watershed)
│   ├── markers.py           # EDT, Strategi A (Local Maxima), B (h-maxima), C (Thresholded)
│   ├── watershed.py         # Inverted distance topography & Marker-Controlled Watershed
│   ├── postprocessing.py    # Filter ukuran area minimum sel & border clearing
│   ├── metrics.py           # MAE, MAPE, RMSE, Pearson r, IoU, Dice, Over/Under rates
│   └── visualizer.py        # Plot komparasi multi-panel (Citra, Mask, Markers, Watershed, GT)
├── run_experiments.py       # Skrip eksekusi eksperimen otomatis & export CSV
└── requirements.txt         # numpy, opencv-python, scipy, scikit-image, matplotlib, pandas
```

---

## 4. Matriks Eksperimen & Metrik Evaluasi

### 4.1 Matriks Metode yang Diuji
1. **Metode 0 (Baseline):** Otsu Thresholding $\rightarrow$ Morfologi $\rightarrow$ Connected Components Labeling.
2. **Metode 1 (MCW - Strategi A):** Otsu $\rightarrow$ EDT $\rightarrow$ Local Maxima Peaks $\rightarrow$ Watershed.
3. **Metode 2 (MCW - Strategi B):** Otsu $\rightarrow$ EDT $\rightarrow$ $h$-Maxima Transform $\rightarrow$ Watershed.
4. **Metode 3 (MCW - Strategi C):** Otsu $\rightarrow$ EDT $\rightarrow$ Thresholded Core Erosi $\rightarrow$ Watershed.

### 4.2 Formula Metrik Kuantitatif
- **Mean Absolute Error (MAE):**
  $$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |y_i - \hat{y}_i|$$
- **Mean Absolute Percentage Error (MAPE):**
  $$\text{MAPE} = \frac{100\%}{N} \sum_{i=1}^N \frac{|y_i - \hat{y}_i|}{y_i}$$
- **Root Mean Squared Error (RMSE):**
  $$\text{RMSE} = \sqrt{\frac{1}{N}\sum_{i=1}^N (y_i - \hat{y}_i)^2}$$
- **Koefisien Korelasi Pearson ($r$):**
  $$r = \frac{\sum (y_i - \bar{y})(\hat{y}_i - \bar{\hat{y}})}{\sqrt{\sum(y_i - \bar{y})^2 \sum(\hat{y}_i - \bar{\hat{y}})^2}}$$
- **Intersection over Union (IoU) & Dice Coefficient (untuk subset mask $F_1$):**
  $$\text{IoU} = \frac{|S_{\text{pred}} \cap S_{\text{gt}}|}{|S_{\text{pred}} \cup S_{\text{gt}}|}, \quad \text{Dice} = \frac{2 |S_{\text{pred}} \cap S_{\text{gt}}|}{|S_{\text{pred}}| + |S_{\text{gt}}|}$$
- **Kuantifikasi Over-segmentation vs Under-segmentation:**
  $$\text{Under-counting Rate} = \frac{\sum_{y_i > \hat{y}_i} (y_i - \hat{y}_i)}{\sum y_i}, \quad \text{Over-counting Rate} = \frac{\sum_{\hat{y}_i > y_i} (\hat{y}_i - y_i)}{\sum y_i}$$

---

## 5. Rencana Pembahasan & Reviewer Anticipation

| Potensi Pertanyaan Dosen / Reviewer | Jawaban Ilmiah & Bukti yang Disiapkan |
|---|---|
| *Mengapa tidak memakai U-Net atau Cellpose yang lebih modern?* | Proyek ini menguji batas kemampuan metode deterministik klasik sesuai silabus PCD. Metode klasik memiliki keunggulan transparansi matematis penuh, nol kebutuhan data training, bebas risiko overfitting, serta komputasi instan di perangkat tanpa GPU. |
| *Apakah metode ini bekerja pada sel nyata dengan bentuk ireguler?* | BBBC005 menyajikan variasi sintetis terkontrol. Sebagai batasan penelitian (*limitation*), kami mendokumentasikan bahwa transformasi jarak Euclidean mengasumsikan objek sel mendekati bentuk cembung (*convex-like*). Untuk sel amorf/ireguler, diperlukan pengembangan marker berbasis gradien atau morfologi tingkat lanjut. |
| *Mengapa performa drop pada blur F32?* | Pada defokus ekstrem ($F_{32}$), fungsi sebaran titik optik mengaburkan gradien batas antar-sel sehingga puncak peta jarak saling melebur secara fisik. Hal ini dibuktikan sebagai limitasi fisik optik, bukan semata kegagalan algoritma. |
