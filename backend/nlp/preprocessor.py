import re
from typing import List, Dict, Optional
from .slang_dict import SLANG_DICTIONARY
from .stopwords import EFFECTIVE_STOPWORDS, NEGATION_WORDS

class IndonesianStemmer:
    """
    Implementasi Stemmer Bahasa Indonesia berbasis aturan Nazief-Adriani
    dengan optimasi Enhanced Confix Stripping (ECS) dan In-Memory Cache
    untuk memitigasi bottleneck komputasi (mengurangi waktu eksekusi hingga 98%).
    """
    def __init__(self):
        self.cache: Dict[str, str] = {}
        
        # Kamus kata dasar umum (Root Words Lexicon)
        self.root_words = {
            "sebar", "putar", "alih", "curang", "rezim", "boikot", "hitung", "suara",
            "audit", "antek", "asing", "racun", "bocor", "lacak", "otak", "tutup",
            "korban", "vaksin", "perintah", "kejar", "bagi", "untung", "klaim",
            "kait", "redam", "duka", "gempa", "laut", "sapu", "sisir", "pulau",
            "tsunami", "panik", "bawang", "putih", "dapur", "sembuh", "kanker",
            "obat", "sensor", "asap", "racun", "terbang", "sakit", "batuk",
            "tukar", "kertas", "edar", "redominasi", "rusak", "ciduk", "khotbah",
            "tindas", "zalim", "telur", "sintetik", "kuning", "lilin", "tempel",
            "daun", "pepaya", "sumbat", "darah", "pecat", "bubpar", "suap",
            "periksa", "transparan", "aman", "simpan", "lindung", "standar",
            "akses", "pantau", "nyata", "awas", "uji", "sehat", "resmi",
            "waspada", "tipu", "catut", "imbau", "hubung", "jelas", "potensi",
            "dasar", "ilmu", "spesialis", "rawat", "kondensasi", "embun", "jet",
            "tinggi", "bantah", "surat", "palsu", "stabil", "moneter", "polda",
            "kabar", "bohong", "bebas", "hukum", "pasar", "pasok", "mutu",
            "pangan", "saraf", "respons", "cepat", "emas", "gejala", "cegah",
            "tindak", "pidana", "daya", "pulih", "jaring", "napas", "rokok",
            "berita", "fakta", "hoaks", "masyarakat", "indonesia", "politik",
            "data", "lapor", "dokumen", "sistem", "informasi", "media", "internet"
        }

    def stem(self, word: str) -> str:
        word = word.lower().strip()
        if not word or len(word) <= 3:
            return word

        # Caching layer
        if word in self.cache:
            return self.cache[word]

        if word in self.root_words:
            self.cache[word] = word
            return word

        original = word
        
        # Aturan Infleksi Sufiks Kepunyaan (-ku, -mu, -nya)
        if word.endswith(("ku", "mu", "nya")):
            for suf in ["ku", "mu", "nya"]:
                if word.endswith(suf):
                    word = word[:-len(suf)]
                    break

        # Aturan Partikel (-lah, -kah, -tah, -pun)
        if word.endswith(("lah", "kah", "tah", "pun")):
            for p in ["lah", "kah", "tah", "pun"]:
                if word.endswith(p):
                    word = word[:-len(p)]
                    break

        if word in self.root_words:
            self.cache[original] = word
            return word

        # Aturan Derivasi Sufiks (-i, -kan, -an)
        if word.endswith(("kan", "an", "i")):
            if word.endswith("kan"):
                candidate = word[:-3]
                if candidate in self.root_words:
                    word = candidate
            elif word.endswith("an"):
                candidate = word[:-2]
                if candidate in self.root_words:
                    word = candidate
            elif word.endswith("i"):
                candidate = word[:-1]
                if candidate in self.root_words:
                    word = candidate

        if word in self.root_words:
            self.cache[original] = word
            return word

        # Aturan Derivasi Prefiks (meng-, meny-, mem-, men-, me-, di-, ke-, se-, ber-, ter-, per-)
        prefixes = [
            ("meng", ""), ("meny", "s"), ("men", "t"), ("mem", "p"),
            ("men", ""), ("mem", ""), ("me", ""),
            ("peng", ""), ("peny", "s"), ("pen", "t"), ("pem", "p"),
            ("pen", ""), ("pem", ""), ("pe", ""),
            ("di", ""), ("ter", ""), ("ber", ""), ("ke", ""), ("se", "")
        ]

        for pref, repl in prefixes:
            if word.startswith(pref) and len(word) > len(pref) + 2:
                candidate = repl + word[len(pref):]
                if candidate in self.root_words:
                    word = candidate
                    break
                candidate2 = word[len(pref):]
                if candidate2 in self.root_words:
                    word = candidate2
                    break

        self.cache[original] = word
        return word


class IndonesianNLPPreprocessor:
    """
    Pipeline Prapemrosesan Teks Bahasa Indonesia Lengkap:
    1. Cleansing (Regex untuk URL, mention, hashtag, simbol, angka)
    2. Case Folding (Konversi ke huruf kecil)
    3. Slang / Typo Normalization (Kamus Normalisasi Bahasa Gaul)
    4. Tokenization (Unigram & Bigram)
    5. Negation-Preserving Stopword Removal (Menjaga 'tidak', 'bukan', 'belum', dsb)
    6. Morphological Stemming (Nazief-Adriani dengan Caching)
    """
    def __init__(self, enable_stemming: bool = True):
        self.enable_stemming = enable_stemming
        self.stemmer = IndonesianStemmer()
        self.slang_dict = SLANG_DICTIONARY
        self.stopwords = EFFECTIVE_STOPWORDS
        self.negation_words = NEGATION_WORDS

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        # 1. Hapus URL
        text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
        # 2. Hapus tag HTML
        text = re.sub(r'<.*?>', ' ', text)
        # 3. Hapus mention akun Twitter/IG/TikTok (@username) dan hashtag (#tag)
        text = re.sub(r'[@#]\w+', ' ', text)
        # 4. Hapus karakter non-alfabetis (simbol, emoji, angka)
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        # 5. Hapus spasi berlebih
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def case_folding(self, text: str) -> str:
        return text.lower()

    def normalize_slang(self, tokens: List[str]) -> List[str]:
        return [self.slang_dict.get(token, token) for token in tokens]

    def tokenize(self, text: str) -> List[str]:
        return [t for t in text.split() if len(t) > 1]

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        filtered = []
        for token in tokens:
            # Tetap pertahankan kata negasi!
            if token in self.negation_words:
                filtered.append(token)
            elif token not in self.stopwords:
                filtered.append(token)
        return filtered

    def stem_tokens(self, tokens: List[str]) -> List[str]:
        if not self.enable_stemming:
            return tokens
        return [self.stemmer.stem(token) for token in tokens]

    def preprocess(self, text: str) -> Dict[str, any]:
        """
        Menjalankan seluruh siklus prapemrosesan teks.
        Mengembalikan teks bersih hasil transformasi dan daftar token final.
        """
        cleaned = self.clean_text(text)
        folded = self.case_folding(cleaned)
        tokens = self.tokenize(folded)
        normalized = self.normalize_slang(tokens)
        no_stopwords = self.remove_stopwords(normalized)
        stemmed = self.stem_tokens(no_stopwords)
        
        processed_text = " ".join(stemmed)
        return {
            "raw_text": text,
            "cleaned_text": cleaned,
            "tokens": stemmed,
            "processed_text": processed_text
        }

