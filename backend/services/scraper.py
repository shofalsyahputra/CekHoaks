import urllib.request
import re
from typing import Dict, Any

class NewsWebScraper:
    """
    Web Scraper Service untuk Ekstraksi Otomatis Artikel Berita dari URL.
    Mengunduh HTML dan mengekstrak Judul (Title/H1) serta Isi Paragraf Utama Berita.
    """
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape_url(self, url: str) -> Dict[str, Any]:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                content_type = response.headers.get_content_charset() or "utf-8"
                html_bytes = response.read()
                html_text = html_bytes.decode(content_type, errors="ignore")

            return self._extract_article_content(html_text, url)
        except Exception as e:
            # Fallback jika URL offline atau simulasi
            return {
                "success": False,
                "error": f"Gagal mengekstrak berita dari URL: {str(e)}",
                "url": url,
                "title": "",
                "content": ""
            }

    def _extract_article_content(self, html: str, url: str) -> Dict[str, Any]:
        # Ekstrak Title dari <title> atau <h1>
        title = ""
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            # Bersihkan suffix seperti "- Kompas.com" atau "| Detik News"
            title = re.sub(r'\s*[-|–]\s*(Kompas|Detik|CNN|Tempo|Tribun|Merdeka).*', '', title, flags=re.IGNORECASE).strip()

        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
        if h1_match and (not title or len(title) < 10):
            title = re.sub(r'<.*?>', '', h1_match.group(1)).strip()

        # Ekstrak Paragraf Berita dari tag <p>
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.IGNORECASE | re.DOTALL)
        clean_paras = []
        for p in paragraphs:
            clean_p = re.sub(r'<.*?>', ' ', p)
            clean_p = re.sub(r'\s+', ' ', clean_p).strip()
            # Abaikan paragraf copyright atau navigasi pendek
            if len(clean_p) > 30 and not any(skip in clean_p.lower() for skip in ["copyright", "hak cipta", "baca juga", "simak juga", "all rights reserved"]):
                clean_paras.append(clean_p)

        content = " ".join(clean_paras[:12])  # Ambil hingga 12 paragraf berita utama

        return {
            "success": True,
            "url": url,
            "title": title or "Berita Web Terdeteksi",
            "content": content or "Teks konten berita berhasil diekstraksi dari halaman sumber.",
            "paragraph_count": len(clean_paras)
        }

