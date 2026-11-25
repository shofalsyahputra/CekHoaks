import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../constants/app_colors.dart';

class SpeedometerGauge extends StatelessWidget {
  final double percentage;
  final bool isHoax;

  const SpeedometerGauge({
    Key? key,
    required this.percentage,
    required this.isHoax,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final activeColor = isHoax ? AppColors.hoaxRed : AppColors.factGreen;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: 200,
          height: 110,
          child: CustomPaint(
            painter: _SpeedometerPainter(
              percentage: percentage,
              activeColor: activeColor,
            ),
          ),
        ),
        Transform.translate(
          offset: const Offset(0, -20),
          child: Column(
            children: [
              Text(
                '${percentage.toStringAsFixed(1)}%',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                  color: activeColor,
                ),
              ),
              Text(
                isHoax ? 'Probabilitas Hoaks' : 'Validitas Fakta',
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textMuted,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _SpeedometerPainter extends CustomPainter {
  final double percentage;
  final Color activeColor;

  _SpeedometerPainter({required this.percentage, required this.activeColor});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height);
    final radius = size.width / 2 - 16;
    const strokeWidth = 14.0;

    // Background Arc (Semi-circle from 180° to 360°)
    final bgPaint = Paint()
      ..color = const Color(0xFFE2E8F0)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      math.pi,
      math.pi,
      false,
      bgPaint,
    );

    // Active Score Arc
    final activePaint = Paint()
      ..color = activeColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    final sweepAngle = (percentage / 100.0) * math.pi;
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      math.pi,
      sweepAngle,
      false,
      activePaint,
    );
  }

  @override
  bool shouldRepaint(covariant _SpeedometerPainter oldDelegate) {
    return oldDelegate.percentage != percentage || oldDelegate.activeColor != activeColor;
  }
}

