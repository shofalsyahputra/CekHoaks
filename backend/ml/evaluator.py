import math
import random
from typing import List, Dict, Tuple, Any
from .vectorizer import IndonesianTfidfVectorizer
from .classifier import MultinomialNaiveBayes

class ModelEvaluator:
    """
    Kerangka Evaluasi Matematis Berdasarkan Dokumen Riset:
    - K-Fold Cross Validation (k=10)
    - Confusion Matrix (TP, FP, TN, FN)
    - Metrik Makro: Accuracy, Precision, Recall, F1-Score
    - Pengujian 4 Skenario Eksperimental
    """
    def __init__(self, k_folds: int = 10, random_seed: int = 42):
        self.k_folds = k_folds
        self.random_seed = random_seed

    def cross_validate(self, corpus_tokens: List[List[str]], labels: List[str], 
                       vectorizer_params: Dict[str, Any], classifier_params: Dict[str, Any]) -> Dict[str, Any]:
        random.seed(self.random_seed)
        n_samples = len(labels)
        
        # Buat partisi K-Fold
        indices = list(range(n_samples))
        random.shuffle(indices)
        fold_size = max(1, n_samples // self.k_folds)
        
        all_y_true = []
        all_y_pred = []

        for fold in range(self.k_folds):
            start = fold * fold_size
            end = start + fold_size if fold < self.k_folds - 1 else n_samples
            val_idx = set(indices[start:end])
            train_idx = [i for i in indices if i not in val_idx]

            X_train_tokens = [corpus_tokens[i] for i in train_idx]
            y_train = [labels[i] for i in train_idx]
            X_val_tokens = [corpus_tokens[i] for i in val_idx]
            y_val = [labels[i] for i in val_idx]

            if not y_val:
                continue

            # Inisialisasi vectorizer & classifier
            vec = IndonesianTfidfVectorizer(
                ngram_range=vectorizer_params.get("ngram_range", (1, 2)),
                norm=vectorizer_params.get("norm", "l2")
            )
            clf = MultinomialNaiveBayes(alpha=classifier_params.get("alpha", 1.0))

            X_train = vec.fit_transform(X_train_tokens)
            clf.fit(X_train, y_train)

            X_val = vec.transform(X_val_tokens)
            preds = clf.predict(X_val)

            all_y_true.extend(y_val)
            all_y_pred.extend(preds)

        # Hitung Metrik Evaluasi Komprehensif
        return self.compute_metrics(all_y_true, all_y_pred)

    def compute_metrics(self, y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
        classes = sorted(list(set(y_true)))
        positive_label = "HOAKS" if "HOAKS" in classes else classes[0]
        negative_label = "FAKTA" if "FAKTA" in classes else classes[1]

        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == positive_label and yp == positive_label)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == negative_label and yp == positive_label)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == positive_label and yp == negative_label)
        tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == negative_label and yp == negative_label)

        total = len(y_true)
        accuracy = (tp + tn) / total if total > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1_score, 4),
            "confusion_matrix": {
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "positive_label": positive_label,
                "negative_label": negative_label
            },
            "total_samples": total
        }

    def run_all_scenarios(self, corpus_tokens: List[List[str]], labels: List[str]) -> Dict[str, Any]:
        """
        Mengeksekusi 4 skenario eksperimen sesuai tabel spesifikasi pada dokumen:
        1. BoW + Laplace + Unigram
        2. TF-IDF + Laplace + Unigram
        3. TF-IDF + Laplace + Bigram
        4. TF-IDF L2 + Lidstone (alpha=0.5) + Bigram
        """
        scenarios = {
            "Eksperimen 1 (BoW, Laplace alpha=1.0, Unigram)": self.cross_validate(
                corpus_tokens, labels,
                vectorizer_params={"ngram_range": (1, 1), "norm": None},
                classifier_params={"alpha": 1.0}
            ),
            "Eksperimen 2 (TF-IDF, Laplace alpha=1.0, Unigram)": self.cross_validate(
                corpus_tokens, labels,
                vectorizer_params={"ngram_range": (1, 1), "norm": "l2"},
                classifier_params={"alpha": 1.0}
            ),
            "Eksperimen 3 (TF-IDF, Laplace alpha=1.0, Bigram)": self.cross_validate(
                corpus_tokens, labels,
                vectorizer_params={"ngram_range": (1, 2), "norm": "l2"},
                classifier_params={"alpha": 1.0}
            ),
            "Eksperimen 4 (TF-IDF Spasial L2, Lidstone alpha=0.5, Bigram)": self.cross_validate(
                corpus_tokens, labels,
                vectorizer_params={"ngram_range": (1, 2), "norm": "l2"},
                classifier_params={"alpha": 0.5}
            )
        }
        return scenarios

