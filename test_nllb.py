import time
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL = "facebook/nllb-200-distilled-600M"
device = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading model (the first run downloads about 2.4 GB)...")
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL).to(device)
model.eval()

samples = {
    "hin_Deva": "वित्त मंत्री ने गुरुवार को पत्रकारों से कहा कि सरकार ग्रामीण सड़कों के बजट में 8 प्रतिशत की वृद्धि करेगी।",
    "tel_Telu": "ఆర్థిక మంత్రి గురువారం విలేకరులతో మాట్లాడుతూ, గ్రామీణ రహదారుల బడ్జెట్‌ను ప్రభుత్వం 8 శాతం పెంచనుందని చెప్పారు.",
}

for code, text in samples.items():
    tok.src_lang = code                      # tells the model which language the input is
    inputs = tok(text, return_tensors="pt").to(device)
    start = time.time()
    with torch.no_grad():
        out = model.generate(
            **inputs,
            forced_bos_token_id=tok.convert_tokens_to_ids("eng_Latn"),   # output language: English
            max_new_tokens=200,
            num_beams=4,                     # tries 4 candidate translations, keeps the best
        )
    print(code, "->", tok.batch_decode(out, skip_special_tokens=True)[0], f"({time.time() - start:.1f}s)")