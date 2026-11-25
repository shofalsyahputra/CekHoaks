import 'package:flutter/material.dart';
import '../models/news_classification.dart';
import '../constants/app_colors.dart';

class XaiKeywordCard extends StatelessWidget {
  final List<ExplainingTerm> terms;

  const XaiKeywordCard({Key? key, required this.terms}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (terms.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: const [
            Icon(Icons.lightbulb_outline, size: 18, color: AppColors.primary),
            SizedBox(width: 6),
            Text(
              'Kata Kunci Pemicu Keputusan AI (XAI):',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w700,
                color: AppColors.textMain,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 6,
          runSpacing: 6,
          children: terms.map((term) {
            final isHoaxTerm = term.direction == 'HOAKS';
            final chipBg = isHoaxTerm ? AppColors.hoaxRedBg : AppColors.factGreenBg;
            final chipColor = isHoaxTerm ? AppColors.hoaxRed : AppColors.factGreen;

            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: chipBg,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: isHoaxTerm ? const Color(0xFFFCA5A5) : const Color(0xFF6EE7B7),
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    term.term,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: chipColor,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Container(
                    width: (term.impactPercent * 0.35).clamp(8.0, 30.0),
                    height: 5,
                    decoration: BoxDecoration(
                      color: chipColor.withOpacity(0.6),
                      borderRadius: BorderRadius.circular(3),
                    ),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    isHoaxTerm ? '+H' : '+F',
                    style: TextStyle(
                      fontSize: 9,
                      fontWeight: FontWeight.bold,
                      color: chipColor.withOpacity(0.8),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}

