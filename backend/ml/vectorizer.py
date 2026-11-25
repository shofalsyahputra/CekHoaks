import math
from typing import List, Dict, Tuple, Set

class IndonesianTfidfVectorizer:
    """
    Term Frequency - Inverse Document Frequency (TF-IDF) Vectorizer
    Mendukung:
    - N-gram deret tunggal (1,1) maupun relasional unigram+bigram (1,2)
    - Normalisasi spasial Euclidean (L2 Norm) sesuai rumus cetak biru:
      v_norm = v / sqrt(sum(v_i^2))
    - Pemulusan (smoothing) IDF standar industri:
      IDF(t) = ln((1 + N) / (1 + DF(t))) + 1
    """
    def __init__(self, ngram_range: Tuple[int, int] = (1, 2), norm: str = "l2", min_df: int = 1):
        self.ngram_range = ngram_range
        self.norm = norm
        self.min_df = min_df
        self.vocabulary: Dict[str, int] = {}
        self.feature_names: List[str] = []
        self.idf_diag: List[float] = []
        self.n_features = 0

    def _extract_ngrams(self, tokens: List[str]) -> List[str]:
        ngrams = []
        min_n, max_n = self.ngram_range
        n_tokens = len(tokens)
        
        for n in range(min_n, max_n + 1):
            for i in range(n_tokens - n + 1):
                ngram = " ".join(tokens[i:i + n])
                ngrams.append(ngram)
        return ngrams

    def fit(self, corpus_tokens: List[List[str]]):
        """Membangun kosakata (vocabulary) dan menghitung nilai bobot IDF dari korpus pelatihan."""
        doc_count = len(corpus_tokens)
        df_counts: Dict[str, int] = {}

        for tokens in corpus_tokens:
            doc_ngrams = set(self._extract_ngrams(tokens))
            for term in doc_ngrams:
                df_counts[term] = df_counts.get(term, 0) + 1

        # Saring berdasarkan min_df
        vocab = {}
        idx = 0
        for term, count in sorted(df_counts.items()):
            if count >= self.min_df:
                vocab[term] = idx
                idx += 1

        self.vocabulary = vocab
        self.n_features = len(vocab)
        self.feature_names = [term for term, _ in sorted(vocab.items(), key=lambda x: x[1])]

        # Hitung IDF dengan formula smoothed
        self.idf_diag = [0.0] * self.n_features
        for term, term_idx in self.vocabulary.items():
            df = df_counts.get(term, 0)
            self.idf_diag[term_idx] = math.log((1.0 + doc_count) / (1.0 + df)) + 1.0

        return self

    def transform(self, corpus_tokens: List[List[str]]) -> List[List[float]]:
        """Mentransformasikan korpus token menjadi matriks vektor berbobot TF-IDF dengan normalisasi L2."""
        matrix = []
        for tokens in corpus_tokens:
            vec = [0.0] * self.n_features
            ngrams = self._extract_ngrams(tokens)
            
            # Hitung Term Frequency (TF)
            tf_counts: Dict[int, int] = {}
            for term in ngrams:
                if term in self.vocabulary:
                    t_idx = self.vocabulary[term]
                    tf_counts[t_idx] = tf_counts.get(t_idx, 0) + 1

            total_terms = len(ngrams) if len(ngrams) > 0 else 1
            for t_idx, count in tf_counts.items():
                tf = count / total_terms
                idf = self.idf_diag[t_idx]
                vec[t_idx] = tf * idf

            # Normalisasi Jarak Euclidean (L2 Normalization)
            if self.norm == "l2":
                norm_val = math.sqrt(sum(v * v for v in vec))
                if norm_val > 0.0:
                    vec = [v / norm_val for v in vec]

            matrix.append(vec)
        return matrix

    def fit_transform(self, corpus_tokens: List[List[str]]) -> List[List[float]]:
        return self.fit(corpus_tokens).transform(corpus_tokens)

    def to_dict(self) -> dict:
        return {
            "ngram_range": list(self.ngram_range),
            "norm": self.norm,
            "min_df": self.min_df,
            "vocabulary": self.vocabulary,
            "feature_names": self.feature_names,
            "idf_diag": self.idf_diag,
            "n_features": self.n_features
        }

    @classmethod
    def from_dict(cls, data: dict):
        obj = cls(
            ngram_range=tuple(data["ngram_range"]),
            norm=data["norm"],
            min_df=data["min_df"]
        )
        obj.vocabulary = data["vocabulary"]
        obj.feature_names = data["feature_names"]
        obj.idf_diag = data["idf_diag"]
        obj.n_features = data["n_features"]
        return obj

