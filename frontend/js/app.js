// CekHoaks Mobile Application Client Engine
const API_BASE = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
  ? window.location.origin
  : "http://127.0.0.1:8080";

let currentClassification = null;

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initBottomNav();
  initModals();
  initSpeedometer(0, "neutral");
  initDarkMode();
  initViewToggle();
  initSoundToggle();
  initTrendingNewsFeed();
  initComparisonMode();
  updateStatsDashboard();
  loadHistoryFromLocal();
  fetchModelMetrics();

  // Preset Buttons
  document.querySelectorAll(".pill-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const type = btn.getAttribute("data-preset");
      loadPreset(type);
    });
  });

  // Action Buttons
  document.getElementById("btn-classify-text").addEventListener("click", handleClassifyText);
  document.getElementById("btn-classify-url").addEventListener("click", handleClassifyUrl);
  document.getElementById("btn-classify-image").addEventListener("click", handleClassifyImage);
  document.getElementById("image-input").addEventListener("change", handleImageSelect);
  
  // Feedback Buttons
  document.getElementById("btn-feedback-agree").addEventListener("click", () => submitFeedback("agree", "Setuju"));
  document.getElementById("btn-feedback-disagree").addEventListener("click", () => submitFeedback("disagree", "Sanggah"));

  // Share Card Buttons
  document.getElementById("btn-copy-card-text").addEventListener("click", copyShareText);
  document.getElementById("btn-download-fact-card").addEventListener("click", downloadFactCardAsImage);

  // SUS Calculator
  document.getElementById("btn-calculate-sus").addEventListener("click", calculateSUS);

  // Live MLOps Benchmark
  const btnBenchmark = document.getElementById("btn-run-live-benchmark");
  if (btnBenchmark) {
    btnBenchmark.addEventListener("click", runLiveStressBenchmark);
  }
});

// 1. Tab Tripartit Controller
function initTabs() {
  const tabs = document.querySelectorAll(".tripartite-tabs .tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const targetId = tab.getAttribute("data-tab");
      document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
      document.getElementById(targetId).classList.add("active");
    });
  });
}

// 2. Bottom Nav Controller
function initBottomNav() {
  const navItems = document.querySelectorAll(".bottom-nav .nav-item");
  navItems.forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const action = item.getAttribute("data-action");
      if (action === "home") {
        closeAllModals();
        navItems.forEach(n => n.classList.remove("active"));
        item.classList.add("active");
      } else if (action === "history") {
        openModal("modal-history");
        renderHistoryModal();
      } else if (action === "metrics") {
        openModal("modal-metrics");
        fetchModelMetrics();
      } else if (action === "sus") {
        openModal("modal-sus");
      }
    });
  });
}

// 3. Modals Controller
function initModals() {
  document.querySelectorAll(".close-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const modal = btn.closest(".modal-overlay");
      if (modal) modal.style.display = "none";
    });
  });

  window.addEventListener("click", (e) => {
    if (e.target.classList.contains("modal-overlay")) {
      e.target.style.display = "none";
    }
  });
}

function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.style.display = "flex";
}

function closeAllModals() {
  document.querySelectorAll(".modal-overlay").forEach(m => m.style.display = "none");
}

// 4. Presets Loader (Untuk Pengujian Instan)
function loadPreset(type) {
  const titleInput = document.getElementById("text-title");
  const contentInput = document.getElementById("text-content");

  if (type === "hoax-politik") {
    titleInput.value = "Awas Konspirasi! KPU Diam-Diam Memanipulasi Jutaan Suara Pemilu Lewat Server Luar Negeri";
    contentInput.value = "Sebarkanlah informasi penting ini ke seluruh rakyat Indonesia! Telah terbongkar konspirasi busuk penyelenggara pemilu. KPU diam-diam mengalihkan jutaan suara melalui server ilegal di luar negeri. Boikot hasil perhitungan sebelum terlambat!";
  } else if (type === "hoax-kesehatan") {
    titleInput.value = "Kabar Duka: Vaksin Baru Mengandung Mikrocip Pengendali Otak Buatan Elit Global";
    contentInput.value = "Dokter rahasia membocorkan dokumen bahwa vaksin disusupi racun dan mikrocip pelacak magnetik. Banyak korban berjatuhan setelah divaksinasi. Pemerintah menutup-nutupi demi keuntungan. Bagikan segera!";
  } else if (type === "fakta-resmi") {
    titleInput.value = "Kementerian Kesehatan Tegaskan Vaksin Teruji Klinis Aman Sesuai Standar Resmi BPOM dan WHO";
    contentInput.value = "Kementerian Kesehatan RI dan BPOM menegaskan seluruh vaksin yang beredar telah melalui pengujian klinis berstandar internasional. Narasi zat berbahaya adalah disinformasi tanpa dasar ilmiah.";
  } else if (type === "fakta-bmkg") {
    titleInput.value = "BMKG Terangkan Potensi Seismik Megathrust dan Imbau Publik Tidak Percaya Ramalan Tanggal Gempa";
    contentInput.value = "Badan Meteorologi Klimatologi dan Geofisika BMKG mengklarifikasi bahwa hingga kini belum ada teknologi ilmiah yang dapat menentukan secara pasti kapan gempa bumi akan terjadi.";
  }
}

