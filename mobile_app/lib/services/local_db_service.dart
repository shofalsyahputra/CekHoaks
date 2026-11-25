import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/news_classification.dart';

class LocalDbService {
  static Database? _database;

  static Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  static Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'cekhoaks_offline.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE classification_history (
            log_id TEXT PRIMARY KEY,
            title TEXT,
            content_preview TEXT,
            predicted_label TEXT,
            hoax_probability REAL,
            fact_probability REAL,
            hoax_percentage REAL,
            fact_percentage REAL,
            confidence_percent REAL,
            risk_level TEXT,
            source_type TEXT,
            evaluated_at TEXT
          )
        ''');
      },
    );
  }

  static Future<void> saveHistory(ClassificationResult result) async {
    final db = await database;
    await db.insert(
      'classification_history',
      result.toMap(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  static Future<List<ClassificationResult>> getAllHistory() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(
      'classification_history',
      orderBy: 'evaluated_at DESC',
      limit: 30,
    );

    return List.generate(maps.length, (i) {
      return ClassificationResult.fromJson(maps[i]);
    });
  }
}

