# CekHoaks Mobile - Proyek Aplikasi Flutter (Tugas Mobile)

Aplikasi mobile deteksi dini berita hoaks dan non-hoaks (fakta) berbahasa Indonesia berbasis **Multinomial Naive Bayes (MNB)**, **TF-IDF N-gram (1,2) Spasial L2-Norm**, dan **Explainable AI (XAI)**.

## 🚀 Fitur Unggulan Mobile
1. **Hero Tripartite Input**:
   - Tab 1: Input Teks Bebas (Judul Berita & Isi Paragraf)
   - Tab 2: URL Web Scraper otomatis
   - Tab 3: Pemindai Kamera & Galeri (OCR Preprocessing: CLAHE, Binarization)
2. **Speedometer Probabilitas Psikologis**:
   - Merah Pekat (`#DC2626`) untuk indikasi Hoaks
   - Hijau Zamrud (`#059669`) untuk validitas Fakta Kredibel
3. **Visualisasi Explainable AI (XAI)**:
   - Menyoroti token/kata kunci pemicu probabilitas dengan bar dampak
4. **Shareable Fact Card**:
   - Membagikan hasil verifikasi fakta langsung ke WhatsApp & Media Sosial
5. **Penyimpanan Offline (SQLite)**:
   - Menyimpan riwayat pemeriksaan tanpa ketergantungan koneksi internet
6. **Modul Pengujian Usabilitas SUS (System Usability Scale)**:
   - Kalkulator 10 pertanyaan Likert dengan ambang batas kelulusan skor > 68.

## Menjalankan Aplikasi

Jalankan perintah dari folder `mobile_app`:

```powershell
cd mobile_app
flutter pub get
```

### Web (Chrome atau Edge)

```powershell
flutter run -d chrome
```

Ganti `chrome` menjadi `edge` jika ingin menggunakan Microsoft Edge.

### Windows desktop

Pastikan Visual Studio sudah terpasang dengan workload **Desktop development with C++**. Jika Flutter meminta symlink support, aktifkan **Developer Mode** Windows (Settings → System → For developers), lalu jalankan:

```powershell
flutter run -d windows
```

### Android

Jalankan aplikasi di emulator atau perangkat Android yang terhubung:

```powershell
flutter run
```

Untuk memeriksa perangkat yang dikenali Flutter, gunakan `flutter devices`.

### Backend (untuk fitur klasifikasi)

Di terminal kedua, dari folder root repository (satu tingkat di atas `mobile_app`), jalankan:

```powershell
python backend/api/server.py 8080
```

> **Catatan jaringan Android Emulator:** Backend URL disetel ke `http://10.0.2.2:8080` (alamat loopback bawaan Android Emulator ke host PC). Jika menggunakan perangkat Android fisik melalui kabel USB atau WiFi, ganti konstanta `baseUrl` di file `lib/services/api_service.dart` dengan alamat IP lokal komputer Anda (misal `http://192.168.1.xxx:8080`).