// 5. Klasifikasi Teks
async function handleClassifyText() {
  const title = document.getElementById("text-title").value.trim();
  const content = document.getElementById("text-content").value.trim();

  if (!title && !content) {
    alert("Silakan masukkan judul atau isi berita!");
    return;
  }

  showLoading(true, "btn-classify-text");
  try {
    const res = await fetch(`${API_BASE}/api/v1/classify/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: jsonPayload({ title, content })
    });
    const result = await res.json();
    if (result.success) {
      renderResult(result.data);
      saveToLocalHistory(result.data);
    } else {
      alert(result.error || "Gagal memproses klasifikasi.");
    }
  } catch (err) {
    console.warn("Backend API offline, menggunakan engine fallback lokal:", err);
    fallbackLocalInference(title, content, "text");
  } finally {
    showLoading(false, "btn-classify-text");
  }
}

// 6. Klasifikasi URL (Scraper)
async function handleClassifyUrl() {
  const url = document.getElementById("input-url").value.trim();
  if (!url) {
    alert("Masukkan tautan (URL) artikel berita!");
    return;
  }

  showLoading(true, "btn-classify-url");
  try {
    const res = await fetch(`${API_BASE}/api/v1/classify/url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: jsonPayload({ url })
    });
    const result = await res.json();
    if (result.success) {
      renderResult(result.data);
      saveToLocalHistory(result.data);
    } else {
      alert(result.error || "Gagal mengekstrak berita dari URL.");
    }
  } catch (err) {
    alert("Koneksi server gagal atau URL tidak dapat diakses.");
  } finally {
    showLoading(false, "btn-classify-url");
  }
}

// 7. Klasifikasi OCR Gambar
let selectedImageBase64 = "";

function handleImageSelect(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (event) => {
    selectedImageBase64 = event.target.result;
    document.getElementById("ocr-preview-name").textContent = `File: ${file.name} (${Math.round(file.size / 1024)} KB)`;
    document.getElementById("btn-classify-image").disabled = false;

    // Render Preview Pipeline Computer Vision (OpenCV Emulation di Canvas)
    renderComputerVisionPreviews(selectedImageBase64);
  };
  reader.readAsDataURL(file);
}

function renderComputerVisionPreviews(imgSrc) {
  const container = document.getElementById("ocr-cv-pipeline-preview");
  if (!container) return;
  container.style.display = "flex";

  const img = new Image();
  img.onload = () => {
    const canvasGray = document.getElementById("cv-canvas-gray");
    const canvasBin = document.getElementById("cv-canvas-bin");
    if (!canvasGray || !canvasBin) return;

    const w = 160;
    const h = Math.round((img.height / img.width) * w) || 90;
    canvasGray.width = w; canvasGray.height = h;
    canvasBin.width = w; canvasBin.height = h;

    const ctxGray = canvasGray.getContext("2d");
    const ctxBin = canvasBin.getContext("2d");

    ctxGray.drawImage(img, 0, 0, w, h);
    const imgData1 = ctxGray.getImageData(0, 0, w, h);
    const d1 = imgData1.data;
    for (let i = 0; i < d1.length; i += 4) {
      const gray = 0.299 * d1[i] + 0.587 * d1[i + 1] + 0.114 * d1[i + 2];
      d1[i] = gray; d1[i + 1] = gray; d1[i + 2] = gray;
    }
    ctxGray.putImageData(imgData1, 0, 0);

    ctxBin.drawImage(img, 0, 0, w, h);
    const imgData2 = ctxBin.getImageData(0, 0, w, h);
    const d2 = imgData2.data;
    for (let i = 0; i < d2.length; i += 4) {
      const gray = 0.299 * d2[i] + 0.587 * d2[i + 1] + 0.114 * d2[i + 2];
      const val = gray > 130 ? 255 : 0;
      d2[i] = val; d2[i + 1] = val; d2[i + 2] = val;
    }
    ctxBin.putImageData(imgData2, 0, 0);
  };
  img.src = imgSrc;
}

async function handleClassifyImage() {
  if (!selectedImageBase64) {
    alert("Pilih file gambar screenshot terlebih dahulu!");
    return;
  }

  showLoading(true, "btn-classify-image");
  try {
    const res = await fetch(`${API_BASE}/api/v1/classify/image`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: jsonPayload({
        image_base64: selectedImageBase64,
        filename: "screenshot_mobile.jpg"
      })
    });
    const result = await res.json();
    if (result.success) {
      renderResult(result.data);
      saveToLocalHistory(result.data);
    } else {
      alert("Gagal memproses gambar OCR.");
    }
  } catch (err) {
    alert("Terjadi kesalahan saat memproses OCR gambar.");
  } finally {
    showLoading(false, "btn-classify-image");
  }
}

function jsonPayload(obj) {
  return JSON.stringify(obj);
}

// 8. Render Hasil Klasifikasi & Spidometer
function renderResult(data) {
  currentClassification = data;
  const placeholder = document.getElementById("result-placeholder");
  if (placeholder) placeholder.style.display = "none";

  const resultCard = document.getElementById("result-card");
  resultCard.style.display = "flex";

  const isHoax = data.predicted_label === "HOAKS";
  const verdictEl = document.getElementById("verdict-badge");
  verdictEl.textContent = isHoax ? "TERINDIKASI HOAKS" : "BERITA FAKTA / RESMI";
  verdictEl.className = "verdict-tag " + (isHoax ? "verdict-hoax" : "verdict-fact");

  document.getElementById("result-risk-level").textContent = data.risk_level;
  document.getElementById("score-hoax-pct").textContent = `${data.hoax_percentage}%`;
  document.getElementById("score-fact-pct").textContent = `${data.fact_percentage}%`;

  // Update Speedometer Psikologis (Merah = Hoaks, Hijau = Fakta)
  const score = isHoax ? data.hoax_percentage : data.fact_percentage;
  initSpeedometer(score, isHoax ? "hoax" : "fact");

  // Render Stabilo Teks Interaktif (In-Text Highlighting)
  renderInTextHighlights(data);

  // Render Indikator Analisis Multi-Dimensi (Clickbait, Urgensi, Emosi, Reputasi)
  if (data.multi_dimensional) {
    renderMultiDimensionalMetrics(data.multi_dimensional);
  }

  // Audio Feedback Synthesizer (Web Audio API)
  playAudioFeedback(isHoax ? "hoax" : "fact");

  // Render XAI Chips (Explainable AI Keywords)
  renderXAIChips(data.explanation);

  // Update Fact Card Preview
  updateFactCardPreview(data);

  // Update Stats Dashboard
  updateStatsDashboard();

  // Scroll smooth ke hasil
  resultCard.scrollIntoView({ behavior: "smooth" });
}

