import os
import json
import time
from nlp.preprocessor import IndonesianNLPPreprocessor
from ml.vectorizer import IndonesianTfidfVectorizer
from ml.classifier import MultinomialNaiveBayes
from ml.evaluator import ModelEvaluator
from services.feedback_service import DatabaseService

def train():
    print("=" * 70)
    print("  PELATIHAN MODEL MULTINOMIAL NAIVE BAYES KLASIFIKASI HOAKS & FAKTA")
    print("=" * 70)

    # 1. Load Dataset (Gabungkan korpus utama + tambahan jika ada)
    dataset_dir = os.path.join(os.path.dirname(__file__), "..", "dataset")
    main_path = os.path.join(dataset_dir, "hoax_corpus_indonesia.json")
    extra_path = os.path.join(dataset_dir, "corpus_tambahan.json")

    with open(main_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    if os.path.exists(extra_path):
        with open(extra_path, "r", encoding="utf-8") as f:
            extra_data = json.load(f)
        existing_ids = {item["id"] for item in raw_data}
        for item in extra_data:
            if item["id"] not in existing_ids:
                raw_data.append(item)
        print(f"[*] Berhasil menggabungkan korpus tambahan ({len(extra_data)} dokumen).")

    hoax_count = sum(1 for d in raw_data if d["label"] == "HOAKS")
    fact_count = sum(1 for d in raw_data if d["label"] == "FAKTA")
    print(f"[*] Total korpus: {len(raw_data)} dokumen (HOAKS: {hoax_count}, FAKTA: {fact_count}).")

    # 2. Preprocessing
    print("[*] Menjalankan Pipeline NLP: Cleansing, Normalisasi Slang, Stopwords Negasi, & Stemming...")
    start_prep = time.time()
    preprocessor = IndonesianNLPPreprocessor(enable_stemming=True)

    corpus_tokens = []
    labels = []
    preprocessed_samples = []

    for item in raw_data:
        full_text = f"{item['title']} {item['content']}"
        res = preprocessor.preprocess(full_text)
        corpus_tokens.append(res["tokens"])
        labels.append(item["label"])
        preprocessed_samples.append({
            "id": item["id"],
            "title": item["title"],
            "label": item["label"],
            "tokens": res["tokens"]
        })

    prep_time = time.time() - start_prep
    print(f"[+] Prapemrosesan selesai dalam {prep_time:.2f} detik (Optimasi Caching aktif).")

    # 3. Eksekusi 4 Skenario Eksperimen (10-Fold Cross Validation)
    print("\n[*] Menjalankan Pengujian 4 Skenario Eksperimental (10-Fold Cross Validation):")
    evaluator = ModelEvaluator(k_folds=10, random_seed=42)
    scenario_results = evaluator.run_all_scenarios(corpus_tokens, labels)

    print("-" * 70)
    print(f"{'Skenario':<45} | {'Akurasi':<8} | {'Presisi':<8} | {'Recall':<8} | {'F1-Score':<8}")
    print("-" * 70)
    for name, metrics in scenario_results.items():
        print(f"{name:<45} | {metrics['accuracy']*100:>6.1f}% | {metrics['precision']*100:>6.1f}% | {metrics['recall']*100:>6.1f}% | {metrics['f1_score']*100:>6.1f}%")
    print("-" * 70)

    # 4. Melatih Model Produksi Terbaik (Skenario 4: TF-IDF Spasial L2, Lidstone alpha=0.5, Unigram+Bigram)
    best_params = {
        "ngram_range": (1, 2),
        "norm": "l2",
        "alpha": 0.5
    }
    print(f"\n[*] Membangun Model Produksi Optimal: TF-IDF (1,2) L2-Norm + Lidstone Smoothing (alpha={best_params['alpha']})...")
    
    vectorizer = IndonesianTfidfVectorizer(ngram_range=best_params["ngram_range"], norm=best_params["norm"])
    X_train = vectorizer.fit_transform(corpus_tokens)

    classifier = MultinomialNaiveBayes(alpha=best_params["alpha"])
    classifier.fit(X_train, labels)

    print(f"[+] Model berhasil dilatih! Jumlah fitur kosakata (N-Gram): {vectorizer.n_features}")

    # 5. Serialisasi Model
    model_export_path = os.path.join(os.path.dirname(__file__), "model_weights.json")
    model_bundle = {
        "version": "1.0.0",
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "best_params": best_params,
        "metrics_scenario_4": scenario_results["Eksperimen 4 (TF-IDF Spasial L2, Lidstone alpha=0.5, Bigram)"],
        "all_scenarios": scenario_results,
        "vectorizer": vectorizer.to_dict(),
        "classifier": classifier.to_dict()
    }

    with open(model_export_path, "w", encoding="utf-8") as f:
        json.dump(model_bundle, f, indent=2, ensure_ascii=False)

    print(f"[+] Bobot model tersimpan di: {model_export_path}")

    # 6. Catat riwayat MLOps ke SQLite
    db_path = os.path.join(os.path.dirname(__file__), "database.db")
    db = DatabaseService(db_path)
    db.save_model_version(
        version_tag="v1.0.0-lidstone-tfidf-bigram",
        metrics=scenario_results["Eksperimen 4 (TF-IDF Spasial L2, Lidstone alpha=0.5, Bigram)"],
        hyperparameters=best_params
    )
    print(f"[+] Metrik model dan parameter MLOps berhasil dicatat ke basis data SQLite.")
    print("=" * 70)

if __name__ == "__main__":
    train()

