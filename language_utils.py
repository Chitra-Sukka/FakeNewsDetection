"""Language detection + translation-to-English for the multilingual pipeline.

Translation runs LOCALLY with Meta's NLLB-200 model (no internet, no rate limits).

Flow:  text -> detect_language() -> (if not English) to_english() -> English model

Detection is two-stage:
 1. Unicode script check (instant, very reliable for Telugu / Devanagari).
 2. `langdetect` for Latin-script text and for telling Hindi from Marathi/Nepali.
"""
import os
import re
import threading
from functools import lru_cache

LANG_NAMES = {
    "en": "English", "hi": "Hindi", "te": "Telugu", "ta": "Tamil", "kn": "Kannada",
    "ml": "Malayalam", "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati",
    "pa": "Punjabi", "ur": "Urdu", "ne": "Nepali",
}

# Browser speech-recognition / synthesis tags
SPEECH_LANG = {"en": "en-IN", "hi": "hi-IN", "te": "te-IN"}


class TranslationError(RuntimeError):
    pass


# Very common Hindi / Telugu words written in English letters ("Hinglish").
# Words that are also ordinary English (to, is, the, me, hi, do, main) are left out.
ROMANISED_INDIC = set("""
hai hain ki ka ke ko ne mein se par aur nahi nahin kya tha thi raha rahi rahe gaya gayi
kiya kiye diya liye lekin agar toh koi sab bahut yeh woh wo hum tum bhi ab kar karke
kaha kahaa bataya batayaa jankari sarkar mantri vibhag
undi ledu chesaru chepparu mariyu kuda oka ani aithe vachindi unnaru
""".split())
ROMAN_THRESHOLD = 0.12


def looks_like_romanised_indic(text: str) -> bool:
    tokens = re.findall(r"[a-z]+", text.lower())
    if len(tokens) < 8:
        return False
    return sum(t in ROMANISED_INDIC for t in tokens) / len(tokens) >= ROMAN_THRESHOLD


def _script_ratio(letters, lo, hi):
    return sum(1 for ch in letters if lo <= ord(ch) <= hi) / len(letters)


def detect_language(text: str) -> str:
    """Return an ISO code ('en', 'hi', 'te', ...) or 'unknown'."""
    letters = [ch for ch in text if ch.isalpha()]
    if len(letters) < 3:
        return "unknown"

    if _script_ratio(letters, 0x0C00, 0x0C7F) > 0.3:      # Telugu block
        return "te"

    if looks_like_romanised_indic(text):                   # Hindi/Telugu typed in English letters
        return "roman-indic"

    try:
        from langdetect import DetectorFactory, detect
        DetectorFactory.seed = 0                           # deterministic results
        code = detect(text)
    except Exception:
        code = None

    if _script_ratio(letters, 0x0900, 0x097F) > 0.3:      # Devanagari
        return code if code in ("hi", "mr", "ne") else "hi"

    if code:
        return code.split("-")[0]
    return "en"     # langdetect missing/failed on Latin text: assume English


# ---------------------------------------------------------------- translation
MODEL_NAME = os.environ.get("NLLB_MODEL", "facebook/nllb-200-distilled-600M")
MAX_SENTENCES = 80      # an article longer than this is truncated (keeps replies fast)
BATCH = 8

# ISO code (from detect_language) -> NLLB language code
NLLB_CODES = {
    "hi": "hin_Deva", "te": "tel_Telu", "ta": "tam_Taml", "kn": "kan_Knda",
    "ml": "mal_Mlym", "bn": "ben_Beng", "mr": "mar_Deva", "gu": "guj_Gujr",
    "pa": "pan_Guru", "ur": "urd_Arab", "ne": "npi_Deva",
    "fr": "fra_Latn", "es": "spa_Latn", "de": "deu_Latn", "pt": "por_Latn",
    "it": "ita_Latn", "ar": "arb_Arab", "ru": "rus_Cyrl", "zh": "zho_Hans",
    "tr": "tur_Latn",
}

_lock = threading.RLock()     # the model is shared, so one translation at a time
_state = {}


def _load():
    """Load the model once (about 10 s) and keep it in memory (GPU if available)."""
    with _lock:
        if "model" in _state:
            return
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tok = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device).eval()
        _state.update(tok=tok, model=model, device=device)


def warm_up():
    """Call at startup so the first user request isn't slow."""
    try:
        _load()
        _translate_sentences(["\u0928\u092e\u0938\u094d\u0924\u0947"], "hin_Deva")
        print(f"Translation model ready on {_state['device']}")
    except Exception as e:                        # app still starts; errors show on use
        print("Translation warm-up failed:", e)


_SENT_END = re.compile(r"(?<=[.?!\u0964])\s+|\n+")


def split_sentences(text: str, max_len: int = 400):
    """Sentence pieces short enough for the model."""
    out = []
    for s in (x.strip() for x in _SENT_END.split(text)):
        while len(s) > max_len:                   # very long sentence: cut at a space
            cut = s.rfind(" ", 0, max_len)
            cut = cut if cut > 0 else max_len
            out.append(s[:cut].strip())
            s = s[cut:].strip()
        if s:
            out.append(s)
    return out


def _translate_sentences(sentences, nllb_src):
    import torch
    tok, model, device = _state["tok"], _state["model"], _state["device"]
    tok.src_lang = nllb_src
    eng = tok.convert_tokens_to_ids("eng_Latn")
    order = sorted(range(len(sentences)), key=lambda i: len(sentences[i]))   # less padding
    out = [""] * len(sentences)
    for i in range(0, len(order), BATCH):
        idx = order[i:i + BATCH]
        enc = tok([sentences[j] for j in idx], return_tensors="pt", padding=True,
                  truncation=True, max_length=256).to(device)
        with torch.no_grad():
            gen = model.generate(**enc, forced_bos_token_id=eng,
                                 max_new_tokens=256, num_beams=4)
        for j, t in zip(idx, tok.batch_decode(gen, skip_special_tokens=True)):
            out[j] = t
    return out


@lru_cache(maxsize=128)
def _cached(text: str, nllb_src: str) -> str:
    try:
        with _lock:
            _load()
            sentences = split_sentences(text)[:MAX_SENTENCES]
            english = " ".join(_translate_sentences(sentences, nllb_src))
    except Exception as e:                         # model missing, GPU out of memory, ...
        raise TranslationError(str(e)) from e
    # The classifier learned "percent"; British output says "per cent".
    return re.sub(r"\bper cent\b", "percent", english, flags=re.I).strip()


def to_english(text: str, source: str) -> str:
    """Translate to English. Raises TranslationError on any failure."""
    if source == "en":
        return text
    if os.environ.get("DISABLE_TRANSLATION") == "1":
        raise TranslationError("translation disabled")
    code = NLLB_CODES.get(source)
    if code is None:
        raise TranslationError(f"language '{source}' is not supported yet")
    return _cached(text, code)