import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/news_classification.dart';

class ApiService {
  // Ganti IP dengan IP LAN mesin Anda saat pengujian di perangkat Android fisik
  static const String baseUrl = 'http://10.0.2.2:8080/api/v1'; // Default emulator Android

  static Future<ClassificationResult> classifyText(String title, String content) async {
    final url = Uri.parse('$baseUrl/classify/text');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'title': title, 'content': content}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return ClassificationResult.fromJson(data['data']);
    } else {
      throw Exception('Gagal melakukan klasifikasi teks: ${response.statusCode}');
    }
  }

  static Future<ClassificationResult> classifyUrl(String newsUrl) async {
    final url = Uri.parse('$baseUrl/classify/url');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'url': newsUrl}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return ClassificationResult.fromJson(data['data']);
    } else {
      throw Exception('Gagal mengekstrak berita dari URL: ${response.statusCode}');
    }
  }

  static Future<ClassificationResult> classifyImage(String base64Image, String filename) async {
    final url = Uri.parse('$baseUrl/classify/image');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'image_base64': base64Image, 'filename': filename}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return ClassificationResult.fromJson(data['data']);
    } else {
      throw Exception('Gagal memproses gambar OCR: ${response.statusCode}');
    }
  }

  static Future<bool> sendFeedback(String logId, String type, String verdict, String notes) async {
    final url = Uri.parse('$baseUrl/feedbacks');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'log_id': logId,
        'feedback_type': type,
        'user_verdict': verdict,
        'notes': notes,
      }),
    );
    return response.statusCode == 200;
  }
}