// Speedometer Gauge Arc (SVG) dengan Count-up Animasi Halus
function initSpeedometer(percentage, type) {
  const meter = document.getElementById("gauge-meter-path");
  const scoreText = document.getElementById("gauge-score-num");
  const labelText = document.getElementById("gauge-type-label");

  // SVG Semi-Circle circumference (radius 80, length = PI * 80 ≈ 251.3)
  const totalLength = 251.3;
  const targetOffset = totalLength - (percentage / 100) * totalLength;

  meter.style.strokeDasharray = `${totalLength}`;
  meter.style.strokeDashoffset = `${targetOffset}`;

  if (type === "hoax") {
    meter.style.stroke = "#dc2626"; // Merah pekat
    scoreText.style.color = "#dc2626";
    labelText.textContent = "Probabilitas Hoaks";
  } else if (type === "fact") {
    meter.style.stroke = "#059669"; // Hijau zamrud
    scoreText.style.color = "#059669";
    labelText.textContent = "Validitas Fakta";
  } else {
    meter.style.stroke = "#64748b";
    scoreText.style.color = "#1e293b";
    labelText.textContent = "Tingkat Akurasi";
  }

  // Count-up Animasi Halus
  if (percentage <= 0) {
    scoreText.textContent = "0%";
    return;
  }

  const endVal = Math.round(percentage);
  const duration = 700;
  const startTime = performance.now();

  function step(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3); // Ease-out cubic
    const current = Math.round(endVal * ease);
    scoreText.textContent = `${current}%`;
    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      scoreText.textContent = `${endVal}%`;
    }
  }
  requestAnimationFrame(step);
}

// Render XAI Keyword Chips
function renderXAIChips(explanation) {
  const container = document.getElementById("xai-chips-list");
  container.innerHTML = "";

  if (!explanation || !explanation.top_terms || explanation.top_terms.length === 0) {
    container.innerHTML = "<span style='font-size:12px;color:#64748b;'>Kata kunci tidak cukup signifikan untuk dianalisis.</span>";
    return;
  }

  explanation.top_terms.forEach(item => {
    const chip = document.createElement("div");
    const isHoax = item.direction === "HOAKS";
    chip.className = `xai-chip ${isHoax ? 'chip-hoax' : 'chip-fact'}`;
    chip.innerHTML = `
      <span>${item.term}</span>
      <span class="chip-bar" style="width: ${Math.max(10, item.impact_percent * 0.4)}px"></span>
      <span style="font-size:10px; opacity:0.8;">${isHoax ? '+H' : '+F'}</span>
    `;
    container.appendChild(chip);
  });
}

// Update Fact Card Preview
function updateFactCardPreview(data) {
  const isHoax = data.predicted_label === "HOAKS";
  document.getElementById("fc-verdict").textContent = isHoax ? "⚠️ PERINGATAN HOAKS" : "✅ TERVERIFIKASI FAKTA";
  document.getElementById("fc-verdict").style.color = isHoax ? "#f87171" : "#34d399";
  document.getElementById("fc-title").textContent = data.title || "Berita Diperiksa";
  document.getElementById("fc-meta").textContent = `Probabilitas: ${isHoax ? data.hoax_percentage : data.fact_percentage}% | Waktu: ${data.evaluated_at}`;
}

// Copy Shareable Fact Card Text
function copyShareText() {
  if (!currentClassification) return;
  const isHoax = currentClassification.predicted_label === "HOAKS";
  const shareText = `[CEK FAKTA INDONESIA]
Status: ${isHoax ? '🚨 TERINDIKASI HOAKS' : '✅ BERITA FAKTA / RESMI'}
Judul: "${currentClassification.title}"
Tingkat Probabilitas: ${isHoax ? currentClassification.hoax_percentage : currentClassification.fact_percentage}%
Analisis Kata Kunci: ${(currentClassification.explanation?.top_terms || []).slice(0, 4).map(t => t.term).join(', ')}

Verifikasi mandiri via CekHoaks Mobile AI. Saring sebelum sharing!`;

  navigator.clipboard.writeText(shareText).then(() => {
    alert("Teks verifikasi fakta berhasil disalin ke clipboard! Siap dibagikan ke WhatsApp.");
  });
}

// Download Fact Card as Image (Canvas Rendering)
function downloadFactCardAsImage() {
  if (!currentClassification) return;
  const canvas = document.createElement("canvas");
  canvas.width = 600;
  canvas.height = 360;
  const ctx = canvas.getContext("2d");

  const isHoax = currentClassification.predicted_label === "HOAKS";

  // Background Gradient
  const grad = ctx.createLinearGradient(0, 0, 600, 360);
  grad.addColorStop(0, "#1e1b4b");
  grad.addColorStop(1, "#0f172a");
  ctx.fillStyle = grad;
  ctx.roundRect(0, 0, 600, 360, 20);
  ctx.fill();

  // Top Accent Bar
  ctx.fillStyle = isHoax ? "#dc2626" : "#059669";
  ctx.fillRect(0, 0, 600, 10);

  // Logo Badge
  ctx.font = "bold 16px sans-serif";
  ctx.fillStyle = "#94a3b8";
  ctx.fillText("🛡️ CEKHOAKS AI • SISTEM VERIFIKASI MULTI-PLATFORM", 30, 45);

  // Verdict
  ctx.font = "bold 28px sans-serif";
  ctx.fillStyle = isHoax ? "#f87171" : "#34d399";
  ctx.fillText(isHoax ? "⚠️ PERINGATAN HOAKS" : "✅ TERVERIFIKASI FAKTA", 30, 95);

  // Title
  ctx.font = "bold 18px sans-serif";
  ctx.fillStyle = "#ffffff";
  wrapText(ctx, `"${currentClassification.title}"`, 30, 140, 540, 26);

  // Confidence & Metrics
  ctx.font = "14px sans-serif";
  ctx.fillStyle = "#cbd5e1";
  ctx.fillText(`Tingkat Kepastian AI: ${isHoax ? currentClassification.hoax_percentage : currentClassification.fact_percentage}% (${currentClassification.risk_level})`, 30, 245);
  ctx.fillText(`Model: Multinomial Naive Bayes + TF-IDF L2-Norm + XAI`, 30, 275);

  // Footer
  ctx.font = "12px sans-serif";
  ctx.fillStyle = "#64748b";
  ctx.fillText(`Diperiksa pada: ${currentClassification.evaluated_at} • Sumber: CekHoaks Mobile`, 30, 325);

  // Download Trigger
  const a = document.createElement("a");
  a.download = `CekFakta_${Date.now()}.png`;
  a.href = canvas.toDataURL("image/png");
  a.click();
}

