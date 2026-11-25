import os
import sys
import json
import base64
import time
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from nlp.preprocessor import IndonesianNLPPreprocessor
from ml.vectorizer import IndonesianTfidfVectorizer
from ml.classifier import MultinomialNaiveBayes
from ml.xai import ExplainableAIEngine
from services.scraper import NewsWebScraper
from services.ocr_service import OCRService
from services.feedback_service import DatabaseService

# Load persistent models
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_PATH = os.path.join(BASE_DIR, "backend", "model_weights.json")
DB_PATH = os.path.join(BASE_DIR, "backend", "database.db")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Inisialisasi komponen sistem
preprocessor = IndonesianNLPPreprocessor(enable_stemming=True)
scraper_service = NewsWebScraper(timeout=10)
ocr_service = OCRService()
db_service = DatabaseService(DB_PATH)

vectorizer = None
classifier = None
xai_engine = None
model_metadata = {}

def load_model():
    global vectorizer, classifier, xai_engine, model_metadata
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        vectorizer = IndonesianTfidfVectorizer.from_dict(data["vectorizer"])
        classifier = MultinomialNaiveBayes.from_dict(data["classifier"])
        xai_engine = ExplainableAIEngine(vectorizer, classifier)
        model_metadata = {
            "version": data.get("version", "1.0.0"),
            "trained_at": data.get("trained_at", ""),
            "best_params": data.get("best_params", {}),
            "metrics": data.get("metrics_scenario_4", {}),
            "all_scenarios": data.get("all_scenarios", {})
        }
        print(f"[*] Model MNB & XAI berhasil dimuat ke memori ({vectorizer.n_features} fitur N-gram).")
    else:
        print("[!] File model_weights.json belum ditemukan. Menjalankan training otomatis...")
        from train_model import train
        train()
        load_model()

load_model()

class AppRequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _send_json(self, status_code: int, data: dict):
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # 1. API: Riwayat Klasifikasi
        if path == "/api/v1/history":
            logs = db_service.get_recent_logs(limit=20)
            self._send_json(200, {"success": True, "data": logs})
            return

        # 2. API: Metrik Model & Eksperimen
        if path == "/api/v1/model/metrics":
            db_metrics = db_service.get_latest_model_metrics()
            self._send_json(200, {
                "success": True,
                "current_model": model_metadata,
                "database_record": db_metrics
            })
            return

        # 3. API: Trending Hoaks Stats
        if path == "/api/v1/trending":
            logs = db_service.get_recent_logs(limit=50)
            total = len(logs)
            hoax_count = sum(1 for l in logs if l.get("predicted_label") == "HOAKS")
            fact_count = total - hoax_count
            self._send_json(200, {
                "success": True,
                "total_inspected": total,
                "hoax_detected": hoax_count,
                "fact_verified": fact_count
            })
            return

        # 4. Layani File Statis Frontend (Aplikasi Mobile Web / PWA)
        if path == "/" or path == "":
            file_path = os.path.join(FRONTEND_DIR, "index.html")
        else:
            rel_path = path.lstrip("/").replace("/", os.sep)
            file_path = os.path.join(FRONTEND_DIR, rel_path)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"
            
            with open(file_path, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-Type", f"{mime_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(content)
        else:
            self._send_json(404, {"error": "Halaman atau endpoint tidak ditemukan."})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Baca Body Request
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)

        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {}

        # 1. POST /api/v1/auth/login
        if path == "/api/v1/auth/login":
            email = body.get("email", "")
            password = body.get("password", "")
            # Simulasi autentikasi JWT token
            token = f"jwt_token_demo_{int(time.time())}"
            self._send_json(200, {
                "success": True,
                "message": "Autentikasi berhasil.",
                "token": token,
                "user": {
                    "id": "usr-demo-001",
                    "email": email or "user@tugas.mobile",
                    "name": "Pengguna Mobile",
                    "role": "researcher" if "admin" in email else "user"
                }
            })
            return

        # 2. POST /api/v1/classify/text (Rute Inti)
        if path == "/api/v1/classify/text":
            title = body.get("title", "").strip()
            content = body.get("content", "").strip()

            if not title and not content:
                self._send_json(400, {"success": False, "error": "Judul atau isi berita wajib diisi."})
                return

            full_text = f"{title} {title} {content}"  # Beri penekanan leksikal pada judul clickbait
            result = self._perform_classification(title, content, full_text, source_type="text")
            self._send_json(200, {"success": True, "data": result})
            return

        # 3. POST /api/v1/classify/url (URL Web Scraper)
        if path == "/api/v1/classify/url":
            url = body.get("url", "").strip()
            if not url:
                self._send_json(400, {"success": False, "error": "Parameter URL wajib disertakan."})
                return

            scrape_res = scraper_service.scrape_url(url)
            if not scrape_res["success"] and not scrape_res.get("content"):
                self._send_json(422, {"success": False, "error": scrape_res.get("error", "Gagal memproses URL")})
                return

            title = scrape_res.get("title", "")
            content = scrape_res.get("content", "")
            full_text = f"{title} {title} {content}"

            result = self._perform_classification(title, content, full_text, source_type="url")
            result["scraped_metadata"] = {
                "source_url": url,
                "paragraph_count": scrape_res.get("paragraph_count", 0)
            }
            self._send_json(200, {"success": True, "data": result})
            return

        # 4. POST /api/v1/classify/image (OCR Image / Screenshot Scanner)
        if path == "/api/v1/classify/image":
            image_b64 = body.get("image_base64", "")
            image_bytes = b""
            if image_b64:
                try:
                    if "," in image_b64:
                        image_b64 = image_b64.split(",")[1]
                    image_bytes = base64.b64decode(image_b64)
                except Exception:
                    pass

            ocr_res = ocr_service.process_image_and_extract_text(
                image_bytes,
                filename=body.get("filename", "screenshot.jpg")
            )
            title = ocr_res.get("title", "")
            content = ocr_res.get("content", "")
            full_text = f"{title} {title} {content}"

            result = self._perform_classification(title, content, full_text, source_type="ocr_image")
            result["ocr_metadata"] = {
                "filename": ocr_res.get("filename"),
                "pipeline_applied": ocr_res.get("pipeline_applied"),
                "character_accuracy": ocr_res.get("estimated_character_accuracy")
            }
            self._send_json(200, {"success": True, "data": result})
            return

        # 5. POST /api/v1/feedbacks (Crowdsourced Feedback)
        if path == "/api/v1/feedbacks":
            log_id = body.get("log_id", "")
            feedback_type = body.get("feedback_type", "disagree")
            user_verdict = body.get("user_verdict", "FAKTA")
            notes = body.get("notes", "")

            fid = db_service.save_feedback(log_id, feedback_type, user_verdict, notes)
            self._send_json(200, {
                "success": True,
                "message": "Sanggahan/umpan balik berhasil disimpan ke repositori crowdsourcing.",
                "feedback_id": fid
            })
            return

        # 6. POST /api/v1/research/train (Re-train Engine)
        if path == "/api/v1/research/train":
            from train_model import train
            train()
            load_model()
            self._send_json(200, {
                "success": True,
                "message": "Pelatihan ulang model MNB berhasil diselesaikan secara asinkron.",
                "model_metadata": model_metadata
            })
            return

        self._send_json(404, {"error": "Endpoint tidak valid."})

    def _perform_classification(self, title: str, content: str, full_text: str, source_type: str = "text") -> dict:
        # Preprocessing Teks
        prep_res = preprocessor.preprocess(full_text)
        tokens = prep_res["tokens"]

        # Vektorisasi TF-IDF
        vec_features = vectorizer.transform([tokens])

        # Prediksi MNB & Probabilitas Posterior Terkalibrasi
        predicted_label = classifier.predict(vec_features)[0]
        probas = classifier.predict_proba(vec_features)[0]

        hoax_score = probas.get("HOAKS", 0.5)
        fact_score = probas.get("FAKTA", 0.5)

        # XAI Explanation (LIME Feature Weights)
        explanation = xai_engine.explain_instance(tokens, top_k=8)

        # Skala Kepercayaan & Risiko
        confidence = round(max(hoax_score, fact_score) * 100, 1)
        if predicted_label == "HOAKS":
            risk_level = "Tinggi (Bahaya Hoaks)" if hoax_score > 0.70 else "Sedang (Waspada Misinformasi)"
        else:
            risk_level = "Rendah (Berita Kredibel / Faktual)" if fact_score > 0.70 else "Verifikasi Lanjut Disarankan"

        # Simpan jejak audit ke basis data relasional SQLite
        log_id = db_service.save_log(
            title=title,
            content=content,
            cleansed_text=prep_res["cleaned_text"],
            predicted_label=predicted_label,
            hoax_score=round(hoax_score, 4),
            fact_score=round(fact_score, 4),
            xai_metadata=explanation,
            source_type=source_type
        )

        return {
            "log_id": log_id,
            "title": title,
            "content_preview": (content[:160] + "...") if len(content) > 160 else content,
            "predicted_label": predicted_label,
            "hoax_probability": round(hoax_score, 4),
            "fact_probability": round(fact_score, 4),
            "hoax_percentage": round(hoax_score * 100, 1),
            "fact_percentage": round(fact_score * 100, 1),
            "confidence_percent": confidence,
            "risk_level": risk_level,
            "tokens_count": len(tokens),
            "cleansed_text": prep_res["cleaned_text"],
            "explanation": explanation,
            "source_type": source_type,
            "evaluated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

def run_server(port: int = 8080):
    candidate_ports = [port, 8000, 5000, 3000, 8888, 8085]
    httpd = None
    selected_port = port
    for p in candidate_ports:
        try:
            server_address = ("0.0.0.0", p)
            httpd = HTTPServer(server_address, AppRequestHandler)
            selected_port = p
            break
        except OSError as e:
            print(f"[!] Port {p} tidak dapat digunakan ({e}), mencoba port cadangan...", flush=True)

    if not httpd:
        print("[X] Gagal mengikat port jaringan.", flush=True)
        return

    print("=" * 70, flush=True)
    print(f"[*] Server REST API & Mobile Web App Aktif di: http://127.0.0.1:{selected_port}", flush=True)
    print(f"[*] Dokumentasi Endpoint API:", flush=True)
    print(f"    - POST /api/v1/classify/text   (Klasifikasi Teks Bebas + XAI)", flush=True)
    print(f"    - POST /api/v1/classify/url    (Scraping Tautan Web Berita)", flush=True)
    print(f"    - POST /api/v1/classify/image  (Ekstraksi Gambar/Screenshot OCR)", flush=True)
    print(f"    - POST /api/v1/feedbacks       (Pelaporan Crowdsourcing Sanggahan)", flush=True)
    print(f"    - GET  /api/v1/history         (Riwayat Audit Pemeriksaan)", flush=True)
    print(f"    - GET  /api/v1/model/metrics   (Metrik 10-Fold CV & Hyperparameter)", flush=True)
    print(f"    - GET  /                       (Antarmuka Aplikasi Mobile PWA)", flush=True)
    print("=" * 70, flush=True)
    print(f"[*] Tekan CTRL+C untuk menghentikan server.", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Mematikan server...", flush=True)
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
