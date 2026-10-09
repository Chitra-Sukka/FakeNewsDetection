import io
import os

import joblib
import numpy as np
from flask import Flask, jsonify, render_template, request, send_file

from language_utils import (LANG_NAMES, SPEECH_LANG, TranslationError,
                            detect_language, to_english, warm_up)
from preprocess import prepare_text

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE, "model", "fake_news_model.pkl")
VEC_PATH = os.path.join(BASE, "model", "vectorizer.pkl")

if not (os.path.exists(MODEL_PATH) and os.path.exists(VEC_PATH)):
    raise SystemExit("No trained model found. Run:  python train_model.py")

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VEC_PATH)
feature_names = np.array(vectorizer.get_feature_names_out())

app = Flask(__name__)

MAX_CHARS = 20_000
MIN_WORDS = 15          # below this the TF-IDF vector is too thin to trust
UNCERTAIN_BELOW = 65.0   # below this confidence we do not accuse either way

# Spoken verdicts (voice assistant). Other languages fall back to English.
SPOKEN = {
    "en": {"fake": "This news is likely fake. Confidence {c} percent.",
           "real": "This news is likely real. Confidence {c} percent.",
           "uncertain": "I am not sure about this news. Please check other sources."},
    "hi": {"fake": "यह खबर फर्जी होने की संभावना है। विश्वास स्तर {c} प्रतिशत।",
           "real": "यह खबर असली होने की संभावना है। विश्वास स्तर {c} प्रतिशत।",
           "uncertain": "इस खबर के बारे में निश्चित रूप से कहना मुश्किल है। कृपया दूसरे स्रोतों से जांच करें।"},
    "te": {"fake": "ఈ వార్త నకిలీ అయ్యే అవకాశం ఉంది. నమ్మకం {c} శాతం.",
           "real": "ఈ వార్త నిజమయ్యే అవకాశం ఉంది. నమ్మకం {c} శాతం.",
           "uncertain": "ఈ వార్త గురించి ఖచ్చితంగా చెప్పడం కష్టం. దయచేసి ఇతర వనరులను తనిఖీ చేయండి."},
}


def explain(vec, top_n=10):
    """Words that pushed the prediction hardest (works on the sparse row)."""
    row = vec.tocoo()
    contrib = row.data * model.coef_[0][row.col]
    order = np.argsort(-np.abs(contrib))[:top_n]
    fake, real = [], []
    for i in order:
        word = str(feature_names[row.col[i]])
        (fake if contrib[i] < 0 else real).append(word)
    return fake, real


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    news = str(data.get("news", "")).strip()
    chosen = str(data.get("language", "auto")).lower()

    if not news:
        return jsonify({"error": "Please enter some news text."}), 400
    news = news[:MAX_CHARS]

    # 1. Detect language (a manual choice is only used if detection fails)
    detected = detect_language(news)
    legacy = {"english": "en", "hindi": "hi", "telugu": "te"}
    chosen = legacy.get(chosen, chosen)
    lang = detected if detected != "unknown" else (chosen if chosen in LANG_NAMES else "en")

    if detected == "roman-indic":
        return jsonify({"error": "This looks like Hindi or Telugu typed in English letters, "
                                 "which I cannot read reliably. Please use Hindi (Devanagari) "
                                 "or Telugu script, or English. For the microphone, choose "
                                 "'Speak: Hindi' or 'Speak: Telugu'."}), 422

    # 2. Translate to English if needed (the model only knows English)
    translated = None
    english_text = news
    if lang != "en":
        try:
            english_text = to_english(news, lang)
            translated = english_text
        except TranslationError as e:
            app.logger.warning("translation failed: %s", e)
            return jsonify({"error": "Could not translate this text. The language "
                                     "may not be supported yet - please try again."}), 503

    # 3. Clean + guard against empty / too-short input
    cleaned = prepare_text(english_text)
    if len(cleaned.split()) < MIN_WORDS:
        return jsonify({"error": "Text is too short to analyse. Please paste a "
                                 "full paragraph or article."}), 422

    vec = vectorizer.transform([cleaned])
    if vec.nnz == 0:
        return jsonify({"error": "No recognisable words found in this text."}), 422

    # 4. Predict (classes_ == [0 fake, 1 real])
    proba = model.predict_proba(vec)[0]
    is_real = bool(proba[1] >= 0.5)
    confidence = round(float(max(proba)) * 100, 2)
    fake_words, real_words = explain(vec)

    leaning = "REAL NEWS" if is_real else "FAKE NEWS"
    uncertain = confidence < UNCERTAIN_BELOW
    verdict = "UNCERTAIN" if uncertain else leaning
    spoken_lang = lang if lang in SPOKEN else "en"
    key = "uncertain" if uncertain else ("real" if is_real else "fake")
    spoken = SPOKEN[spoken_lang][key].format(c=int(round(confidence)))

    return jsonify({
        "result": verdict,
        "confidence": confidence,
        "low_confidence": uncertain,
        "leaning": leaning,
        "fake_words": fake_words,
        "real_words": real_words,
        "detected_language": lang,
        "language_name": LANG_NAMES.get(lang, lang),
        "translated_text": translated[:1500] if translated else None,
        "spoken": spoken,
        "speech_lang": SPEECH_LANG.get(spoken_lang, "en-IN"),
    })


@app.route("/tts", methods=["POST"])
def tts():
    """Fallback speech for browsers/OSes with no Telugu or Hindi voice installed."""
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", ""))[:500]
    lang = str(data.get("lang", "en"))
    if not text or lang not in SPOKEN:
        return jsonify({"error": "Invalid request."}), 400
    try:
        from gtts import gTTS
        buf = io.BytesIO()
        gTTS(text=text, lang=lang).write_to_fp(buf)
        buf.seek(0)
        return send_file(buf, mimetype="audio/mpeg")
    except Exception as e:
        app.logger.warning("tts failed: %s", e)
        return jsonify({"error": "Speech service unavailable."}), 503


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    # In debug mode Flask starts two processes; load the translator only in the real one
    if not debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        warm_up()
    app.run(debug=debug)