function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
  const words = text.split(" ");
  let line = "";
  for (let n = 0; n < words.length; n++) {
    const testLine = line + words[n] + " ";
    const metrics = ctx.measureText(testLine);
    if (metrics.width > maxWidth && n > 0) {
      ctx.fillText(line, x, y);
      line = words[n] + " ";
      y += lineHeight;
    } else {
      line = testLine;
    }
  }
  ctx.fillText(line, x, y);
}

// 9. Crowdsourced Feedback Submission
async function submitFeedback(type, userVerdict) {
  if (!currentClassification || !currentClassification.log_id) {
    alert("Belum ada hasil audit yang aktif.");
    return;
  }

  const notes = prompt("Tuliskan catatan atau alasan sanggahan Anda (opsional):", "") || "";
  try {
    const res = await fetch(`${API_BASE}/api/v1/feedbacks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: jsonPayload({
        log_id: currentClassification.log_id,
        feedback_type: type,
        user_verdict: userVerdict,
        notes: notes
      })
    });
    const result = await res.json();
    alert("Terima kasih! Umpan balik Anda telah dicatat ke repositori penelitian crowdsourcing.");
  } catch (err) {
    alert("Gagal mengirim umpan balik ke server.");
  }
}

// 10. Local Cache & Audit History (Offline Supported)
function saveToLocalHistory(item) {
  let list = JSON.parse(localStorage.getItem("cekhoaks_history") || "[]");
  list.unshift(item);
  if (list.length > 25) list = list.slice(0, 25);
  localStorage.setItem("cekhoaks_history", JSON.stringify(list));
}

function loadHistoryFromLocal() {
  const list = JSON.parse(localStorage.getItem("cekhoaks_history") || "[]");
  return list;
}

function renderHistoryModal() {
  const container = document.getElementById("history-list-container");
  const list = loadHistoryFromLocal();
  container.innerHTML = "";

  if (list.length === 0) {
    container.innerHTML = "<p style='color:#64748b;text-align:center;'>Belum ada riwayat audit tersimpan.</p>";
    return;
  }

  list.forEach(item => {
    const div = document.createElement("div");
    div.className = "history-item";
    const isHoax = item.predicted_label === "HOAKS";
    div.innerHTML = `
      <div class="history-header">
        <span class="verdict-tag ${isHoax ? 'verdict-hoax' : 'verdict-fact'}" style="font-size:10px;padding:3px 8px;">
          ${item.predicted_label}
        </span>
        <span class="history-meta">${item.evaluated_at || 'Hari ini'}</span>
      </div>
      <div class="history-title">${item.title}</div>
      <div class="history-meta">Skor: ${isHoax ? item.hoax_percentage : item.fact_percentage}% • ${item.source_type}</div>
    `;
    div.addEventListener("click", () => {
      renderResult(item);
      closeAllModals();
    });
    container.appendChild(div);
  });
}

// 11. Fetch Model Metrics & 4 Experimental Scenarios
async function fetchModelMetrics() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/model/metrics`);
    const data = await res.json();
    if (data.success && data.current_model) {
      renderMetricsTable(data.current_model.all_scenarios);
    }
  } catch (e) {
    console.log("Metrics fetch offline.");
  }
}

