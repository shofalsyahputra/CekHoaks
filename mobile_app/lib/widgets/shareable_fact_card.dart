import 'package:flutter/material.dart';
import 'package:share_plus/share_plus.dart';
import '../models/news_classification.dart';
import '../constants/app_colors.dart';

class ShareableFactCard extends StatelessWidget {
  final ClassificationResult result;

  const ShareableFactCard({Key? key, required this.result}) : super(key: key);

  void _shareViaText() {
    final verdict = result.isHoax ? '🚨 TERINDIKASI HOAKS' : '✅ BERITA FAKTA / RESMI';
    final pct = result.isHoax ? result.hoaxPercentage : result.factPercentage;
    final topTerms = result.topTerms.take(4).map((e) => e.term).join(', ');

    final shareContent = '''
[CEK FAKTA INDONESIA]
Status: $verdict
Judul: "${result.title}"
Tingkat Probabilitas: $pct% (${result.riskLevel})
Kata Kunci Pemicu: $topTerms

Verifikasi mandiri menggunakan CekHoaks Mobile AI. Saring sebelum sharing!
''';

    Share.share(shareContent, subject: 'Hasil Verifikasi Fakta Berita');
  }

  @override
  Widget build(BuildContext context) {
    final isHoax = result.isHoax;

    return Column(
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF1E1B4B), Color(0xFF0F172A)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.15),
                blurRadius: 16,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    '🛡️ CEKHOAKS VERIFIKASI RESMI',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF94A3B8),
                    ),
                  ),
                  Text(
                    '${isHoax ? result.hoaxPercentage : result.factPercentage}% Akurasi',
                    style: const TextStyle(
                      fontSize: 10,
                      color: Color(0xFF94A3B8),
                    ),
                  ),
                ],
              ),
              const Divider(color: Colors.white12, height: 16),
              Text(
                isHoax ? '⚠️ PERINGATAN HOAKS' : '✅ TERVERIFIKASI FAKTA',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                  color: isHoax ? const Color(0xFFF87171) : const Color(0xFF34D399),
                ),
              ),
              const SizedBox(height: 6),
              Text(
                '"${result.title}"',
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                  height: 1.3,
                ),
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: const [
                  Text(
                    'Saring Sebelum Sharing',
                    style: TextStyle(fontSize: 10, color: Color(0xFF64748B)),
                  ),
                  Text(
                    'Multinomial Naive Bayes AI',
                    style: TextStyle(fontSize: 10, color: Color(0xFF64748B)),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 10),
        ElevatedButton.icon(
          onPressed: _shareViaText,
          icon: const Icon(Icons.share, size: 16),
          label: const Text('Bagikan Hasil Verifikasi Fakta (WhatsApp / Medsos)'),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primary,
            foregroundColor: Colors.white,
            minimumSize: const Size(double.infinity, 44),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
        ),
      ],
    );
  }
}

