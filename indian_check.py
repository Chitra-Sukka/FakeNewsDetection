"""Run a folder of Indian news articles through the real app pipeline.

Put one article per .txt file (UTF-8) in:
    indian_test/real/   (genuine news from reputable outlets)
    indian_test/fake/   (viral claims that fact-checkers have debunked)
Then run:  python indian_check.py
"""
import glob
import os
from collections import defaultdict

import app as A
from language_utils import warm_up

warm_up()
client = A.app.test_client()

results = []            # (true_label, predicted_label, language)
skipped = 0
for label, folder in [(0, "fake"), (1, "real")]:
    for path in sorted(glob.glob(os.path.join("indian_test", folder, "*.txt"))):
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        r = client.post("/predict", json={"news": text})
        j = r.get_json()
        if r.status_code != 200:
            skipped += 1
            print(f"{folder:5} {name[:28]:28} SKIPPED: {j.get('error')}")
            continue
        if j["result"] == "UNCERTAIN":
            pred = None                      # the app refused to accuse either way
        else:
            pred = 1 if j["result"] == "REAL NEWS" else 0
        results.append((label, pred, j["detected_language"]))
        flag = "uncertain" if pred is None else ("ok" if pred == label else "WRONG")
        print(f"{folder:5} {name[:28]:28} {j['detected_language']:3} -> {j['result']:10} {j['confidence']:5.1f}%  {flag}")

if not results:
    raise SystemExit("\nNo articles found. Check the indian_test/real and indian_test/fake folders.")

decided = [r for r in results if r[1] is not None]
correct = sum(1 for t, p, _ in decided if t == p)
print("\n=== SUMMARY ===")
print(f"Articles tested: {len(results)}   (skipped: {skipped})")
print(f"Correct: {correct}   Wrong: {len(decided) - correct}   Uncertain: {len(results) - len(decided)}")
if decided:
    print(f"Accuracy on the articles the app dared to judge: {correct}/{len(decided)}")
print("Real news wrongly called FAKE :", sum(1 for t, p, _ in decided if t == 1 and p == 0))
print("Fake news wrongly called REAL :", sum(1 for t, p, _ in decided if t == 0 and p == 1))
by_lang = defaultdict(lambda: [0, 0, 0])
for t, p, lang in results:
    by_lang[lang][2] += 1
    if p is not None:
        by_lang[lang][1] += 1
        by_lang[lang][0] += int(t == p)
for lang, (ok, n, total) in sorted(by_lang.items()):
    print(f"  language {lang}: {ok}/{n} correct of those judged ({total} tested)")