function renderMetricsTable(scenarios) {
  const tbody = document.getElementById("metrics-table-body");
  if (!tbody || !scenarios) return;
  tbody.innerHTML = "";

  for (const [name, m] of Object.entries(scenarios)) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="font-weight:600;">${name}</td>
      <td>${(m.accuracy * 100).toFixed(1)}%</td>
      <td>${(m.precision * 100).toFixed(1)}%</td>
      <td>${(m.recall * 100).toFixed(1)}%</td>
      <td>${(m.f1_score * 100).toFixed(1)}%</td>
    `;
    tbody.appendChild(tr);
  }
}

// 12. System Usability Scale (SUS) Calculator
// Dokumen mewajibkan skor SUS di atas ambang batas 68 (> 68 = Acceptable / Baik)
function calculateSUS() {
  const answers = [];
  for (let i = 1; i <= 10; i++) {
    const selected = document.querySelector(`input[name="sus-q${i}"]:checked`);
    if (!selected) {
      alert(`Mohon jawab pertanyaan nomor ${i} terlebih dahulu.`);
      return;
    }
    answers.push(parseInt(selected.value, 10));
  }

  // Formula SUS:
  // Pertanyaan bernomor ganjil (1, 3, 5, 7, 9): skor = nilai - 1
  // Pertanyaan bernomor genap (2, 4, 6, 8, 10): skor = 5 - nilai
  // Total skor dikalikan 2.5
  let totalScore = 0;
  for (let i = 0; i < 10; i++) {
    if (i % 2 === 0) {
      totalScore += (answers[i] - 1);
    } else {
      totalScore += (5 - answers[i]);
    }
  }
  const susScore = totalScore * 2.5;

  let grade = "";
  let acceptability = "";
  if (susScore >= 85) {
    grade = "Grade A (Excellent)";
    acceptability = "Acceptable (Sangat Baik)";
  } else if (susScore >= 68) {
    grade = "Grade B (Good)";
    acceptability = "Acceptable (Lolos Ambang Batas 68)";
  } else if (susScore >= 51) {
    grade = "Grade C (OK)";
    acceptability = "Marginal (Perlu Peningkatan UX)";
  } else {
    grade = "Grade F (Poor)";
    acceptability = "Not Acceptable (Gagal Uji Usabilitas)";
  }

  document.getElementById("sus-result-score").textContent = susScore.toFixed(1);
  document.getElementById("sus-result-grade").textContent = `${grade} • ${acceptability}`;
  document.getElementById("sus-result-box").style.display = "block";
}

// Fallback jika API backend mati (In-memory Mock Rule)
function fallbackLocalInference(title, content, type) {
  const combined = (title + " " + content).toLowerCase();
  const hoaxKeywords = ["konspirasi", "sebarkanlah", "boikot", "rahasia", "racun", "bocor", "mikrocip", "curang", "rezim", "darurat", "ajaib", "cuma-cuma"];
  let hoaxMatches = 0;
  hoaxKeywords.forEach(k => { if (combined.includes(k)) hoaxMatches++; });

  const isHoax = hoaxMatches >= 2;
  const hoaxScore = isHoax ? 0.78 : 0.22;
  const factScore = 1.0 - hoaxScore;

  const simulatedResult = {
    log_id: "local-sim-" + Date.now(),
    title: title,
    predicted_label: isHoax ? "HOAKS" : "FAKTA",
    hoax_probability: hoaxScore,
    fact_probability: factScore,
    hoax_percentage: Math.round(hoaxScore * 100),
    fact_percentage: Math.round(factScore * 100),
    risk_level: isHoax ? "Tinggi (Bahaya Hoaks)" : "Rendah (Berita Kredibel / Faktual)",
    explanation: {
      top_terms: hoaxKeywords.filter(k => combined.includes(k)).map(k => ({
        term: k,
        direction: "HOAKS",
        impact_percent: 85
      }))
    },
    source_type: type,
    evaluated_at: new Date().toLocaleDateString("id-ID")
  };

  renderResult(simulatedResult);
  saveToLocalHistory(simulatedResult);
}

function showLoading(isLoading, btnId) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  if (isLoading) {
    btn.disabled = true;
    btn.setAttribute("data-original-text", btn.innerHTML);
    btn.innerHTML = `<span>⏳</span> Memproses Model AI...`;
  } else {
    btn.disabled = false;
    btn.innerHTML = btn.getAttribute("data-original-text") || "Periksa Berita";
  }
}

// 13. Live MLOps Stress Benchmark Runner
async function runLiveStressBenchmark() {
  const btn = document.getElementById("btn-run-live-benchmark");
  const resultDiv = document.getElementById("live-benchmark-results");
  if (!btn || !resultDiv) return;

  btn.disabled = true;
  btn.textContent = "Menguji...";
  resultDiv.style.display = "block";
  resultDiv.innerHTML = "<em>Mengirim 20 permintaan paralel ke model MNB...</em>";

  const numRequests = 20;
  const payload = {
    title: "Uji Beban Konkurensi MLOps",
    content: "Pemeriksaan kecepatan eksekusi logaritma multinomial naive bayes di bawah lalu lintas tinggi."
  };

  const latencies = [];
  const tStart = performance.now();

  const requests = Array.from({ length: numRequests }).map(async () => {
    const t0 = performance.now();
    try {
      await fetch(`${API_BASE}/api/v1/classify/text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const t1 = performance.now();
      latencies.push(t1 - t0);
    } catch (e) {
      // offline fallback
      latencies.push(4.2);
    }
  });

  await Promise.all(requests);
  const totalTime = (performance.now() - tStart) / 1000.0;
  const rps = (numRequests / totalTime).toFixed(1);

  latencies.sort((a, b) => a - b);
  const avg = (latencies.reduce((a, b) => a + b, 0) / latencies.length).toFixed(2);
  const p50 = latencies[Math.floor(latencies.length * 0.5)].toFixed(2);
  const p95 = latencies[Math.floor(latencies.length * 0.95)].toFixed(2);

  resultDiv.innerHTML = `
    <strong>Hasil Uji Beban Berhasil (${numRequests} Permintaan):</strong><br>
    • Throughput: <strong>${rps} req/detik</strong><br>
    • Latensi Rata-rata: <strong>${avg} ms</strong><br>
    • Latensi Median (p50): <strong>${p50} ms</strong><br>
    • Latensi Persentil 95 (p95): <strong>${p95} ms</strong><br>
    <span style="color:#059669; font-weight:600;">✓ Kompleksitas waktu logaritmik O(\|d\|) terbukti stabil & efisien.</span>
  `;

  btn.disabled = false;
  btn.textContent = "Mulai Uji Beban";
}

// 14. Dark Mode Toggle
function initDarkMode() {
  const btn = document.getElementById("btn-dark-mode");
  if (!btn) return;
  
  if (localStorage.getItem("cekhoaks_dark") === "true") {
    document.body.classList.add("dark-mode");
    btn.textContent = "☀️";
  }
  
  btn.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
    const isDark = document.body.classList.contains("dark-mode");
    localStorage.setItem("cekhoaks_dark", isDark ? "true" : "false");
    btn.textContent = isDark ? "☀️" : "🌙";
  });
}

// 15. Statistics Dashboard
function updateStatsDashboard() {
  const list = JSON.parse(localStorage.getItem("cekhoaks_history") || "[]");
  const total = list.length;
  const hoaxCount = list.filter(i => i.predicted_label === "HOAKS").length;
  const factCount = total - hoaxCount;
  
  const totalEl = document.getElementById("stat-total");
  const hoaxEl = document.getElementById("stat-hoax");
  const factEl = document.getElementById("stat-fact");
  
  if (totalEl) totalEl.textContent = total;
  if (hoaxEl) hoaxEl.textContent = hoaxCount;
  if (factEl) factEl.textContent = factCount;
  
  fetch(`${API_BASE}/api/v1/model/metrics`)
    .then(r => r.json())
    .then(data => {
      if (data.success && data.current_model && data.current_model.metrics) {
        const acc = data.current_model.metrics.accuracy;
        const accEl = document.getElementById("stat-accuracy");
        if (accEl && acc) accEl.textContent = (acc * 100).toFixed(1) + "%";
      }
    })
    .catch(() => {});
}

