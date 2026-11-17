# Catatan Detail Proyek: Penghitungan Sel Otomatis (Cell Counting)

Dokumen ini menjelaskan secara ringkas dan praktis: apa yang sebenarnya dikerjakan di proyek ini, bagaimana alur metodenya, hasil eksperimen nyata yang didapat, serta format luaran akhir yang harus dikumpulkan.

---

## 1. Inti Proyek: Sebenarnya Kita Ngapain?

### Masalah Nyata di Lapangan
Di laboratorium biologi, peneliti sering memotret sel menggunakan mikroskop fluoresensi untuk menghitung populasi sel. Masalahnya:
1. **Menghitung manual itu lama dan bikin mata lelah** kalau sampelnya ada ratusan atau ribuan.
2. **Sel mikroskop sering nempel atau tumpuk-menumpuk (*touching/overlapping cells*)**. Kalau cuma pakai teknik ambang biner biasa (Otsu), dua atau tiga sel yang nempel bakal dianggap sebagai **satu sel besar**. Akibatnya jumlah sel terhitung jauh lebih sedikit dari aslinya (*under-counting*).
3. **Fokus mikroskop kadang meleset (blur/defokus)**, membuat batas pinggir antar sel jadi kabur dan makin menyatu.

### Yang Kita Kerjakan
Kita membangun sistem berbasis **Pengolahan Citra Digital (PCD) Klasik** untuk:
1. Mendeteksi sel dari citra mikroskop sintetis benchmark (**BBBC005**).
2. Memisahkan sel-sel yang saling menempel menggunakan algoritma **Marker-Controlled Watershed**.
3. Menguji dan membandingkan **3 strategi pembuatan marker** (titik awal penanda sel) untuk mencari tahu strategi mana yang paling akurat dan paling tahan saat citra blur atau selnya sangat padat.

> **Catatan Aturan Dosen:**  
> Proyek ini **sama sekali tidak memakai Deep Learning** (tanpa YOLO, U-Net, atau CNN). Dosen mewajibkan metode matematika PCD klasik yang deterministik, ringan di CPU biasa, dan prosesnya bisa dijelaskan langkah demi langkah (*interpretable*).

---

## 2. Alur Metode: Dari Gambar Masuk Sampai Keluar Angka

Pipeline pemrosesan citra dirancang modular dalam 6 tahapan utama:

```
[Citra Fluoresensi Asli (w2)]
              │
              ▼
   1. Preprocessing (Gaussian Filter + Contrast Stretching)
              │
              ▼
   2. Segmentasi Biner (Otsu Thresholding + Morfologi Closing)
              │
              ▼
   3. Peta Jarak (Euclidean Distance Transform / EDT)
              │
              ▼
   4. Ekstraksi Marker (Uji Coba 3 Strategi: M1, M2, M3)
              │
              ▼
   5. Pemisahan Sel (Marker-Controlled Watershed)
              │
              ▼
   6. Evaluasi & Metrik (Hitung Jumlah Objek vs Ground Truth)
```

### Langkah demi Langkahnya:

1. **Preprocessing (Pembersihan Awal):**
   * Citra input berupa kanal fluoresensi inti sel (`w2`, grayscale 8-bit).
   * Diberi filter **Gaussian ($\sigma = 1.5$)** untuk meredam bintik-bintik noise sensor mikroskop.
   * Dilakukan penyesuaian kontras (*min-max stretching*) agar perbedaan antara inti sel yang terang dan background yang gelap semakin tegas.

2. **Binerisasi (Memisahkan Sel dari Background):**
   * Menggunakan **Otsu Thresholding** untuk menentukan nilai ambang batas optimal secara otomatis berdasarkan variansi antar-kelas.
   * Diterapkan operasi morfologi **Closing** (elemen struktur disk kecil) untuk menutup lubang kecil di dalam badan sel dan meratakan tepian. Hasilnya adalah *binary mask* (sel = putih, background = hitam).

