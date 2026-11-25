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

## 📱 Panduan Menjalankan Aplikasi Flutter
1. Pastikan Flutter SDK telah terpasang di komputer Anda.
2. Jalankan perintah instalasi pustaka:
   ```bash
   flutter pub get
   ```
3. Pastikan backend Python telah aktif (`python backend/api/server.py 8080`).
4. Jalankan aplikasi di emulator atau perangkat fisik:
   ```bash
   flutter run
   ```
> **Catatan Jaringan Android Emulator:** Backend URL disetel ke `http://10.0.2.2:8080` (alamat loopback bawaan Android Emulator ke host PC). Jika menggunakan perangkat Android fisik melalui kabel USB atau WiFi, ganti konstanta `baseUrl` di file `lib/services/api_service.dart` dengan alamat IP lokal komputer Anda (misal `http://192.168.1.xxx:8080`).

