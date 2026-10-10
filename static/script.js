const $ = (id) => document.getElementById(id);
let lastSpoken = "";
let recognition = null;
let isListening = false;
let hasResult = false;
let currentResult = null;

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({
    "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
  }[ch]));
}
function wordCount(text) {
  const trimmed = (text || "").trim();
  return trimmed ? trimmed.split(/\s+/).length : 0;
}
function updateWordCount() {
  $("wordCount").textContent = `${wordCount($("newsText").value)} words`;
}
document.addEventListener("DOMContentLoaded", () => {
  $("year").textContent = new Date().getFullYear();
  $("newsText").addEventListener("input", updateWordCount);
  updateWordCount();
});

async function checkNews() {
  const news = $("newsText").value.trim();
  if (!news) {
    showMessage("Please enter or speak a news article before analyzing it.");
    $("newsText").focus();
    return;
  }
  if (wordCount(news) < 15) {
    showMessage("Please enter at least 15 words for a more useful analysis.");
    $("newsText").focus();
    return;
  }

  $("loading").hidden = false;
  $("emptyState").hidden = true;
  $("result").hidden = true;
  $("checkBtn").disabled = true;
  $("checkBtn").innerHTML = '<span class="spinner spinner-small"></span> Analyzing…';
  $("resultSubtitle").textContent = "Processing your article.";
  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({news, language: $("language").value})
    });
    let data;
    try { data = await response.json(); }
    catch { throw new Error("The server returned an invalid response. Check the Flask terminal."); }
    if (!response.ok) throw new Error(data.error || data.message || "The server could not analyze this article.");
    if (data.error) throw new Error(data.error);

    currentResult = {...data, original_news: news, analyzed_at: new Date().toLocaleString()};
    renderResult(currentResult);
    hasResult = true;
    $("pdfBtn").disabled = false;
    $("speakBtn").disabled = false;
    $("resultSubtitle").textContent = "Analysis complete · " + currentResult.analyzed_at;
    lastSpoken = makeSpokenSummary(currentResult);
  } catch (error) {
    showMessage(error.message || "Could not connect to the server. Make sure Flask is running.");
  } finally {
    $("loading").hidden = true;
    $("checkBtn").disabled = false;
    $("checkBtn").innerHTML = "<span>✦</span> Analyze news";
  }
}

function showMessage(message) {
  $("loading").hidden = true;
  $("emptyState").hidden = false;
  $("result").hidden = true;
  $("emptyState").innerHTML = `<div class="empty-illustration">!</div><h3>Unable to analyze</h3><p>${esc(message)}</p>`;
  $("resultSubtitle").textContent = "Please review the input and try again.";
}

function renderResult(data) {
  const raw = String(data.result || data.prediction || data.label || "Unknown");
  const normalized = raw.toLowerCase();
  const isFake = normalized.includes("fake") || normalized.includes("false");
  const isReal = normalized.includes("real") || normalized.includes("true") || normalized.includes("reliable");
  const uncertain = !isFake && !isReal;
  const verdict = isFake ? "POTENTIALLY FAKE" : isReal ? "LIKELY REAL" : raw.toUpperCase();
  const cardClass = isFake ? "fake" : uncertain ? "uncertain" : "";
  const confidenceRaw = Number(data.confidence);
  const confidence = Number.isFinite(confidenceRaw) ? Math.max(0, Math.min(100, confidenceRaw <= 1 ? confidenceRaw * 100 : confidenceRaw)) : null;
  const confidenceText = confidence === null ? "N/A" : `${confidence.toFixed(confidence % 1 ? 1 : 0)}%`;
  const language = data.language_name || data.detected_language || "Not provided";
  const leaning = data.leaning ? `<div class="meta-card"><div class="meta-label">Model insight</div><div class="meta-value">${esc(data.leaning)}</div></div>` : "";
  const fakeWords = Array.isArray(data.fake_words) ? data.fake_words : [];
  const realWords = Array.isArray(data.real_words) ? data.real_words : [];
  const wordChips = (words, fake) => words.length
    ? `<div class="word-chips">${words.map(w => `<span class="word-chip ${fake ? "fake-word" : ""}">${esc(w)}</span>`).join("")}</div>`
    : '<p>No influential words were provided by the model.</p>';
  const translation = data.translated_text
    ? `<div class="translation-card"><h3>Translation used by the model</h3><p>${esc(data.translated_text)}</p></div>` : "";
  $("result").innerHTML = `
    <div class="verdict-card ${cardClass}">
      <div><div class="verdict-label">${esc(verdict)}</div><div class="verdict-subtitle">${isFake ? "The model flags this article as potentially misleading." : isReal ? "The model classifies this article as likely real." : "The model returned an unrecognized label; check your backend output."} This is a prediction, not independent verification.</div></div>
      <div class="confidence-box"><div class="confidence-number">${confidenceText}</div><div class="confidence-caption">Model score</div></div>
    </div>
    <div class="meta-grid">
      <div class="meta-card"><div class="meta-label">Detected language</div><div class="meta-value">${esc(language)}</div></div>
      <div class="meta-card"><div class="meta-label">Confidence / score</div><div class="meta-value">${confidenceText}</div></div>
      <div class="meta-card"><div class="meta-label">Analyzed at</div><div class="meta-value">${esc(currentResult?.analyzed_at || new Date().toLocaleString())}</div></div>
      ${leaning}
    </div>
    <div class="explain-card"><h3>✧ Why did the model predict this?</h3><p>These words are supplied by your model as influential signals. They do not prove a claim is true or false.</p>
      <div class="word-group"><div class="word-group-title">✓ Real-related words</div>${wordChips(realWords, false)}</div>
      <div class="word-group"><div class="word-group-title">⚠ Fake-related words</div>${wordChips(fakeWords, true)}</div>
    </div>
    ${translation}
  `;
  $("emptyState").hidden = true;
  $("result").hidden = false;
}