3. **Euclidean Distance Transform (EDT):**
   * Mask biner tadi diubah menjadi peta jarak Euclidean.
   * Logikanya: piksel yang berada persis di tengah-tengah sel akan punya jarak paling jauh ke background (nilainya tinggi / puncak bukit), sedangkan piksel di pinggir nilainya kecil (lembah).
   * Peta jarak inilah yang menjadi dasar untuk menentukan titik pusat masing-masing sel.

4. **Ekstraksi Marker (3 Strategi yang Ditandingkan):**
   * **Baseline (Pembanding):** Mask biner Otsu langsung dihitung menggunakan *Connected Components*. Tidak ada usaha memisahkan sel yang nempel.
   * **Strategi M1 — Local Maxima Peak Finding:** Mencari titik-titik puncak lokal tertinggi pada peta EDT dengan syarat jarak minimum antar puncak ($r_{\min} = 7$ piksel).
   * **Strategi M2 — $h$-Maxima Transform:** Mencari puncak topografi tetapi menekan puncak-puncak kecil yang ketinggiannya kurang dari nilai ambang $h$. Tujuannya agar riak noise kecil di satu sel tidak dianggap dua sel terpisah.
   * **Strategi M3 — Distance Thresholding & Erosi:** Memotong peta jarak pada persentase tertentu dari nilai maksimum (misal 30%), lalu dierosi beberapa iterasi sampai menyusut menjadi inti kecil di tengah sel.

5. **Marker-Controlled Watershed:**
   * Peta EDT dibalik nilainya (dikalikan $-1$) sehingga pusat sel berubah menjadi cekungan air paling dalam.
   * Marker hasil langkah ke-4 ditaruh di dasar cekungan sebagai sumber mata air berlabel.
   * Simulasi luapan air dijalankan (algoritma Vincent & Soille 1991). Saat genangan air dari dua sel yang bersebelahan bertemu di lekukan cekungan, sistem membangun batas pemisah (*watershed ridge lines*).
   * Dengan cara ini, sel yang tadinya menyatu berhasil dibelah tepat di lekukan pertemuannya.

6. **Postprocessing & Penghitungan:**
   * Objek-objek yang ukurannya terlalu kecil (luas < 15 piksel) dibuang karena merupakan artefak atau sisa noise.
   * Jumlah sel akhir dihitung dari total region berlabel unik yang tersisa.

---

## 3. Dataset yang Dipakai

* **Nama Dataset:** Broad Bioimage Benchmark Collection — **BBBC005 v1** (koleksi standar internasional dari Broad Institute of Harvard & MIT).
* **Karakteristik Citra:** Citra sintetis sel mamalia berukuran $696 \times 520$ piksel.
* **Protokol Sampling Terstratifikasi (144 Citra):**
  Untuk memastikan pengujian adil dan efisien di CPU tanpa perlu download puluhan gigabyte:
  * **Kepadatan Rendah:** 1 dan 6 sel per citra (sel jarang bersentuhan).
  * **Kepadatan Sedang:** 27 dan 52 sel per citra (mulai sering nempel).
  * **Kepadatan Tinggi:** 74 dan 100 sel per citra (membentuk kluster rapat).
  * **Tingkat Blur/Defokus:** $F_1$ (tajam 100%), $F_7$ (agak blur), $F_{17}$ (blur sedang), dan $F_{32}$ (sangat blur).
  * Tiap kombinasi diambil 6 sampel replika acak ($s01$ sampai $s06$).
* **Ground-Truth Mask:** 36 citra pada kondisi tajam ($F_1$) digunakan untuk mengukur akurasi bentuk spasial (IoU dan Dice).

---

## 4. Hasil Eksperimen Nyata: Bagaimana Performanya?

Eksperimen sudah dijalankan pada 144 citra uji. Hasil kuantitatif dari `results/metrics_summary.csv` adalah sebagai berikut:

| Metode / Strategi | MAE (Error Rata-rata) | MAPE (%) | RMSE | Korelasi Pearson ($r$) | Under-Seg Ratio (USR) | Keterangan Singkat |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **Baseline (Otsu Saja)** | 34.04 sel | 48.56% | 48.53 | 0.3128 | 78.54% | Meleset parah saat sel padat. |
| **M1 (Local Maxima)** | **18.40 sel** | **23.65%** | **32.18** | 0.7020 | **42.44%** | **Paling akurat & error paling rendah.** |
| **M2 ($h$-Maxima)** | 22.40 sel | 32.05% | 35.10 | **0.7449** | 51.52% | Korelasi paling linier & stabil. |
| **M3 (Erosi Morfologi)** | 33.19 sel | 48.49% | 47.61 | 0.3610 | 76.57% | Kurang efektif, mirip baseline. |

### Poin Analisis Utama:
1. **MCW Berhasil Memotong Error Separuhnya:**  
   Metode M1 berhasil memangkas error rata-rata dari 34 sel (Baseline) menjadi **18.4 sel** (penurunan error ~46%). Angka MAPE turun dari 48.5% menjadi **23.6%**.
2. **Kenapa Baseline Gagal?**  
   Rasio *under-segmentation* (USR) Baseline mencapai **78.5%**. Artinya pada 78% sampel, sistem mengira jumlah sel lebih sedikit dari aslinya karena gumpalan sel tidak terpecah.
3. **M1 vs M2:**  
   * **M1** unggul dalam menghitung sel individual secara tepat karena radius minimum $r_{\min}$ sangat cocok dengan ukuran rata-rata inti sel BBBC005.
   * **M2** punya keunggulan korelasi Pearson paling tinggi ($r = 0.745$), artinya prediksinya paling konsisten mengikuti tren kenaikan jumlah sel asli, dan tidak gampang memunculkan marker palsu saat citra terkena blur.
4. **Kenapa M3 Kurang Optimal?**  
   Operasi erosi seragam cenderung menghapus sel-sel kecil sebelum berhasil memisahkan sel-sel besar yang menempel rapat.
5. **Dampak Defokus (Blur):**  
   Pada blur berat ($F_{32}$), semua metode mengalami kenaikan error karena batas intensitas sel melebar dan kontur gradien menghilang. Namun M1 dan M2 tetap jauh lebih baik dibanding baseline.

---

## 5. Bentuk Luaran Proyek (Deliverables yang Harus Ada)

Supaya proyek ini tuntas dan siap dinilai dosen, luaran yang dihasilkan mencakup:

1. **Kode Sumber Modular (`src/`):**
   * Script Python bersih, berstruktur rapi, dan bisa dijalankan ulang dengan satu perintah: `python -m src.run_experiments`.
2. **Data & Grafik Evaluasi (`results/`):**
   * `metrics_summary.csv` dan `metrics_detailed.csv` berisi seluruh angka evaluasi.
   * Gambar publikasi di `results/figures/`:
     * `fig1_method_comparison.png` (Perbandingan MAE & RMSE antar metode).
     * `fig2_density_analysis.png` (Grafik performa pada sel sedikit vs padat).
     * `fig3_blur_degradation.png` (Grafik ketahanan saat gambar makin blur).
     * `fig4_pipeline_visual.png` (Kolase visual: Asli $\rightarrow$ Mask Otsu $\rightarrow$ EDT $\rightarrow$ Marker $\rightarrow$ Hasil Potongan Watershed).
3. **Paper Ilmiah Format IEEE Conference (`paper/`):**
   * Dokumen 6 halaman, format 2 kolom, Bahasa Indonesia baku.
   * Struktur: Abstrak, Pendahuluan, Metodologi Matematis, Setup Eksperimen, Hasil & Pembahasan Kuantitatif, serta Kesimpulan.
4. **Slide Presentasi & Demo Pengujian:**
   * Menampilkan perbandingan visual sebelum vs sesudah watershed pada kasus sel bertumpuk.
