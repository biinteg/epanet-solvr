# Product Requirements Document (PRD)
**Produk:** Web Aplikasi Optimasi Jaringan Distribusi Air (EPANET Solver)
**Status:** Draft
**Tanggal:** 10 Mei 2026

## 1. Pendahuluan
### 1.1 Latar Belakang
Dalam desain jaringan distribusi air menggunakan software EPANET, penentuan diameter pipa seringkali dilakukan melalui proses coba-coba (*trial and error*). Proses manual ini sangat memakan waktu, terutama untuk mencapai kriteria hidrolis yang ditetapkan oleh regulasi. Oleh karena itu, diperlukan sebuah alat otomatisasi yang mampu mengiterasi ukuran pipa secara cerdas dan cepat tanpa intervensi manual.

### 1.2 Tujuan Produk
Membangun aplikasi web yang memungkinkan pengguna untuk mengunggah file jaringan EPANET (`.inp`), lalu sistem akan secara otomatis menganalisis dan mengiterasi diameter pipa hingga memenuhi standar kriteria hidrolis resmi. Setelah selesai, pengguna dapat mengunduh file `.inp` hasil optimasi.

## 2. Ruang Lingkup (Scope)
### 2.1 In Scope (Cakupan Fitur)
- **Upload File:** Menerima unggahan file input EPANET berformat `.inp`.
- **Parsing & Simulasi:** Membaca file `.inp` dan menjalankan simulasi hidrolis menggunakan library **WNTR** dan **EPyT** di Python.
- **Kondisi Simulasi:** Analisis dilakukan secara *steady-state* / kondisi awal pada waktu simulasi $t=0$.
- **Mesin Optimasi (Auto-Iterate):** 
  - Melakukan iterasi penggantian diameter pipa secara otomatis.
  - Menggunakan daftar ukuran standar pipa komersial: **40 mm hingga 315 mm**.
  - Mengulang simulasi setiap kali ada perubahan diameter hingga seluruh kriteria terpenuhi atau algoritma mencapai titik konvergen (batas maksimal iterasi).
- **Evaluasi Standar:** Mengevaluasi kondisi hidrolis berdasarkan regulasi yang berlaku.
- **Download Hasil:** Menyediakan file `.inp` baru yang diameternya telah dioptimasi untuk diunduh.

### 2.2 Out of Scope (Di Luar Cakupan)
- **Extended Period Simulation (EPS):** Sistem tidak melakukan optimasi berbasis profil pola waktu (EPS). Untuk analisis EPS secara penuh, pengguna harus menggunakan EPANET Desktop.
- **Pembuatan Topologi Jaringan:** Sistem tidak menyediakan fitur menggambar jaringan dari awal.
- **Optimasi Komponen Non-Pipa:** Sistem tidak mengoptimalkan pengaturan pompa, dimensi tangki, atau status valve. Hanya diameter pipa yang diiterasi.

## 3. Kriteria Evaluasi & Batasan (Constraints)
Setiap iterasi akan dievaluasi ketat berdasarkan **Permen PU No. 18/PRT/M/2007**:
1. **Tekanan (Pressure):** Antara **10 meter hingga 80 meter** di setiap *junction* (titik simpul).
2. **Kecepatan (Velocity):** Antara **0.3 m/s hingga 2.5 m/s** di setiap pipa.
3. **Headloss (Kehilangan Tekanan):** Maksimal **10 m/km** di setiap pipa.

**Daftar Ukuran Diameter Pipa Standar (Contoh):**
`[40, 50, 63, 75, 90, 110, 160, 200, 250, 315] mm`
*(Daftar ini akan digunakan oleh algoritma untuk melakukan *upsizing* atau *downsizing* ukuran pipa).*

## 4. Kebutuhan Fungsional (Functional Requirements)
### 4.1 Modul Input
- **FR-01:** Sistem harus menyediakan form *Drag & Drop* atau tombol Browse untuk mengunggah file `.inp`.
- **FR-02:** Sistem harus memvalidasi ekstensi file file dan memastikan file dapat diparsing oleh WNTR/EPyT.

