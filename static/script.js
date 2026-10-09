// ---------- helpers ----------
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

let lastSpoken = null;   // { text, lang } of the latest verdict

// ---------- fake news check ----------
async function checkNews() {
    const newsText = $("newsText").value.trim();
    const language = $("language").value;
    const loading = $("loading");
    const result = $("result");

    result.innerHTML = "";
    if (!newsText) {
        result.textContent = "⚠️ Please enter some news text.";
        return;
    }

    loading.style.display = "block";
    try {
        const response = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ news: newsText, language: language })
        });
        const data = await response.json();
        loading.style.display = "none";

        if (!response.ok) {
            result.textContent = "❌ " + data.error;
            return;
        }

        const chips = (words) => words.map((w) => `<span class="word">${esc(w)}</span>`).join("");

        result.innerHTML = `
            <div class="prediction">
                <div class="prediction-result">${esc(data.result)}</div>
                ${data.low_confidence
                    ? `<div class="confidence">Leaning towards ${esc(data.leaning)} (${esc(data.confidence)}% confidence)</div>
                       <div class="warn">⚠️ The model is not sure about this one. Please check other sources.</div>`
                    : `<div class="confidence">Confidence: ${esc(data.confidence)}%</div>`}
                <div class="lang-chip">🌐 Detected language: ${esc(data.language_name)}</div>
                ${data.translated_text ? `<div class="translated"><strong>English translation used by the model:</strong><br>${esc(data.translated_text)}</div>` : ""}
                <div class="explanation">
                    <h3>🔍 Why did AI predict this?</h3>
                    <p>Words that influenced the prediction${data.translated_text ? " (in the English translation)" : ""}:</p>
                    <div class="important-words">
                        <strong>⚠️ Fake-related words:</strong>
                        <div class="word-list">${chips(data.fake_words) || "None detected"}</div>
                        <br>
                        <strong>✅ Real-related words:</strong>
                        <div class="word-list">${chips(data.real_words) || "None detected"}</div>
                    </div>
                </div>
            </div>`;

        lastSpoken = { text: data.spoken, lang: data.speech_lang };
        $("speakBtn").disabled = false;
        if ($("autoRead").checked) speak(lastSpoken.text, lastSpoken.lang);

    } catch (error) {
        loading.style.display = "none";
        result.textContent = "❌ Unable to connect to the AI server.";
        console.error(error);
    }
}

// ---------- voice input (speech -> text) ----------
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let listening = false;

function setMicUI(on) {
    listening = on;
    const btn = $("micBtn");
    btn.classList.toggle("listening", on);
    btn.textContent = on ? "⏹ Stop listening" : "🎤 Start speaking";
}

function toggleMic() {
    if (!SR) {
        $("result").textContent = "❌ Voice input needs Google Chrome or Microsoft Edge.";
        return;
    }
    if (listening) { recognition.stop(); return; }

    window.speechSynthesis && window.speechSynthesis.cancel();
    recognition = new SR();
    recognition.lang = $("voiceLang").value;
    recognition.interimResults = true;
    recognition.continuous = true;

    const box = $("newsText");
    let finalText = box.value ? box.value.trim() + " " : "";

    recognition.onresult = (e) => {
        let interim = "";
        for (let i = e.resultIndex; i < e.results.length; i++) {
            const t = e.results[i][0].transcript;
            if (e.results[i].isFinal) finalText += t + " ";
            else interim += t;
        }
        box.value = finalText + interim;
    };
    recognition.onerror = (e) => {
        const msg = {
            "not-allowed": "Microphone permission was denied.",
            "no-speech": "I didn't hear anything - try again.",
            "network": "Voice input needs an internet connection.",
            "language-not-supported": "This browser doesn't support that speaking language."
        }[e.error] || "Voice input error: " + e.error;
        $("result").textContent = "🎤 " + msg;
    };
    recognition.onend = () => {
        setMicUI(false);
        if ($("autoCheck").checked && box.value.trim()) checkNews();
    };

    recognition.start();
    setMicUI(true);
}

// ---------- voice output (text -> speech) ----------
async function speak(text, langTag) {
    if (!text) return;
    const synth = window.speechSynthesis;
    if (synth) {
        synth.cancel();
        const voices = synth.getVoices();
        const want = langTag.toLowerCase();
        const voice =
            voices.find((v) => v.lang.toLowerCase().replace("_", "-") === want) ||
            voices.find((v) => v.lang.toLowerCase().startsWith(want.split("-")[0]));
        if (voice) {
            const u = new SpeechSynthesisUtterance(text);
            u.voice = voice;
            u.lang = voice.lang;
            synth.speak(u);
            return;
        }
    }
    // No installed voice for this language (common for Telugu on Windows):
    // fall back to the server (gTTS, needs internet).
    try {
        const r = await fetch("/tts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text, lang: langTag.split("-")[0] })
        });
        if (r.ok) new Audio(URL.createObjectURL(await r.blob())).play();
    } catch (err) {
        console.error(err);
    }
}

function speakLast() {
    if (lastSpoken) speak(lastSpoken.text, lastSpoken.lang);
}

// Chrome loads voices asynchronously; touching the list early warms it up.
if (window.speechSynthesis) window.speechSynthesis.getVoices();