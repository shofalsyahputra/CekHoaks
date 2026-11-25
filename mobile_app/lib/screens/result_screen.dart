import 'package:flutter/material.dart';
import '../models/news_classification.dart';
import '../constants/app_colors.dart';
import '../widgets/speedometer_gauge.dart';
import '../widgets/xai_keyword_card.dart';
import '../widgets/shareable_fact_card.dart';
import '../services/api_service.dart';

class ResultScreen extends StatefulWidget {
  final ClassificationResult result;

  const ResultScreen({Key? key, required this.result}) : super(key: key);

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  bool _feedbackSent = false;

  void _sendFeedback(String type) async {
    final noteController = TextEditingController();
    await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(type == 'agree' ? 'Konfirmasi Persetujuan' : 'Sanggah Hasil'),
        content: TextField(
          controller: noteController,
          decoration: const InputDecoration(
            hintText: 'Tuliskan catatan tambahan (opsional)...',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              final success = await ApiService.sendFeedback(
                widget.result.logId,
                type,
                type == 'agree' ? widget.result.predictedLabel : (widget.result.isHoax ? 'FAKTA' : 'HOAKS'),
                noteController.text,
              );
              if (mounted && success) {
                setState(() => _feedbackSent = true);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Terima kasih atas kontribusi validasi Anda!')),
                );
              }
            },
            child: const Text('Kirim'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final res = widget.result;
    final isHoax = res.isHoax;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Hasil Audit Berita'),
        backgroundColor: AppColors.primaryDark,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Status Badge & Verdict
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: BoxDecoration(
                color: isHoax ? AppColors.hoaxRedBg : AppColors.factGreenBg,
                borderRadius: BorderRadius.circular(30),
                border: Border.all(
                  color: isHoax ? const Color(0xFFFECACA) : const Color(0xFFA7F3D0),
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    isHoax ? 'TERINDIKASI HOAKS' : 'BERITA FAKTA / KREDIBEL',
                    style: TextStyle(
                      fontWeight: FontWeight.w800,
                      fontSize: 13,
                      color: isHoax ? AppColors.hoaxRed : AppColors.factGreen,
                    ),
                  ),
                  Text(
                    res.riskLevel,
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textMuted,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Speedometer Gauge Arc
            Center(
              child: SpeedometerGauge(
                percentage: isHoax ? res.hoaxPercentage : res.factPercentage,
                isHoax: isHoax,
              ),
            ),
            const SizedBox(height: 12),

            // Probability Comparison Bar
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppColors.border),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Column(
                    children: [
                      const Text('Skor Hoaks', style: TextStyle(fontSize: 11, color: AppColors.textMuted)),
                      Text(
                        '${res.hoaxPercentage.toStringAsFixed(1)}%',
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.hoaxRed),
                      ),
                    ],
                  ),
                  Container(height: 24, width: 1, color: AppColors.border),
                  Column(
                    children: [
                      const Text('Skor Fakta', style: TextStyle(fontSize: 11, color: AppColors.textMuted)),
                      Text(
                        '${res.factPercentage.toStringAsFixed(1)}%',
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.factGreen),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Explainable AI Keywords
            XaiKeywordCard(terms: res.topTerms),
            const SizedBox(height: 20),

            // Shareable Fact Card
            ShareableFactCard(result: res),
            const SizedBox(height: 20),

            // Crowdsourced Feedback
            if (!_feedbackSent)
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Apakah hasil klasifikasi ini akurat?',
                      style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () => _sendFeedback('agree'),
                            icon: const Icon(Icons.thumb_up, size: 14, color: AppColors.factGreen),
                            label: const Text('Setuju'),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () => _sendFeedback('disagree'),
                            icon: const Icon(Icons.thumb_down, size: 14, color: AppColors.hoaxRed),
                            label: const Text('Sanggah'),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}

