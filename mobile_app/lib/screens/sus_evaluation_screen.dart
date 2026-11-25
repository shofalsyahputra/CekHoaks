import 'package:flutter/material.dart';
import '../constants/app_colors.dart';

class SusEvaluationScreen extends StatefulWidget {
  const SusEvaluationScreen({Key? key}) : super(key: key);

  @override
  State<SusEvaluationScreen> createState() => _SusEvaluationScreenState();
}

class _SusEvaluationScreenState extends State<SusEvaluationScreen> {
  final List<String> _questions = [
    '1. Saya berpikir akan sering menggunakan aplikasi CekHoaks ini.',
    '2. Saya merasa sistem ini terlalu rumit untuk digunakan.',
    '3. Saya merasa antarmuka aplikasi ini sangat mudah digunakan.',
    '4. Saya merasa butuh bantuan orang lain untuk menggunakan sistem ini.',
    '5. Fitur-fitur dalam sistem ini terintegrasi dengan sangat baik.',
    '6. Saya merasa ada banyak ketidakkonsistenan pada sistem ini.',
    '7. Sebagian besar orang dapat belajar menggunakan sistem ini dengan sangat cepat.',
    '8. Saya merasa sistem ini sangat janggal atau membingungkan saat digunakan.',
    '9. Saya merasa sangat percaya diri saat menggunakan sistem ini.',
    '10. Saya perlu mempelajari banyak hal baru sebelum dapat mengoperasikan sistem ini.',
  ];

  final List<int> _scores = [5, 1, 5, 1, 5, 1, 5, 1, 5, 1]; // Default answers
  double? _calculatedScore;
  String _grade = '';

  void _calculateScore() {
    // Formula SUS:
    // Ganjil (index 0, 2, 4, 6, 8): score - 1
    // Genap (index 1, 3, 5, 7, 9): 5 - score
    // Total dikali 2.5
    double total = 0.0;
    for (int i = 0; i < 10; i++) {
      if (i % 2 == 0) {
        total += (_scores[i] - 1);
      } else {
        total += (5 - _scores[i]);
      }
    }
    final sus = total * 2.5;

    String g = '';
    if (sus >= 85) {
      g = 'Grade A (Excellent) - Sangat Dapat Diterima';
    } else if (sus >= 68) {
      g = 'Grade B (Good) - Lolos Batas Ambang (> 68)';
    } else if (sus >= 51) {
      g = 'Grade C (OK) - Marginal (Perlu Optimasi UX)';
    } else {
      g = 'Grade F (Poor) - Not Acceptable';
    }

    setState(() {
      _calculatedScore = sus;
      _grade = g;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Uji Usabilitas SUS'),
        backgroundColor: AppColors.primaryDark,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: const Text(
                'Metodologi Usability Testing System Usability Scale (SUS) dengan 10 daftar periksa Likert. Ambang batas toleransi desain sistem: skor > 68.',
                style: TextStyle(fontSize: 12, color: Color(0xFF1E3A8A)),
              ),
            ),
            const SizedBox(height: 16),

            ...List.generate(10, (idx) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _questions[idx],
                      style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                    ),
                    const SizedBox(height: 6),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('STS (1)', style: TextStyle(fontSize: 10, color: AppColors.textMuted)),
                        ...List.generate(5, (val) {
                          final scoreVal = val + 1;
                          return Row(
                            children: [
                              Radio<int>(
                                value: scoreVal,
                                groupValue: _scores[idx],
                                onChanged: (v) {
                                  setState(() => _scores[idx] = v!);
                                },
                              ),
                              Text('$scoreVal', style: const TextStyle(fontSize: 12)),
                            ],
                          );
                        }),
                        const Text('SS (5)', style: TextStyle(fontSize: 10, color: AppColors.textMuted)),
                      ],
                    ),
                    const Divider(),
                  ],
                ),
              );
            }),

            ElevatedButton(
              onPressed: _calculateScore,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              child: const Text('Hitung Skor SUS'),
            ),

            if (_calculatedScore != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.primary, width: 2),
                ),
                child: Column(
                  children: [
                    const Text('Skor Usabilitas Terhitung:', style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                    const SizedBox(height: 4),
                    Text(
                      _calculatedScore!.toStringAsFixed(1),
                      style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w900, color: AppColors.primary),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _grade,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.factGreen),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

