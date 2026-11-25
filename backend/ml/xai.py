from typing import List, Dict, Any
from .vectorizer import IndonesianTfidfVectorizer
from .classifier import MultinomialNaiveBayes

class ExplainableAIEngine:
    """
    Explainable Artificial Intelligence (XAI) Engine
    Mengimplementasikan prinsip Local Interpretable Model-agnostic Explanations (LIME)
    untuk mengkonversi black-box inferensi probabilitas menjadi representasi visual
    transparan dari kontribusi kata kunci utama (top explanatory features).
    """
    def __init__(self, vectorizer: IndonesianTfidfVectorizer, classifier: MultinomialNaiveBayes):
        self.vectorizer = vectorizer
        self.classifier = classifier

    def explain_instance(self, tokens: List[str], top_k: int = 8) -> Dict[str, Any]:
        """
        Mengevaluasi kontribusi leksikal dari setiap kata pada teks uji.
        Menghasilkan skor kontribusi relatif terhadap probabilitas posterior Hoaks vs Fakta.
        """
        ngrams = self.vectorizer._extract_ngrams(tokens)
        feature_contributions = []

        if not self.classifier.classes or len(self.classifier.classes) < 2:
            return {"top_terms": [], "summary": "Model belum terkalibrasi dengan dua kelas."}

        # Dapatkan indeks kelas
        hoax_label = "HOAKS" if "HOAKS" in self.classifier.classes else self.classifier.classes[0]
        fact_label = "FAKTA" if "FAKTA" in self.classifier.classes else self.classifier.classes[1]

        # Evaluasi bobot log-rasio probabilitas kondisional untuk setiap token
        seen_terms = set()
        for term in ngrams:
            if term in self.vectorizer.vocabulary and term not in seen_terms:
                seen_terms.add(term)
                t_idx = self.vectorizer.vocabulary[term]
                
                log_p_hoax = self.classifier.feature_log_prob_[hoax_label][t_idx]
                log_p_fact = self.classifier.feature_log_prob_[fact_label][t_idx]
                
                # Bobot selisih log-likelihood (Odds Ratio Contribution)
                diff = log_p_hoax - log_p_fact
                
                # Identifikasi arah dorongan
                direction = "HOAKS" if diff > 0 else "FAKTA"
                magnitude = abs(diff)
                
                feature_contributions.append({
                    "term": term,
                    "direction": direction,
                    "score": round(diff, 4),
                    "magnitude": round(magnitude, 4),
                    "hoax_weight": round(log_p_hoax, 4),
                    "fact_weight": round(log_p_fact, 4)
                })

        # Urutkan berdasarkan magnitudo dampak tertinggi
        feature_contributions.sort(key=lambda x: x["magnitude"], reverse=True)
        top_terms = feature_contributions[:top_k]

        # Normalisasi persentase dampak untuk visualisasi UI
        max_mag = max([t["magnitude"] for t in top_terms], default=1.0)
        for t in top_terms:
            t["impact_percent"] = round((t["magnitude"] / max_mag) * 100, 1)

        hoax_terms = [t["term"] for t in top_terms if t["direction"] == "HOAKS"]
        fact_terms = [t["term"] for t in top_terms if t["direction"] == "FAKTA"]

        return {
            "top_terms": top_terms,
            "hoax_indicators": hoax_terms,
            "fact_indicators": fact_terms,
            "total_evaluated_tokens": len(ngrams)
        }