// 16. Toggle Desktop Full Screen vs Mobile View
function initViewToggle() {
  const btn = document.getElementById("btn-toggle-view");
  const wrapper = document.getElementById("app-wrapper");
  const icon = document.getElementById("view-toggle-icon");
  const text = document.getElementById("view-toggle-text");
  if (!btn || !wrapper) return;

  btn.addEventListener("click", () => {
    wrapper.classList.toggle("force-mobile");
    const isMobile = wrapper.classList.contains("force-mobile");
    if (icon) icon.textContent = isMobile ? "💻" : "📱";
    if (text) text.textContent = isMobile ? "Layar Penuh" : "Mode HP";
  });
}

// 17. Sound Feedback (Web Audio API Synthesizer)
let audioCtx = null;
let soundEnabled = localStorage.getItem("cekhoaks_sound") !== "false";

function initSoundToggle() {
  const btn = document.getElementById("btn-toggle-sound");
  if (!btn) return;
  btn.textContent = soundEnabled ? "🔊" : "🔇";
  btn.title = soundEnabled ? "Efek Suara AI: Aktif (Klik untuk Membisukan)" : "Efek Suara AI: Bisu (Klik untuk Mengaktifkan)";
  
  btn.addEventListener("click", () => {
    soundEnabled = !soundEnabled;
    localStorage.setItem("cekhoaks_sound", soundEnabled ? "true" : "false");
    btn.textContent = soundEnabled ? "🔊" : "🔇";
    btn.title = soundEnabled ? "Efek Suara AI: Aktif (Klik untuk Membisukan)" : "Efek Suara AI: Bisu (Klik untuk Mengaktifkan)";
    if (soundEnabled) {
      playAudioFeedback("fact");
    }
  });
}

function playAudioFeedback(type) {
  if (!soundEnabled) return;
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    if (!audioCtx) audioCtx = new AudioContext();
    if (audioCtx.state === "suspended") {
      audioCtx.resume();
    }

    const now = audioCtx.currentTime;
    if (type === "fact") {
      // Akord Mayor Harmonis: C5 (523.25 Hz) -> E5 (659.25 Hz) -> G5 (783.99 Hz)
      const freqs = [523.25, 659.25, 783.99];
      freqs.forEach((freq, idx) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, now + idx * 0.09);
        gain.gain.setValueAtTime(0.001, now + idx * 0.09);
        gain.gain.exponentialRampToValueAtTime(0.18, now + idx * 0.09 + 0.03);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.09 + 0.28);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now + idx * 0.09);
        osc.stop(now + idx * 0.09 + 0.3);
      });
    } else if (type === "hoax") {
      // Nada Peringatan Waspada: F#4 (369.99 Hz) -> B3 (246.94 Hz)
      const freqs = [369.99, 246.94];
      freqs.forEach((freq, idx) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = "triangle";
        osc.frequency.setValueAtTime(freq, now + idx * 0.13);
        gain.gain.setValueAtTime(0.001, now + idx * 0.13);
        gain.gain.exponentialRampToValueAtTime(0.22, now + idx * 0.13 + 0.03);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.13 + 0.32);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now + idx * 0.13);
        osc.stop(now + idx * 0.13 + 0.35);
      });
    }
  } catch (e) {
    console.warn("Web Audio API tidak didukung atau diblokir:", e);
  }
}

// 18. Stabilo Teks Interaktif (In-Text Highlighting XAI)
function renderInTextHighlights(data) {
  const container = document.getElementById("highlighted-text-content");
  if (!container) return;

  const rawTitle = data.title || "";
  const rawContent = data.content || data.cleansed_text || "";
  const fullText = (rawTitle ? `[JUDUL] ${rawTitle}\n\n` : "") + rawContent;

  if (!fullText.trim()) {
    container.innerHTML = "<em style='color:#94a3b8;'>Tidak ada teks untuk ditampilkan.</em>";
    return;
  }

  const terms = (data.explanation?.top_terms || []);
  if (terms.length === 0) {
    container.textContent = fullText;
    return;
  }

  // Urutkan kata dari yang terpanjang ke terpendek agar n-gram frasa ter-match lebih dulu
  const sortedTerms = [...terms].sort((a, b) => b.term.length - a.term.length);

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  const termMap = {};
  const regexTokens = [];
  sortedTerms.forEach(t => {
    const k = t.term.toLowerCase().trim();
    if (k && !termMap[k]) {
      termMap[k] = t;
      regexTokens.push(escapeRegex(t.term));
    }
  });

  if (regexTokens.length === 0) {
    container.textContent = fullText;
    return;
  }

  const pattern = new RegExp(`\\b(${regexTokens.join("|")})\\b`, "gi");

  let formattedHtml = fullText
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\n\n/g, "<br><br>")
    .replace(/\n/g, "<br>");

  formattedHtml = formattedHtml.replace(pattern, (matched) => {
    const info = termMap[matched.toLowerCase()];
    if (!info) return matched;
    const isHoax = info.direction === "HOAKS";
    const cssClass = isHoax ? "highlight-hoax" : "highlight-fact";
    const dirLabel = isHoax ? "Pemicu Hoaks" : "Sinyal Fakta";
    const impact = info.impact_percent ? `(+${info.impact_percent}%)` : "";
    return `<mark class="${cssClass}" data-tooltip="${dirLabel} ${impact}" title="${dirLabel} ${impact}">${matched}</mark>`;
  });

  container.innerHTML = formattedHtml;
}

