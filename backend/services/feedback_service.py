import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

class DatabaseService:
    """
    Manajemen Persistensi Basis Data Relasional SQLite
    Mengimplementasikan skema tabel dari cetak biru arsitektur:
    1. users
    2. classification_logs
    3. user_feedbacks
    4. research_datasets
    5. model_versions
    """
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._init_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Tabel users
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT DEFAULT '',
                role TEXT DEFAULT 'Penyelidik Fakta',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT DEFAULT ''")
            except Exception:
                pass

            # 2. Tabel classification_logs
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS classification_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                input_title TEXT,
                input_content TEXT,
                cleansed_text TEXT,
                predicted_label TEXT,
                hoax_score REAL,
                fact_score REAL,
                xai_metadata TEXT,
                source_type TEXT DEFAULT 'text',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # 3. Tabel user_feedbacks
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedbacks (
                id TEXT PRIMARY KEY,
                log_id TEXT,
                feedback_type TEXT,
                user_verdict TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (log_id) REFERENCES classification_logs (id)
            )
            """)

            # 4. Tabel model_versions
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_versions (
                id TEXT PRIMARY KEY,
                version_tag TEXT,
                accuracy REAL,
                f1_score REAL,
                precision_score REAL,
                recall_score REAL,
                hyperparameters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            conn.commit()

    def save_log(self, title: str, content: str, cleansed_text: str, 
                 predicted_label: str, hoax_score: float, fact_score: float, 
                 xai_metadata: Dict[str, Any], source_type: str = "text") -> str:
        log_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO classification_logs 
            (id, input_title, input_content, cleansed_text, predicted_label, hoax_score, fact_score, xai_metadata, source_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (log_id, title, content, cleansed_text, predicted_label, hoax_score, fact_score, json.dumps(xai_metadata), source_type))
            conn.commit()
        return log_id

    def get_recent_logs(self, limit: int = 15) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM classification_logs 
            ORDER BY created_at DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            logs = []
            for r in rows:
                item = dict(r)
                if item.get("xai_metadata"):
                    try:
                        item["xai_metadata"] = json.loads(item["xai_metadata"])
                    except Exception:
                        pass
                logs.append(item)
            return logs

    def save_feedback(self, log_id: str, feedback_type: str, user_verdict: str, notes: str = "") -> str:
        feedback_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO user_feedbacks (id, log_id, feedback_type, user_verdict, notes)
            VALUES (?, ?, ?, ?, ?)
            """, (feedback_id, log_id, feedback_type, user_verdict, notes))
            conn.commit()
        return feedback_id

    def save_model_version(self, version_tag: str, metrics: Dict[str, Any], hyperparameters: Dict[str, Any]):
        m_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO model_versions 
            (id, version_tag, accuracy, f1_score, precision_score, recall_score, hyperparameters)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (m_id, version_tag, metrics.get("accuracy", 0.0), metrics.get("f1_score", 0.0),
                  metrics.get("precision", 0.0), metrics.get("recall", 0.0), json.dumps(hyperparameters)))
            conn.commit()
        return m_id

    def get_latest_model_metrics(self) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM model_versions ORDER BY created_at DESC LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                res = dict(row)
                if res.get("hyperparameters"):
                    res["hyperparameters"] = json.loads(res["hyperparameters"])
                return res
            return None

    # --- Autentikasi Pengguna (Gmail, Password & Google Auth) ---
    def register_user(self, name: str, email: str, password_hash: str) -> Dict[str, Any]:
        user_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Cek apakah email sudah terdaftar
            cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
            if cursor.fetchone():
                return {"success": False, "error": "Email ini sudah terdaftar. Silakan langsung login."}
            
            cursor.execute("""
            INSERT INTO users (id, email, name, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, email.lower(), name, password_hash, "Penyelidik Fakta"))
            conn.commit()
            
        return {
            "success": True,
            "user": {
                "id": user_id,
                "email": email.lower(),
                "name": name,
                "role": "Penyelidik Fakta",
                "avatar": f"https://api.dicebear.com/7.x/initials/svg?seed={name}"
            }
        }

    def authenticate_user(self, email: str, password_hash: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "Akun dengan email ini belum terdaftar."}
            
            user = dict(row)
            if user.get("password_hash") != password_hash:
                return {"success": False, "error": "Kata sandi yang Anda masukkan salah."}
            
            return {
                "success": True,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "role": user.get("role", "Penyelidik Fakta"),
                    "avatar": f"https://api.dicebear.com/7.x/initials/svg?seed={user['name']}"
                }
            }

    def google_auth_user(self, email: str, name: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
            row = cursor.fetchone()
            if row:
                user = dict(row)
                return {
                    "success": True,
                    "user": {
                        "id": user["id"],
                        "email": user["email"],
                        "name": user["name"],
                        "role": user.get("role", "Penyelidik Fakta Terverifikasi"),
                        "avatar": f"https://api.dicebear.com/7.x/initials/svg?seed={user['name']}"
                    }
                }
            
            # Jika belum ada, daftarkan otomatis via Google
            user_id = str(uuid.uuid4())
            cursor.execute("""
            INSERT INTO users (id, email, name, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, email.lower(), name, "google_oauth_verified", "Penyelidik Fakta Terverifikasi"))
            conn.commit()

            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "email": email.lower(),
                    "name": name,
                    "role": "Penyelidik Fakta Terverifikasi",
                    "avatar": f"https://api.dicebear.com/7.x/initials/svg?seed={name}"
                }
            }

