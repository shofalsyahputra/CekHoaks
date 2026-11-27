import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import re
import time
from datetime import datetime

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache"))
CACHE_FILE = os.path.join(CACHE_DIR, "trending_cache.json")
CACHE_TTL_SECONDS = 1800  # 30 menit

# Fallback terkurasi jika koneksi internet terputus
CURATED_FALLBACK = [
    {
        "title": "Beredar Video Menara BTS 5G Memancarkan Radiasi Pengendali Pikiran",
        "category": "Teknologi & Kesehatan",
        "verdict": "HOAKS",
        "source": "MAFINDO & Kominfo RI",
        "date": "27 Nov 2026",
        "summary": "Video viral menuding gelombang frekuensi mikro BTS 5G memicu gangguan memori. Kemenkominfo memastikan standar pancaran BTS di Indonesia jauh di bawah batas radiasi ICNIRP/WHO.",
        "sample_text": "Awas bahaya radiasi gelombang 5G dari menara tower ilegal! Telah terbukti memicu kerusakan sel otak dan kontrol pikiran warga. Matikan sinyal seluler Anda segera demi keselamatan!"
    },
    {
        "title": "Surat Edaran Palsu Rekrutmen CPNS Kemenkeu Berbayar Melalui Rekening Pribadi",
        "category": "Pemerintahan & Karir",
        "verdict": "HOAKS",
        "source": "BKN & Kemenkeu RI",
        "date": "26 Nov 2026",
        "summary": "Surat berkop Garuda palsu meminta biaya registrasi seleksi CPNS sebesar Rp 2,5 juta. BKN menegaskan seluruh proses pendaftaran CASN resmi hanya lewat portal sscasn.bkn.go.id tanpa pungutan.",
        "sample_text": "Pengumuman kelulusan afirmasi khusus CPNS Kementerian Keuangan RI 2026. Peserta diwajibkan menyelesaikan biaya administrasi pemberkasan SK ke rekening panitia agar NIP segera diterbitkan!"
    },
    {
        "title": "Klaim Air Rebusan Daun Sirih Dapat Menyembuhkan Penyakit Jantung Koroner",
        "category": "Teknologi & Kesehatan",
        "verdict": "HOAKS",
        "source": "PB PERKI & Kemenkes",
        "date": "25 Nov 2026",
        "summary": "Pesan berantai WhatsApp mengklaim plak pembuluh darah arteri lenyap seketika dengan minum air rebusan sirih. Dokter spesialis jantung menegaskan klaim tersebut mitos berbahaya.",
        "sample_text": "Kabar gembira bagi penderita jantung! Jangan mau pasang ring yang mahal. Cukup rebus daun sirih merah 7 lembar setiap pagi, plak pembuluh darah rontok dan jantung sehat seketika!"
    },
    {
        "title": "Pemerintah Mulai Salurkan Bantuan Subsidi Upah (BSU) Lewat Kanal Resmi BPJS",
        "category": "Sosial & Kebijakan",
        "verdict": "FAKTA RESMI",
        "source": "Kemnaker RI & Antara",
        "date": "24 Nov 2026",
        "summary": "Kementerian Ketenagakerjaan mengonfirmasi penyaluran BSU bagi pekerja terdaftar aktif BPJS Ketenagakerjaan melalui Bank Himbara dan PT Pos Indonesia secara bertahap.",
        "sample_text": "Kementerian Ketenagakerjaan resmi mencairkan program Bantuan Subsidi Upah BSU bagi jutaan pekerja berpenghasilan di bawah upah minimum melalui mekanisme transfer rekening bank Himbara."
    }
]

