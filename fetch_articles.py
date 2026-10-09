"""Download news articles listed in sources.csv and save them as test files.

sources.csv needs three columns (with a header line):
    url,label,name
    https://example.com/some-article,real,real_hindu_01

 - label is "real" or "fake"
 - name becomes the file name: indian_test/<label>/<name>.txt

For PRIVATE testing only. Respect each site's terms; if a page is paywalled or
blocks the download, the script says so and you copy that article by hand.
Do NOT list fact-check pages as "fake": they contain the debunking, which would
give the model the answer. Copy the viral claim itself into a .txt file instead.
"""
import csv
import os
import sys

MIN_WORDS = 40


def get_text(url: str) -> str:
    import trafilatura                       # pip install trafilatura
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return ""
    return trafilatura.extract(downloaded, include_comments=False, include_tables=False) or ""


def main(csv_path: str = "sources.csv") -> None:
    if not os.path.exists(csv_path):
        sys.exit(f"{csv_path} not found. Create it with the header: url,label,name")
    ok = failed = 0
    with open(csv_path, newline="", encoding="utf-8-sig") as f:   # utf-8-sig drops the invisible BOM that Notepad/Excel add
        for row in csv.DictReader(f):
            url = (row.get("url") or "").strip()
            label = (row.get("label") or "").strip().lower()
            name = (row.get("name") or "").strip()
            if not url or label not in ("real", "fake") or not name:
                print("SKIPPED (bad row):", row)
                failed += 1
                continue
            try:
                text = get_text(url)
            except Exception as e:           # network error, blocked, library missing
                text = ""
                print(f"{name}: error - {e}")
            words = len(text.split())
            if words < MIN_WORDS:
                print(f"{name}: FAILED ({words} words found). Copy this one by hand: {url}")
                failed += 1
                continue
            folder = os.path.join("indian_test", label)
            os.makedirs(folder, exist_ok=True)
            with open(os.path.join(folder, name + ".txt"), "w", encoding="utf-8") as out:
                out.write(text.strip() + "\n")
            print(f"{name}: saved ({words} words) -> indian_test/{label}/{name}.txt")
            ok += 1
    print(f"\nDone. Saved {ok}, failed {failed}.")


if __name__ == "__main__":
    main(*sys.argv[1:2])