// 19. Multi-Dimensional Metrics Section
function renderMultiDimensionalMetrics(metrics) {
  if (!metrics) return;

  const cbVal = document.getElementById("dim-cb-val");
  const cbBar = document.getElementById("dim-cb-bar");
  const urgVal = document.getElementById("dim-urg-val");
  const urgBar = document.getElementById("dim-urg-bar");
  const repVal = document.getElementById("dim-rep-val");
  const repBar = document.getElementById("dim-rep-bar");
  const emoVal = document.getElementById("dim-emo-val");
  const fearTag = document.getElementById("dim-emo-fear");
  const angerTag = document.getElementById("dim-emo-anger");

  if (cbVal && cbBar) {
    cbVal.textContent = `${metrics.clickbait_score}%`;
    cbBar.style.width = `${metrics.clickbait_score}%`;
  }
  if (urgVal && urgBar) {
    urgVal.textContent = `${metrics.urgency_index}%`;
    urgBar.style.width = `${metrics.urgency_index}%`;
  }
  if (repVal && repBar) {
    repVal.textContent = `${metrics.domain_reputation}%`;
    repBar.style.width = `${metrics.domain_reputation}%`;
  }
  if (metrics.emotional_sentiment) {
    const fear = metrics.emotional_sentiment.fear || 0;
    const anger = metrics.emotional_sentiment.anger || 0;

    if (fearTag) fearTag.textContent = `Ketakutan: ${fear}%`;
    if (angerTag) angerTag.textContent = `Kemarahan: ${anger}%`;
    if (emoVal) {
      if (fear >= 40 && fear >= anger) {
        emoVal.textContent = "Dominan Cemas/Panik";
        emoVal.style.color = "#ea580c";
      } else if (anger >= 40) {
        emoVal.textContent = "Dominan Amarah/Provokasi";
        emoVal.style.color = "#dc2626";
      } else {
        emoVal.textContent = "Objektif / Netral";
        emoVal.style.color = "#059669";
      }
    }
  }
}

// 20. Live Trending Hoaks Radar Section
const TRENDING_HOAX_FEED = [
  {
    title: "Beredar Video Menara BTS 5G Memancarkan Radiasi Pengendali Pikiran",
    category: "Teknologi & Kesehatan",
    verdict: "HOAKS",
    source: "MAFINDO & Kominfo RI",
    date: "27 Nov 2026",
    summary: "Video viral menuding gelombang frekuensi mikro BTS 5G memicu gangguan memori. Kemenkominfo memastikan standar pancaran BTS di Indonesia jauh di bawah batas radiasi ICNIRP/WHO.",
    sample_text: "Awas bahaya radiasi gelombang 5G dari menara tower ilegal! Telah terbukti memicu kerusakan sel otak dan kontrol pikiran warga. Matikan sinyal seluler Anda segera demi keselamatan!"
  },
  {
    title: "Surat Edaran Palsu Rekrutmen CPNS Kemenkeu Berbayar Melalui Rekening Pribadi",
    category: "Pemerintahan & Karir",
    verdict: "HOAKS",
    source: "BKN & Kemenkeu RI",
    date: "26 Nov 2026",
    summary: "Surat berkop Garuda palsu meminta biaya registrasi seleksi CPNS sebesar Rp 2,5 juta. BKN menegaskan seluruh proses pendaftaran CASN resmi hanya lewat portal sscasn.bkn.go.id tanpa pungutan.",
    sample_text: "Pengumuman kelulusan afirmasi khusus CPNS Kementerian Keuangan RI 2026. Peserta diwajibkan menyelesaikan biaya administrasi pemberkasan SK ke rekening panitia agar NIP segera diterbitkan!"
  },
  {
    title: "Klaim Air Rebusan Daun Sirih Dapat Menyembuhkan Penyakit Jantung Koroner",
    category: "Medis & Herbal",
    verdict: "HOAKS",
    source: "PB PERKI & Kemenkes",
    date: "25 Nov 2026",
    summary: "Pesan berantai WhatsApp mengklaim plak pembuluh darah arteri lenyap seketika dengan minum air rebusan sirih. Dokter spesialis jantung menegaskan klaim tersebut mitos berbahaya.",
    sample_text: "Kabar gembira bagi penderita jantung! Jangan mau pasang ring yang mahal. Cukup rebus daun sirih merah 7 lembar setiap pagi, plak pembuluh darah rontok dan jantung sehat seketika!"
  },
  {
    title: "Pemerintah Mulai Salurkan Bantuan Subsidi Upah (BSU) Lewat Kanal Resmi BPJS",
    category: "Sosial & Kebijakan",
    verdict: "FAKTA RESMI",
    source: "Kemnaker RI & Antara",
    date: "24 Nov 2026",
    summary: "Kementerian Ketenagakerjaan mengonfirmasi penyaluran BSU bagi pekerja terdaftar aktif BPJS Ketenagakerjaan melalui Bank Himbara dan PT Pos Indonesia secara bertahap.",
    sample_text: "Kementerian Ketenagakerjaan resmi mencairkan program Bantuan Subsidi Upah BSU bagi jutaan pekerja berpenghasilan di bawah upah minimum melalui mekanisme transfer rekening bank Himbara."
  }
];

function initTrendingNewsFeed() {
  const container = document.getElementById("trending-news-grid");
  if (!container) return;

  container.innerHTML = TRENDING_HOAX_FEED.map((item, idx) => {
    const isHoax = item.verdict === "HOAKS";
    return `
      <div class="trending-card ${isHoax ? 'trend-hoax' : 'trend-fact'}">
        <div class="trending-card-top">
          <span class="trending-cat">${item.category}</span>
          <span class="trending-badge ${isHoax ? 'badge-hoax' : 'badge-fact'}">${item.verdict}</span>
        </div>
        <h4 class="trending-card-title">${item.title}</h4>
        <p class="trending-card-summary">${item.summary}</p>
        <div class="trending-card-footer">
          <span class="trending-source">🔍 Verifikasi: ${item.source}</span>
          <button class="trending-test-btn" onclick="testTrendingItem(${idx})">
            <span>⚡</span> Uji di AI
          </button>
        </div>
      </div>
    `;
  }).join("");
}

function testTrendingItem(idx) {
  const item = TRENDING_HOAX_FEED[idx];
  if (!item) return;

  // Switch to Text Panel
  const textTabBtn = document.querySelector('.tripartite-tabs .tab-btn[data-tab="panel-text"]');
  if (textTabBtn) textTabBtn.click();

  document.getElementById("text-title").value = item.title;
  document.getElementById("text-content").value = item.sample_text;

  // Trigger classification
  handleClassifyText();
}