### 4.2 Modul Simulasi & Evaluasi
- **FR-03:** Sistem harus mampu menjalankan simulasi hidrolis basis (baseline) pada jam ke-0 ($t=0$).
- **FR-04:** Sistem harus memetakan dan menandai *junction* atau *pipe* yang melanggar batas Permen PU.

### 4.3 Modul Iterasi Otomatis (Optimizer)
- **FR-05:** Sistem memiliki algoritma iteratif untuk memperbaiki pelanggaran:
  - Jika tekanan $< 10$ m atau headloss $> 10$ m/km, atau kecepatan $> 2.5$ m/s, sistem akan melakukan *upsize* diameter pipa yang terkait ke standar di atasnya.
  - Jika kecepatan $< 0.3$ m/s dan tekanan masih aman, sistem akan mencoba melakukan *downsize* pipa ke standar di bawahnya untuk efisiensi biaya.
- **FR-06:** Sistem menjalankan simulasi ulang pasca modifikasi diameter.
- **FR-07:** Sistem membatasi jumlah *loop* iterasi (misal maksimal 50-100 iterasi) untuk menghindari *infinite loop* jika jaringan mustahil untuk memenuhi kriteria hidrolis.

### 4.4 Modul Output & Pelaporan
- **FR-08:** Setelah proses selesai/konvergen, sistem menampilkan *Dashboard Summary* yang berisi:
  - Status keberhasilan optimasi (Sukses / Sukses Sebagian / Gagal).
  - Jumlah total iterasi yang dilakukan.
  - Jumlah pipa yang diubah ukurannya.
- **FR-09:** Sistem menyediakan tombol untuk mengunduh hasil akhir jaringan dalam format `.inp`.

## 5. Kebutuhan Non-Fungsional (Non-Functional Requirements)
- **NFR-01 (Kinerja Backend):** Karena proses iterasi simulasi bisa memakan waktu untuk jaringan yang sangat besar, backend harus memproses optimasi ini secara asinkronus (menggunakan Task Queue jika diperlukan, atau WebSocket/Polling) agar *request browser* tidak *timeout*.
- **NFR-02 (Reliabilitas):** Kesalahan dalam satu file `.inp` (misal: jaringan tidak terhubung/disconnected) tidak boleh membuat *server crash*. Harus ada *Exception Handling* yang baik dari engine EPyT/WNTR dan dikembalikan sebagai pesan error ramah pengguna.
- **NFR-03 (UI/UX):** Antarmuka pengguna harus modern, responsif, dan memberikan *feedback* visual yang jelas saat proses komputasi sedang berlangsung (misal: animasi loading *real-time log*).

## 6. Teknologi & Arsitektur
- **Frontend:** HTML/CSS/JS (Vanilla atau Framework) dengan desain yang berfokus pada estetika premium dan responsif (sesuai diskusi UI sebelumnya).
- **Backend:** Python (Flask atau FastAPI).
- **Engine Hidrolika:** 
  - `wntr` (Water Network Tool for Resilience) untuk manipulasi jaringan dan ekstrak properti jaringan.
  - `EPyT` (EPANET Python Toolkit) untuk memanggil API simulasi inti EPANET secara cepat dan efisien dalam *loop* iterasi.
- **Penyimpanan Sementara:** File `.inp` hanya disimpan sementara di *memory* atau folder *temp* lokal selama proses berlangsung, kemudian dihapus setelah diunduh (untuk menjaga privasi data).

## 7. Gambaran User Flow
1. Pengguna membuka halaman aplikasi web.
2. Pengguna mengunggah file desain jaringan `network.inp`.
3. Pengguna menekan tombol **"Mulai Optimasi"**.
4. Layar menampilkan indikator pemrosesan: *"Menganalisis t=0...", "Melakukan Iterasi ke-1...", "Menyesuaikan 12 Pipa..."*.
5. Setelah selesai, layar menampilkan Ringkasan Hasil.
6. Pengguna mengklik **"Download .inp Hasil"**.
7. Pengguna dapat membuka `.inp` yang baru di aplikasi desktop EPANET jika ingin menjalankan EPS.
