import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Tentang Aplikasi',
          style: GoogleFonts.plusJakartaSans(fontWeight: FontWeight.w700),
        ),
        backgroundColor: const Color(0xFF1e1b4b),
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF1e1b4b), Color(0xFF312e81)],
                  ),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Center(
                  child: Text('🛡️', style: TextStyle(fontSize: 40)),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Center(
              child: Text(
                'CekHoaks AI',
                style: GoogleFonts.plusJakartaSans(
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                  color: const Color(0xFF1e1b4b),
                ),
              ),
            ),
            Center(
              child: Text(
                'Versi 1.0.0',
                style: GoogleFonts.plusJakartaSans(
                  fontSize: 13,
                  color: Colors.grey[600],
                ),
              ),
            ),
            const SizedBox(height: 28),
            _buildSection(
              '📖 Deskripsi',
              'Aplikasi mobile cerdas lintas platform untuk deteksi dini berita hoaks berbahasa Indonesia secara real-time. Dibangun menggunakan algoritma Multinomial Naive Bayes (MNB) dengan dukungan Explainable AI (XAI/LIME).',
            ),
            _buildSection(
              '🧠 Teknologi',
              '• Model: Multinomial Naive Bayes\n'
              '• Vektorisasi: TF-IDF N-gram (1,2) L2-Norm\n'
              '• Smoothing: Lidstone Additive (α = 0.5)\n'
              '• NLP: Nazief-Adriani ECS Stemmer\n'
              '• XAI: LIME Feature Attribution\n'
              '• Preprocessing: Negation Preserving',
            ),
            _buildSection(
              '📊 Fitur Utama',
              '• Input tripartit: Teks, URL Scraper, OCR Gambar\n'
              '• Speedometer Arc Psikologis\n'
              '• Kata kunci pemicu (Explainable AI)\n'
              '• Shareable Fact Card untuk WhatsApp\n'
              '• Crowdsourced Feedback Repository\n'
              '• SUS Usability Scale Calculator\n'
              '• Android Share Extension (dari WhatsApp)\n'
              '• Riwayat Audit Offline (SQLite)',
            ),
            _buildSection(
              '📚 Referensi Ilmiah',
              '• McCallum & Nigam (1998) - Multinomial Naive Bayes\n'
              '• Ribeiro et al. (2016) - LIME Explainable AI\n'
              '• Nazief & Adriani (1996) - Indonesian Stemmer\n'
              '• Brooke (1996) - System Usability Scale',
            ),
            _buildSection(
              '🎓 Pengembang',
              'Dikembangkan sebagai proyek Tugas Mobile\nPenerapan Algoritma Multinomial Naive Bayes untuk Klasifikasi Berita Hoaks dan Non-Hoaks',
            ),
            const SizedBox(height: 20),
            Center(
              child: Text(
                '© 2024 CekHoaks AI • Saring Sebelum Sharing',
                style: GoogleFonts.plusJakartaSans(
                  fontSize: 11,
                  color: Colors.grey[500],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(String title, String content) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: GoogleFonts.plusJakartaSans(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: const Color(0xFF1e293b),
            ),
          ),
          const SizedBox(height: 8),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Text(
              content,
              style: GoogleFonts.plusJakartaSans(
                fontSize: 13,
                height: 1.6,
                color: const Color(0xFF475569),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