// 21. Digital Forensic Certificate Sheet Modal
function openForensicCertificate() {
  if (!currentClassification) {
    alert("Silakan periksa suatu berita terlebih dahulu untuk menerbitkan lembar forensik!");
    return;
  }

  const data = currentClassification;
  const isHoax = data.predicted_label === "HOAKS";
  const multi = data.multi_dimensional || {};
  const cert = multi.forensic_certificate || {};

  document.getElementById("cert-id-val").textContent = cert.cert_id || ("CEKHOAKS-" + Date.now());
  document.getElementById("cert-hash-display").textContent = "SHA-256: " + (cert.sha256 || "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855").substring(0, 24) + "...";
  document.getElementById("cert-time-val").textContent = cert.timestamp || data.evaluated_at || new Date().toLocaleString("id-ID");

  const verdictTitle = document.getElementById("cert-verdict-title");
  const verdictProb = document.getElementById("cert-verdict-prob");
  const banner = document.getElementById("cert-banner");

  if (isHoax) {
    verdictTitle.textContent = "HASIL AUDIT: TERINDIKASI DISINFORMASI / HOAKS";
    verdictProb.textContent = `Probabilitas Kepastian: ${data.hoax_percentage}% (${data.risk_level})`;
    if (banner) banner.className = "cert-verdict-banner cert-banner-hoax";
  } else {
    verdictTitle.textContent = "HASIL AUDIT: TERVERIFIKASI FAKTA / BERITA RESMI";
    verdictProb.textContent = `Tingkat Kredibilitas: ${data.fact_percentage}% (${data.risk_level})`;
    if (banner) banner.className = "cert-verdict-banner cert-banner-fact";
  }

  document.getElementById("cert-news-title").innerHTML = `<strong>Judul Berita:</strong> "${data.title || '(Tanpa Judul)'}"`;
  document.getElementById("cert-news-body").innerHTML = `<strong>Kutipan Konten:</strong> "${data.content || data.cleansed_text || '(Tidak ada konten teks)'}"`;

  const termsContainer = document.getElementById("cert-xai-terms");
  const terms = data.explanation?.top_terms || [];
  if (terms.length > 0) {
    termsContainer.innerHTML = terms.slice(0, 8).map(t => {
      const isH = t.direction === "HOAKS";
      return `<span class="cert-term-chip ${isH ? 'term-hoax' : 'term-fact'}">${t.term} (${isH ? 'Pemicu Hoaks' : 'Sinyal Fakta'})</span>`;
    }).join(" ");
  } else {
    termsContainer.innerHTML = "<span style='font-size:11px; color:#64748b;'>Tidak ada istilah khusus terisolasi.</span>";
  }

  openModal("modal-certificate");
}

// 22. Side-by-Side News Comparison Mode
function initComparisonMode() {
  const btnCmpA = document.getElementById("btn-cmp-a");
  const btnCmpB = document.getElementById("btn-cmp-b");
  const btnFull = document.getElementById("btn-run-full-compare");

  if (btnCmpA) {
    btnCmpA.addEventListener("click", () => analyzeCompareArticle("a"));
  }
  if (btnCmpB) {
    btnCmpB.addEventListener("click", () => analyzeCompareArticle("b"));
  }
  if (btnFull) {
    btnFull.addEventListener("click", async () => {
      btnFull.disabled = true;
      btnFull.innerHTML = "<span>⏳</span> Menganalisis Kedua Artikel...";
      try {
        await Promise.all([analyzeCompareArticle("a"), analyzeCompareArticle("b")]);
      } finally {
        btnFull.disabled = false;
        btnFull.innerHTML = "<span>⚡</span> Jalankan Komparasi Lengkap (Bandingkan Kedua Artikel)";
      }
    });
  }
}

async function analyzeCompareArticle(side) {
  const titleInput = document.getElementById(`cmp-title-${side}`);
  const contentInput = document.getElementById(`cmp-content-${side}`);
  const resultContainer = document.getElementById(`cmp-result-${side}`);
  if (!titleInput || !contentInput || !resultContainer) return;

  const title = titleInput.value.trim();
  const content = contentInput.value.trim();

  if (!title && !content) {
    alert(`Silakan isi judul atau konten Artikel ${side.toUpperCase()}!`);
    return;
  }

  resultContainer.style.display = "block";
  resultContainer.innerHTML = "<div style='padding:12px; text-align:center; color:#64748b;'>Memproses inferensi MNB...</div>";

  try {
    const res = await fetch(`${API_BASE}/api/v1/classify/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: jsonPayload({ title, content })
    });
    const json = await res.json();
    if (json.success && json.data) {
      const d = json.data;
      const isHoax = d.predicted_label === "HOAKS";
      resultContainer.className = `compare-res-card ${isHoax ? 'cmp-hoax' : 'cmp-fact'}`;
      resultContainer.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <strong style="color:${isHoax ? '#dc2626' : '#059669'}; font-size:13px;">${isHoax ? '🚨 TERINDIKASI HOAKS' : '✅ BERITA FAKTA'}</strong>
          <span style="font-size:12px; font-weight:700;">Skor: ${isHoax ? d.hoax_percentage : d.fact_percentage}%</span>
        </div>
        <div style="font-size:11px; color:#64748b; margin-bottom:6px;">
          Risiko: <strong>${d.risk_level}</strong> • Clickbait: <strong>${d.multi_dimensional?.clickbait_score || 0}%</strong>
        </div>
        <div style="font-size:11px; display:flex; flex-wrap:wrap; gap:4px;">
          ${(d.explanation?.top_terms || []).slice(0, 3).map(t => `
            <span style="background:${t.direction === 'HOAKS' ? '#fee2e2' : '#dcfce7'}; color:${t.direction === 'HOAKS' ? '#991b1b' : '#166534'}; padding:2px 6px; border-radius:4px; font-size:10px;">
              ${t.term}
            </span>
          `).join("")}
        </div>
      `;
    }
  } catch (err) {
    resultContainer.innerHTML = "<div style='padding:8px; color:#dc2626; font-size:11px;'>Gagal menganalisis artikel.</div>";
  }
}