function makeSpokenSummary(data) {
  const confidence = data.confidence == null ? "" : ` Confidence score: ${data.confidence} percent.`;
  return `Analysis result: ${data.result || data.prediction || "unknown"}.${confidence}`;
}

function eraseAll() {
  if (isListening && recognition) {
    try { recognition.stop(); } catch (_) {}
  }
  isListening = false;
  recognition = null;
  $("newsText").value = "";
  $("language").value = "auto";
  updateWordCount();
  $("result").innerHTML = "";
  $("result").hidden = true;
  $("loading").hidden = true;
  $("emptyState").hidden = false;
  $("emptyState").innerHTML = '<div class="empty-illustration">✦</div><h3>Ready when you are</h3><p>Submit a news article to see the prediction, confidence score, and explanation here.</p>';
  $("resultSubtitle").textContent = "Your prediction will appear here.";
  $("pdfBtn").disabled = true;
  $("speakBtn").disabled = true;
  $("micBtn").textContent = "🎙 Start speaking";
  $("micBtn").classList.remove("is-listening");
  $("checkBtn").disabled = false;
  lastSpoken = "";
  currentResult = null;
  hasResult = false;
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
}

function saveAsPDF() {
  if (!hasResult || !currentResult) return;
  // The browser print dialog includes "Save as PDF" on Chrome, Edge, and most desktop browsers.
  window.print();
}

function toggleMic() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showMessage("Speech recognition is not supported by this browser. Try the latest Google Chrome or Microsoft Edge.");
    return;
  }
  if (isListening && recognition) {
    recognition.stop();
    return;
  }
  recognition = new SpeechRecognition();
  recognition.lang = $("voiceLang").value || "en-IN";
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.onstart = () => {
    isListening = true;
    $("micBtn").textContent = "■ Stop speaking";
    $("micBtn").classList.add("is-listening");
  };
  recognition.onresult = (event) => {
    let finalText = "";
    let interimText = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) finalText += event.results[i][0].transcript + " ";
      else interimText += event.results[i][0].transcript;
    }
    const existing = $("newsText").value.trim();
    if (finalText) $("newsText").value = (existing ? existing + " " : "") + finalText.trim();
    $("newsText").dataset.interim = interimText;
    updateWordCount();
  };
  recognition.onerror = (event) => {
    if (event.error !== "no-speech" && event.error !== "aborted") {
      showMessage(`Microphone error: ${event.error}. Check browser microphone permissions.`);
    }
  };
  recognition.onend = () => {
    isListening = false;
    $("micBtn").textContent = "🎙 Start speaking";
    $("micBtn").classList.remove("is-listening");
    $("newsText").dataset.interim = "";
    if ($("autoCheck").checked && wordCount($("newsText").value) >= 15) checkNews();
  };
  try { recognition.start(); }
  catch (error) { showMessage("Could not start the microphone. Check microphone permissions and try again."); }
}

function speak(text, lang) {
  if (!text) return;
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang || $("voiceLang").value || "en-IN";
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
    return;
  }
  fetch("/tts", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({text, lang: lang || $("voiceLang").value || "en-IN"})
  }).then(async response => {
    if (!response.ok) throw new Error("TTS unavailable");
    const blob = await response.blob();
    const audio = new Audio(URL.createObjectURL(blob));
    await audio.play();
  }).catch(() => showMessage("Text-to-speech is not available in this browser and the server fallback failed."));
}

function speakLast() {
  if (lastSpoken) speak(lastSpoken, currentResult?.speech_lang || $("voiceLang").value);
}
