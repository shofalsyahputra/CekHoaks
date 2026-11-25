import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import '../constants/app_colors.dart';
import '../services/api_service.dart';
import '../services/local_db_service.dart';
import 'result_screen.dart';
import 'history_screen.dart';
import 'sus_evaluation_screen.dart';
import 'about_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  static const _shareChannel = MethodChannel('com.tugasmobile.cekhoaks/share');

  // Controllers
  final _titleController = TextEditingController();
  final _contentController = TextEditingController();
  final _urlController = TextEditingController();

  XFile? _selectedImage;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _checkIncomingSharedText();
  }

  Future<void> _checkIncomingSharedText() async {
    try {
      final String? shared = await _shareChannel.invokeMethod('getSharedText');
      if (shared != null && shared.isNotEmpty) {
        setState(() {
          _contentController.text = shared;
          _tabController.index = 0;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Pesan dari aplikasi lain berhasil disematkan!')),
        );
      }
    } catch (_) {}
  }

  void _loadPreset(String type) {
    if (type == 'hoax-politik') {
      _titleController.text = 'Awas Konspirasi! KPU Diam-Diam Memanipulasi Jutaan Suara Pemilu Lewat Server Luar Negeri';
      _contentController.text = 'Sebarkanlah informasi penting ini ke seluruh rakyat Indonesia! Telah terbongkar konspirasi busuk penyelenggara pemilu. KPU diam-diam mengalihkan jutaan suara melalui server ilegal di luar negeri. Boikot hasil perhitungan suara!';
    } else if (type == 'hoax-vaksin') {
      _titleController.text = 'Kabar Duka: Vaksin Baru Mengandung Mikrocip Pengendali Otak Buatan Elit Global';
      _contentController.text = 'Dokter rahasia membocorkan dokumen bahwa vaksin disusupi racun dan mikrocip pelacak magnetik. Banyak korban berjatuhan setelah divaksinasi. Pemerintah menutup-nutupi demi keuntungan. Bagikan segera!';
    } else if (type == 'fakta-kemenkes') {
      _titleController.text = 'Kementerian Kesehatan Tegaskan Vaksin Teruji Klinis Aman Sesuai Standar BPOM dan WHO';
      _contentController.text = 'Kementerian Kesehatan RI dan BPOM menegaskan seluruh vaksin yang beredar telah melalui pengujian klinis berstandar internasional. Narasi zat berbahaya adalah disinformasi tanpa dasar ilmiah.';
    }
  }

  Future<void> _processTextClassification() async {
    final title = _titleController.text.trim();
    final content = _contentController.text.trim();
    if (title.isEmpty && content.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Silakan masukkan judul atau isi berita!')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final res = await ApiService.classifyText(title, content);
      await LocalDbService.saveHistory(res);
      if (mounted) {
        Navigator.push(context, MaterialPageRoute(builder: (_) => ResultScreen(result: res)));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Gagal: $e')),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _processUrlClassification() async {
    final url = _urlController.text.trim();
    if (url.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Masukkan URL portal berita!')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final res = await ApiService.classifyUrl(url);
      await LocalDbService.saveHistory(res);
      if (mounted) {
        Navigator.push(context, MaterialPageRoute(builder: (_) => ResultScreen(result: res)));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Gagal mengekstrak URL: $e')),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final img = await picker.pickImage(source: source);
    if (img != null) {
      setState(() => _selectedImage = img);
    }
  }

  Future<void> _processImageClassification() async {
    if (_selectedImage == null) return;
    setState(() => _isLoading = true);
    try {
      final bytes = await _selectedImage!.readAsBytes();
      final base64Img = base64Encode(bytes);
      final res = await ApiService.classifyImage(base64Img, _selectedImage!.name);
      await LocalDbService.saveHistory(res);
      if (mounted) {
        Navigator.push(context, MaterialPageRoute(builder: (_) => ResultScreen(result: res)));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Gagal memproses OCR citra: $e')),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('CekHoaks AI'),
        backgroundColor: AppColors.primaryDark,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            tooltip: 'Riwayat Audit',
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const HistoryScreen()),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.rate_review),
            tooltip: 'Uji Usabilitas SUS',
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const SusEvaluationScreen()),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.info_outline, color: Colors.white),
            onPressed: () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const AboutScreen()));
            },
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(icon: Icon(Icons.text_fields), text: 'Teks Bebas'),
            Tab(icon: Icon(Icons.link), text: 'URL Scraper'),
            Tab(icon: Icon(Icons.camera_alt), text: 'OCR Gambar'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 12),
                  Text('Menganalisis Probabilitas Posterior & XAI...'),
                ],
              ),
            )
          : TabBarView(
              controller: _tabController,
              children: [
                // Tab 1: Teks Bebas
                SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Wrap(
                        spacing: 6,
                        children: [
                          ActionChip(
                            label: const Text('🚨 Hoaks KPU', style: TextStyle(fontSize: 11)),
                            onPressed: () => _loadPreset('hoax-politik'),
                          ),
                          ActionChip(
                            label: const Text('⚠️ Hoaks Vaksin', style: TextStyle(fontSize: 11)),
                            onPressed: () => _loadPreset('hoax-vaksin'),
                          ),
                          ActionChip(
                            label: const Text('✅ Fakta Kemenkes', style: TextStyle(fontSize: 11)),
                            onPressed: () => _loadPreset('fakta-kemenkes'),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _titleController,
                        decoration: const InputDecoration(
                          labelText: 'Judul Berita (Analisis Clickbait)',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _contentController,
                        maxLines: 5,
                        decoration: const InputDecoration(
                          labelText: 'Isi Paragraf / Teks Pesan',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: _processTextClassification,
                        icon: const Icon(Icons.search),
                        label: const Text('Periksa Validitas Berita'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primary,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                      ),
                    ],
                  ),
                ),

                // Tab 2: URL Scraper
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      TextField(
                        controller: _urlController,
                        decoration: const InputDecoration(
                          labelText: 'Tautan (URL) Berita',
                          hintText: 'https://news.detik.com/...',
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.link),
                        ),
                      ),
                      const SizedBox(height: 10),
                      const Text(
                        'Engine scraper akan mengunduh artikel dan mengekstrak DOM paragraf berita secara otomatis.',
                        style: TextStyle(fontSize: 12, color: AppColors.textMuted),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: _processUrlClassification,
                        icon: const Icon(Icons.travel_explore),
                        label: const Text('Ekstrak & Analisis URL'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primary,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                      ),
                    ],
                  ),
                ),

                // Tab 3: OCR Gambar
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Container(
                        height: 150,
                        decoration: BoxDecoration(
                          color: Colors.grey.shade100,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.grey.shade300, style: BorderStyle.solid),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.image, size: 40, color: AppColors.textMuted),
                            const SizedBox(height: 8),
                            Text(
                              _selectedImage != null
                                  ? 'Terpilih: ${_selectedImage!.name}'
                                  : 'Pilih Screenshot Pesan WA / Foto Berita',
                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: () => _pickImage(ImageSource.camera),
                              icon: const Icon(Icons.camera_alt),
                              label: const Text('Kamera'),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: () => _pickImage(ImageSource.gallery),
                              icon: const Icon(Icons.photo_library),
                              label: const Text('Galeri'),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: _selectedImage == null ? null : _processImageClassification,
                        icon: const Icon(Icons.document_scanner),
                        label: const Text('Pindai Citra & Analisis OCR'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primary,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
    );
  }
}

