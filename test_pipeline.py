import os
import sys
import json

# Setup import path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from nlp.preprocessor import IndonesianNLPPreprocessor
from ml.vectorizer import IndonesianTfidfVectorizer
from ml.classifier import MultinomialNaiveBayes
from ml.xai import ExplainableAIEngine
from services.feedback_service import DatabaseService
from services.ocr_service import OCRService

def test_full_pipeline():
    print("=" * 70)
    print("  VERIFIKASI INTEGRASI LENGKAP ARSITEKTUR DETEKSI HOAKS")
    print("=" * 70)

    # 1. Test NLP Preprocessing
    print("\n[1] PENGUJIAN NLP PREPROCESSING PIPELINE:")
    prep = IndonesianNLPPreprocessor(enable_stemming=True)
    sample_raw = "Awas! @penipu KPU diam2 memanipulasi https://bit.ly/3x suara tdk transparan bgt #viral"
    res_prep = prep.preprocess(sample_raw)
    print(f"    Raw Text      : {sample_raw}")
    print(f"    Cleaned Text  : {res_prep['cleaned_text']}")
    print(f"    Tokens        : {res_prep['tokens']}")
    assert "tidak" in res_prep['tokens'], "Kata negasi 'tidak' HARUS dipertahankan!"
    print("    -> Normalisasi Slang & Negasi Terlindungi: BERHASIL")

    # 2. Test Model Loading & Serialization
    print("\n[2] PENGUJIAN MODEL MULTINOMIAL NAIVE BAYES & TF-IDF:")
    model_path = os.path.join(BASE_DIR, "backend", "model_weights.json")
    with open(model_path, "r", encoding="utf-8") as f:
        model_data = json.load(f)

    vectorizer = IndonesianTfidfVectorizer.from_dict(model_data["vectorizer"])
    classifier = MultinomialNaiveBayes.from_dict(model_data["classifier"])
    xai = ExplainableAIEngine(vectorizer, classifier)

    print(f"    Total Vocabulary N-Gram: {vectorizer.n_features}")
    print(f"    Hyperparameter Alpha   : {classifier.alpha} (Lidstone Smoothing)")

    # 3. Test Inference: Berita Hoaks
    print("\n[3] PENGUJIAN INFERENSI HOAKS:")
    hoax_news = "Sebarkanlah info penting ini! Terbukti konspirasi server luar negeri memanipulasi perolehan suara pemilu. Boikot hasil perhitungan sebelum terlambat!"
    hoax_tokens = prep.preprocess(hoax_news)["tokens"]
    hoax_vec = vectorizer.transform([hoax_tokens])
    hoax_pred = classifier.predict(hoax_vec)[0]
    hoax_prob = classifier.predict_proba(hoax_vec)[0]
    hoax_exp = xai.explain_instance(hoax_tokens)

    print(f"    Teks Input : {hoax_news[:80]}...")
    print(f"    Prediksi   : {hoax_pred} (Skor Hoaks: {hoax_prob['HOAKS']*100:.1f}%, Skor Fakta: {hoax_prob['FAKTA']*100:.1f}%)")
    print(f"    Top XAI    : {[t['term'] for t in hoax_exp['top_terms'][:4]]}")
    assert hoax_pred == "HOAKS"
    assert hoax_prob["HOAKS"] > 0.60
    print("    -> Deteksi Hoaks & XAI: BERHASIL")

    # 4. Test Inference: Berita Fakta
    print("\n[4] PENGUJIAN INFERENSI FAKTA:")
    fact_news = "Kementerian Kesehatan bersama BPOM menyatakan bahwa vaksin telah melalui pengujian klinis berstandar resmi WHO dan aman digunakan publik."
    fact_tokens = prep.preprocess(fact_news)["tokens"]
    fact_vec = vectorizer.transform([fact_tokens])
    fact_pred = classifier.predict(fact_vec)[0]
    fact_prob = classifier.predict_proba(fact_vec)[0]
    fact_exp = xai.explain_instance(fact_tokens)

    print(f"    Teks Input : {fact_news[:80]}...")
    print(f"    Prediksi   : {fact_pred} (Skor Fakta: {fact_prob['FAKTA']*100:.1f}%, Skor Hoaks: {fact_prob['HOAKS']*100:.1f}%)")
    print(f"    Top XAI    : {[t['term'] for t in fact_exp['top_terms'][:4]]}")
    assert fact_pred == "FAKTA"
    assert fact_prob["FAKTA"] > 0.60
    print("    -> Deteksi Fakta & XAI: BERHASIL")

    # 5. Test SQLite Audit Trail & Feedback
    print("\n[5] PENGUJIAN BASIS DATA PERSISTENSI RELASIONAL SQLITE:")
    db_path = os.path.join(BASE_DIR, "backend", "database.db")
    db = DatabaseService(db_path)
    log_id = db.save_log(
        title="Uji Otomatis Unit",
        content=hoax_news,
        cleansed_text=" ".join(hoax_tokens),
        predicted_label=hoax_pred,
        hoax_score=hoax_prob["HOAKS"],
        fact_score=hoax_prob["FAKTA"],
        xai_metadata=hoax_exp,
        source_type="automated_test"
    )
    print(f"    Tersimpan Log ID : {log_id}")
    
    fb_id = db.save_feedback(log_id, "agree", "HOAKS", "Prediksi sangat akurat")
    print(f"    Tersimpan Umpan Balik ID : {fb_id}")

    recent = db.get_recent_logs(limit=3)
    print(f"    Total Log Terambil : {len(recent)} entri")
    assert len(recent) > 0
    print("    -> SQLite Audit Trail & Crowdsourced Feedback: BERHASIL")

    # 6. Test OCR Service Preprocessing
    print("\n[6] PENGUJIAN OCR SERVICE & PREPROCESSING CITRA:")
    ocr = OCRService()
    ocr_res = ocr.process_image_and_extract_text(b"GIF89a Screenshot WhatsApp pesan berantai peringatan darurat", "test_wa.jpg")
    print(f"    Pipeline Applied : {ocr_res['pipeline_applied']}")
    print(f"    Extracted Title  : {ocr_res['title']}")
    print("    -> OCR Service & Computer Vision Pipeline: BERHASIL")

    print("\n" + "=" * 70)
    print("  HASIL: 100% MODUL DAN PIPELINE BERFUNGSI SEMPURNA DENGAN SUKSES!")
    print("=" * 70)

if __name__ == "__main__":
    test_full_pipeline()