class LiveHoaxFeedService:
    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.rss_url = "https://turnbackhoax.id/feed/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 CekHoaks-Feed-Sync/1.0"
        }

    def _strip_html(self, raw_html: str) -> str:
        clean = re.sub(r"<[^>]+>", " ", raw_html)
        clean = clean.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"').replace("&#8217;", "'").replace("&#8220;", '"').replace("&#8221;", '"')
        return re.sub(r"\s+", " ", clean).strip()

    def _determine_category(self, text: str) -> str:
        t = text.lower()
        if any(k in t for k in ["kesehatan", "obat", "vaksin", "virus", "dokter", "medis", "sakit", "meninggal", "daun", "rebusan"]):
            return "Teknologi & Kesehatan"
        elif any(k in t for k in ["uang", "bansos", "dana", "subsidi", "bantuan", "rekening", "hadiah", "pajak", "bank"]):
            return "Sosial & Kebijakan"
        elif any(k in t for k in ["pemilu", "kpu", "presiden", "menteri", "partai", "dpr", "polisi", "cpns", "bkn", "pemerintah"]):
            return "Pemerintahan & Karir"
        return "Sosial & Kebijakan"

    def fetch_from_mafindo_rss(self, max_items: int = 8) -> list:
        try:
            req = urllib.request.Request(self.rss_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                xml_data = response.read()

            root = ET.fromstring(xml_data)
            items = []

            for item in root.findall("./channel/item")[:max_items]:
                raw_title = item.findtext("title", "")
                link = item.findtext("link", "")
                pub_date = item.findtext("pubDate", "")
                description = item.findtext("description", "")

                # Clean Title
                clean_title = re.sub(r"^\[.*?\]\s*", "", raw_title).strip()
                if not clean_title:
                    clean_title = raw_title

                # Format Date
                date_str = pub_date[:16] if pub_date else datetime.now().strftime("%d %b %Y")
                try:
                    dt = datetime.strptime(pub_date[:16].strip(), "%a, %d %b %Y")
                    date_str = dt.strftime("%d %b %Y")
                except Exception:
                    pass

                # Clean Summary
                clean_summary = self._strip_html(description)
                if len(clean_summary) > 170:
                    clean_summary = clean_summary[:167] + "..."

                # Verdict
                verdict = "HOAKS"
                if any(tag in raw_title.upper() for tag in ["[BENAR]", "[FAKTA]", "[KLARIFIKASI]"]):
                    verdict = "FAKTA RESMI"

                category = self._determine_category(raw_title + " " + clean_summary)

                sample_text = f"{clean_title}. {clean_summary}"
                if len(sample_text) < 50:
                    sample_text = f"Pesan klarifikasi resmi terkait: {clean_title}. Informasi tersebut disebarkan tanpa rujukan data ilmiah yang dapat dipertanggungjawabkan."

                items.append({
                    "title": clean_title,
                    "category": category,
                    "verdict": verdict,
                    "source": "MAFINDO (TurnBackHoax.id)",
                    "date": date_str,
                    "link": link,
                    "summary": clean_summary,
                    "sample_text": sample_text
                })

            if items:
                # Save to cache
                cache_payload = {
                    "last_synced": time.time(),
                    "last_synced_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB"),
                    "count": len(items),
                    "items": items
                }
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(cache_payload, f, ensure_ascii=False, indent=2)
                return items
        except Exception as e:
            print(f"[!] Gagal fetch live RSS MAFINDO ({e}), beralih ke cache/fallback.")

        return self.get_cached_or_fallback()

    def get_cached_or_fallback(self) -> list:
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                items = cache.get("items", [])
                if items:
                    return items
            except Exception:
                pass
        return CURATED_FALLBACK

    def get_feed(self, force_refresh: bool = False) -> dict:
        now = time.time()
        # Periksa apakah cache masih segar
        if not force_refresh and os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                age = now - cache.get("last_synced", 0)
                if age < CACHE_TTL_SECONDS and cache.get("items"):
                    return {
                        "success": True,
                        "source": "cache",
                        "last_synced": cache.get("last_synced_str", "Baru saja"),
                        "count": len(cache["items"]),
                        "data": cache["items"]
                    }
            except Exception:
                pass

        # Ambil live dari MAFINDO
        items = self.fetch_from_mafindo_rss()
        return {
            "success": True,
            "source": "live_mafindo",
            "last_synced": datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB"),
            "count": len(items),
            "data": items
        }
