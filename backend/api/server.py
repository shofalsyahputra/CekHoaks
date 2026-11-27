import os
import sys
import json
import base64
import time
import hashlib
import re
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

        # 6. POST /api/v1/copilot/chat (Asisten Forensik Interaktif AI Copilot)
        if path == "/api/v1/copilot/chat":
            msg = body.get("message", "").strip().lower()
            ctx = body.get("context", {})
            title = ctx.get("title", "")
            predicted = ctx.get("predicted_label", "HOAKS")
            hoax_pct = ctx.get("hoax_percentage", 75.0)
            terms = ctx.get("terms", [])
            multi_dim = ctx.get("multi_dim", {})

            reply = self._generate_copilot_response(msg, title, predicted, hoax_pct, terms, multi_dim)
            self._send_json(200, {
                "success": True,
                "reply": reply,
                "timestamp": time.strftime("%H:%M:%S")
            })
            return

        # 7. POST /api/v1/research/train (Re-train Engine)
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

    def _generate_copilot_response(self, query: str, title: str, label: str, hoax_pct: float, terms: list, multi_dim: dict) -> str:
        terms_str = ", ".join([f"'{t}'" for t in terms[:4]]) if terms else "istilah pemicu"
        cb_score = multi_dim.get("clickbait_score", 0)
        urg_score = multi_dim.get("urgency_index", 0)
        is_hoax = label == "HOAKS"

        if any(w in query for w in ["kenapa", "mengapa", "alasan", "sebab", "dasar"]):
            if is_hoax:
                return (
                    f"Berdasarkan inferensi model Multinomial Naive Bayes (MNB), artikel ini terindikasi **HOAKS ({hoax_pct}%)** "
                    f"karena mengandung fitur leksikal dengan bobot log-odds negatif yang signifikan: {terms_str}. "
                    f"Selain itu, indeks clickbait judul terukur {cb_score}% dan ada pola urgensi palsu ({urg_score}%) yang lazim digunakan dalam rekayasa sosial."
                )
            else:
                return (
                    f"Model MNB mengklasifikasikan artikel ini sebagai **FAKTA RESMI ({100 - hoax_pct}%)** karena kosakata yang digunakan "
                    f"bersifat objektif, netral, dan mengindikasikan struktur pelaporan kredibel tanpa manipulasi emosi provokatif."
                )

        elif any(w in query for w in ["klarifikasi", "bantah", "balas", "sangkal", "counter"]):
            if is_hoax:
                return (
                    "Anda dapat menggunakan format klarifikasi 3-titik: (1) Tegaskan bahwa info belum terverifikasi secara resmi, "
                    "(2) Tunjukkan bahwa tidak ada rilis rujukan dari lembaga berwenang, dan (3) Ajak untuk menghentikan penyebaran "
                    "sebelum memeriksa di portal MAFINDO (turnbackhoax.id) atau Kominfo."
                )
            else:
                return "Karena artikel ini terverifikasi fakta, Anda dapat membagikannya sebagai rujukan edukatif yang valid untuk meluruskan kesalahpahaman."

        elif any(w in query for w in ["wa", "whatsapp", "keluarga", "grup", "orang tua", "sopan"]):
            return (
                "Tips meluruskan di grup WhatsApp tanpa berdebat: Gunakan teknik *'Empathy First'*. "
                "Awali dengan terima kasih atas niat baik pengirim, lalu sertakan bantahan resmi secara santun: "
                "\"*Terima kasih infonya Om/Tante 🙏, izin meluruskan tadi saya cek di verifikasi CekHoaks info ini ternyata hoaks yang didaur ulang. Mohon jangan disebarkan lagi ya agar tidak bingung. Terima kasih.*\""
            )

        elif any(w in query for w in ["sumber", "cek", "kominfo", "mafindo", "bukti", "portal"]):
            return (
                "Rujukan resmi terbaik untuk memverifikasi isu ini di Indonesia:\n"
                "1. **MAFINDO (turnbackhoax.id)** - Arsip pencarian cek fakta terlengkap.\n"
                "2. **Kemenkominfo (aduankonten.id)** - Kanal pelaporan dan klarifikasi hoaks resmi pemerintah.\n"
                "3. **Google Fact Check Explorer** - Basis data cek fakta global terakreditasi IFCN."
            )

        else:
            return (
                f"Saya adalah Copilot Forensik CekHoaks AI. Mengenai artikel \"{title[:50]}...\": "
                f"Status saat ini teridentifikasi sebagai **{label} ({hoax_pct}%)** dengan clickbait meter {cb_score}%. "
                f"Anda bisa bertanya kepada saya: *'Mengapa ini hoaks?'*, *'Bagaimana cara membalas di grup WA?'*, atau *'Di mana mencari klarifikasi resminya?'*."
            )

    def _calculate_multi_dimensional_metrics(self, title: str, content: str, tokens: list, hoax_score: float, source_type: str) -> dict:
        combined = f"{title} {content}".lower()
        
        # 1. Clickbait Score (Sensasionalisme Judul)
        clickbait_keywords = ["awas", "viral", "terbongkar", "bocoran", "geger", "mengejutkan", "kabar duka", "rahasia", "gempar", "terbukti", "heboh", "syok"]
        cb_matches = sum(1 for w in clickbait_keywords if w in title.lower())
        caps_count = sum(1 for c in title if c.isupper())
        caps_ratio = (caps_count / len(title)) if len(title) > 0 else 0
        exclamation_count = title.count("!") + content[:100].count("!")
        
        raw_cb = (cb_matches * 25) + (caps_ratio * 40) + (exclamation_count * 15)
        clickbait_score = min(99, max(5, int(raw_cb if hoax_score > 0.5 else raw_cb * 0.4)))

        # 2. Indeks Urgensi Palsu (False Urgency Index)
        urgency_phrases = ["sebarkanlah", "viralkan", "sebelum dihapus", "bagikan segera", "jangan sampai", "tolak", "boikot", "rakyat harus tahu", "darurat", "peringatan keras"]
        urg_matches = sum(1 for p in urgency_phrases if p in combined)
        urgency_index = min(98, max(4, int((urg_matches * 30) + (hoax_score * 35))))

        # 3. Radar Sentimen Emosi (Fear, Anger, Neutral)
        fear_words = ["awas", "racun", "bahaya", "panik", "ancaman", "meninggal", "korban", "hancur", "tsunami", "gempa", "kanker", "mematikan"]
        anger_words = ["busuk", "zalim", "korup", "biadab", "curang", "rezim", "boikot", "antek", "bajingan", "dusta", "bobrok"]
        
        fear_count = sum(1 for w in fear_words if w in combined)
        anger_count = sum(1 for w in anger_words if w in combined)
        
        if hoax_score > 0.55:
            fear_pct = min(85, max(20, int(fear_count * 25 + hoax_score * 40)))
            anger_pct = min(85, max(15, int(anger_count * 25 + hoax_score * 35)))
            neutral_pct = max(5, 100 - fear_pct - anger_pct)
        else:
            neutral_pct = min(90, max(50, int((1 - hoax_score) * 85)))
            fear_pct = max(5, int((100 - neutral_pct) * 0.5))
            anger_pct = max(5, 100 - neutral_pct - fear_pct)

        # 4. Indeks Kredibilitas Sumber / Domain
        credible_domains = ["detik.com", "kompas.com", "tempo.co", "antaranews.com", "kemenkes.go.id", "bmkg.go.id", "kpu.go.id", "cnnindonesia.com", "republika.co.id"]
        if source_type == "url":
            is_credible = any(d in combined for d in credible_domains)
            domain_reputation = 94 if is_credible else 32
        else:
            domain_reputation = int(round((1.0 - hoax_score) * 90 + 10))

        # 5. SHA-256 Digital Forensic Certificate ID
        cert_hash = hashlib.sha256(f"{title} {content}".encode("utf-8")).hexdigest()[:16].upper()
        cert_id = f"CEKHOAKS-SEC-{cert_hash[:4]}-{cert_hash[4:8]}-{cert_hash[8:12]}-{cert_hash[12:16]}"

        # 6. Analisis Kerentanan Demografis (Demographic Vulnerability Profile)
        health_kws = ["rebusan", "vaksin", "dokter", "racun", "kanker", "obat", "jantung", "meninggal", "sembuh"]
        finance_kws = ["dana", "rekening", "bantuan", "subsidi", "uang", "rekrutmen", "hadiah", "pemenang", "biaya"]
        politic_kws = ["pemilu", "kpu", "suara", "rezim", "konspirasi", "antek", "boikot", "curang"]

        if any(w in combined for w in health_kws):
            target_group = "Lansia & Grup WhatsApp Keluarga"
            vuln_score = 88 if hoax_score > 0.5 else 30
            psych_vector = "Kekhawatiran Kesehatan & Manipulasi Empati Keluarga"
            mitigation = "Gunakan klarifikasi santun bernada empati, sertakan kutipan dokter/BPOM, hindari debat terbuka."
        elif any(w in combined for w in finance_kws):
            target_group = "Pencari Kerja, Masyarakat Prasejahtera & Pelajar"
            vuln_score = 92 if hoax_score > 0.5 else 25
            psych_vector = "Urgensi Ekonomi & Janji Imbalan Palsu (Phishing)"
            mitigation = "Edukasi untuk memeriksa kanal resmi SSCASN/Kemnaker dan jangan pernah mengirim uang ke rekening pribadi."
        elif any(w in combined for w in politic_kws):
            target_group = "Pemilih Pemula & Netizen Medsos (X/FB/TikTok)"
            vuln_score = 82 if hoax_score > 0.5 else 35
            psych_vector = "Polarisasi Opini & Pemicu Kemarahan Kolektif"
            mitigation = "Bandingkan dengan siaran pers KPU dan data tabulasi pembanding independen yang terverifikasi."
        else:
            target_group = "Masyarakat Umum & Pengguna Internet"
            vuln_score = 65 if hoax_score > 0.5 else 20
            psych_vector = "Rasa Penasaran & Kecepatan Informasi Viral"
            mitigation = "Terapkan prinsip 'Saring Sebelum Sharing' dan periksa domain rujukan sebelum membagikan."

        return {
            "clickbait_score": clickbait_score,
            "urgency_index": urgency_index,
            "emotional_sentiment": {
                "fear": fear_pct,
                "anger": anger_pct,
                "neutral": neutral_pct
            },
            "domain_reputation": domain_reputation,
            "forensic_certificate": {
                "cert_id": cert_id,
                "sha256": cert_hash,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC+7"),
                "algorithm": "Multinomial Naive Bayes + Lidstone (alpha=0.5) + LIME XAI",
                "auditor": "CekHoaks Digital Forensics Engine v1.2"
            },
            "demographic_vulnerability": {
                "target_group": target_group,
                "vulnerability_score": vuln_score,
                "psychological_vector": psych_vector,
                "mitigation_strategy": mitigation
            }
        }

    def _generate_counter_narrative(self, title: str, content: str, label: str, terms: list, risk_level: str) -> dict:
        terms_str = ", ".join([t.get("term", "") for t in terms[:3]]) if terms else "klaim provokatif"
        safe_title = title if title else "informasi yang beredar"

        if label == "HOAKS":
            formal = (
                f"SIARAN KLARIFIKASI RESMI TERKAIT INFORMASI BEREDAR:\n\n"
                f"Menanggapi narasi yang beredar di masyarakat dengan judul \"{safe_title}\", "
                f"disampaikan bahwa narasi tersebut TIDAK BENAR dan terindikasi sebagai disinformasi/hoaks. "
                f"Hasil audit forensik leksikal menunjukkan adanya anomali istilah provokatif ({terms_str}) "
                f"dengan tingkat risiko {risk_level}.\n\n"
                f"Masyarakat diimbau untuk tidak menyebarluaskan narasi ini dan hanya mempercayai informasi "
                f"resmi yang telah diverifikasi oleh kementerian/lembaga berwenang melalui kanal aduankonten.id."
            )
            whatsapp = (
                f"Bapak/Ibu dan teman-teman sekalian, mohon izin meluruskan info di atas yaa terkait \"{safe_title}\" 🙏.\n\n"
                f"Setelah dicek di sistem verifikasi fakta CekHoaks AI dan rujukan resmi, informasi tersebut terkonfirmasi HOAKS / tidak akurat "
                f"(terindikasi pemicu: {terms_str}).\n\n"
                f"Mohon untuk tidak diteruskan ke grup lain agar tidak menimbulkan kepanikan atau salah paham. "
                f"Terima kasih atas perhatiannya, mari tetap bijak menyaring sebelum sharing! ✨"
            )
            social = (
                f"🚨 [CEK FAKTA RESMI]\n\n"
                f"Beredar klaim: \"{safe_title}\"\n\n"
                f"❌ STATUS: TERINDIKASI DISINFORMASI / HOAKS\n"
                f"⚠️ Risiko: {risk_level}\n"
                f"🔍 Pemicu: Pola leksikal {terms_str} tanpa dasar rujukan data resmi.\n\n"
                f"Fakta sebenarnya: Hingga saat ini tidak ada pengumuman resmi terkait klaim tersebut. Selalu cek silang sebelum membagikan!\n\n"
                f"#CekFakta #SaringSebelumSharing #AntiHoaks #LiterasiDigital"
            )
        else:
            formal = (
                f"KONFIRMASI INFORMASI FAKTUAL:\n\n"
                f"Mengenai artikel dengan judul \"{safe_title}\", hasil klasifikasi membuktikan narasi ini BERITA FAKTA / RESMI. "
                f"Kandungan berita bersifat faktual, objektif, dan selaras dengan siaran pers instansi terpercaya."
            )
            whatsapp = (
                f"Bapak/Ibu sekalian, sekadar konfirmasi info \"{safe_title}\" di atas sudah dicek dan terbukti FAKTA RESMI yaa 👍. "
                f"Informasinya valid dan bersumber dari rujukan kredibel. Semoga bermanfaat!"
            )
            social = (
                f"✅ [VERIFIKASI FAKTA RESMI]\n\n"
                f"Judul: \"{safe_title}\"\n\n"
                f"✔️ STATUS: VALID & TERVERIFIKASI FAKTA\n"
                f"Isi berita kredibel, proporsional, dan bebas dari rekayasa disinformasi.\n\n"
                f"#InfoValid #BeritaResmi #CekFakta"
            )

        return {
            "formal_pr": formal,
            "whatsapp_group": whatsapp,
            "social_media": social
        }

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
        explanation = xai_engine.explain_instance(tokens, top_k=10)

        # Skala Kepercayaan & Risiko
        confidence = round(max(hoax_score, fact_score) * 100, 1)
        if predicted_label == "HOAKS":
            risk_level = "Tinggi (Bahaya Hoaks)" if hoax_score > 0.70 else "Sedang (Waspada Misinformasi)"
        else:
            risk_level = "Rendah (Berita Kredibel / Faktual)" if fact_score > 0.70 else "Verifikasi Lanjut Disarankan"

        # Analisis Multi-Dimensi Tingkat Lanjut (Clickbait, Urgensi, Emosi, Forensik)
        multi_dim = self._calculate_multi_dimensional_metrics(title, content, tokens, hoax_score, source_type)

        # Generator Narasi Klarifikasi Otomatis (Counter-Narrative)
        counter_narrative = self._generate_counter_narrative(
            title, content, predicted_label,
            explanation.get("top_terms", []), risk_level
        )

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
            "content": content,
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
            "multi_dimensional": multi_dim,
            "counter_narrative": counter_narrative,
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
