import math
from typing import List, Dict, Any

class MultinomialNaiveBayes:
    """
    Multinomial Naive Bayes (MNB) Classifier
    Implementasi Berdasarkan Dokumen Riset:
    - Additive Laplace Smoothing (alpha=1.0) atau Lidstone Smoothing (alpha=0.1 / 0.5)
    - Komputasi Domain Logaritmik (Log-Space Arithmetic) untuk mencegah kegagalan Arithmetic Underflow
    - Estimasi Probabilitas Posterior Kelas via Softmax Normalized Log-Likelihood
    """
    def __init__(self, alpha: float = 1.0):
        self.alpha = float(alpha)
        self.classes: List[str] = []
        self.class_log_prior_: Dict[str, float] = {}
        self.feature_log_prob_: Dict[str, List[float]] = {}
        self.n_features_: int = 0

    def fit(self, X: List[List[float]], y: List[str]):
        """
        Melatih model MNB pada matriks fitur TF-IDF dan label kelas ('HOAKS' / 'FAKTA').
        """
        n_samples = len(y)
        if n_samples == 0:
            raise ValueError("Data pelatihan tidak boleh kosong.")
        
        self.n_features_ = len(X[0])
        self.classes = sorted(list(set(y)))
        n_classes = len(self.classes)

        # Hitung class prior log P(c)
        class_counts = {c: 0 for c in self.classes}
        for label in y:
            class_counts[label] += 1

        for c in self.classes:
            self.class_log_prior_[c] = math.log(class_counts[c] / n_samples)

        # Akumulasi bobot fitur per kelas
        feature_counts = {c: [0.0] * self.n_features_ for c in self.classes}
        total_counts = {c: 0.0 for c in self.classes}

        for i, sample in enumerate(X):
            c = y[i]
            for j in range(self.n_features_):
                val = sample[j]
                if val > 0.0:
                    feature_counts[c][j] += val
                    total_counts[c] += val

        # Hitung log conditional probability log P(t|c) dengan Laplace/Lidstone smoothing
        # P(t|c) = (count(t, c) + alpha) / (sum(count(t', c)) + alpha * |V|)
        for c in self.classes:
            smoothed_denominator = total_counts[c] + (self.alpha * self.n_features_)
            log_probs = []
            for j in range(self.n_features_):
                smoothed_numerator = feature_counts[c][j] + self.alpha
                prob = smoothed_numerator / smoothed_denominator
                log_probs.append(math.log(prob))
            self.feature_log_prob_[c] = log_probs

        return self

    def predict_log_proba(self, X: List[List[float]]) -> List[Dict[str, float]]:
        """Menghitung nilai log posterior unnormalized untuk setiap sampel."""
        results = []
        for sample in X:
            sample_log_prob = {}
            for c in self.classes:
                # log P(c|d) = log P(c) + sum(f_j * log P(t_j|c))
                log_p = self.class_log_prior_[c]
                for j in range(self.n_features_):
                    val = sample[j]
                    if val > 0.0:
                        log_p += val * self.feature_log_prob_[c][j]
                sample_log_prob[c] = log_p
            results.append(sample_log_prob)
        return results

    def predict_proba(self, X: List[List[float]]) -> List[Dict[str, float]]:
        """
        Menghitung probabilitas posterior terkalibrasi [0.0 - 1.0]
        menggunakan normalisasi softmax pada domain logaritmik:
        P(c|d) = exp(log_p - max_log) / sum(exp(log_k - max_log))
        """
        log_probas = self.predict_log_proba(X)
        proba_results = []

        for log_prob in log_probas:
            max_log = max(log_prob.values())
            exp_sums = {c: math.exp(log_p - max_log) for c, log_p in log_prob.items()}
            total_exp = sum(exp_sums.values())

            calibrated = {c: exp_val / total_exp for c, exp_val in exp_sums.items()}
            proba_results.append(calibrated)

        return proba_results

    def predict(self, X: List[List[float]]) -> List[str]:
        """Memprediksi label kelas dengan probabilitas posterior tertinggi."""
        probas = self.predict_proba(X)
        return [max(p.items(), key=lambda item: item[1])[0] for p in probas]

    def to_dict(self) -> dict:
        return {
            "alpha": self.alpha,
            "classes": self.classes,
            "class_log_prior": self.class_log_prior_,
            "feature_log_prob": self.feature_log_prob_,
            "n_features": self.n_features_
        }

    @classmethod
    def from_dict(cls, data: dict):
        obj = cls(alpha=data["alpha"])
        obj.classes = data["classes"]
        obj.class_log_prior_ = data["class_log_prior"]
        obj.feature_log_prob_ = data["feature_log_prob"]
        obj.n_features_ = data["n_features"]
        return obj

