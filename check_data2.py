import pandas as pd

fake = pd.read_csv("dataset/Fake.csv")
true = pd.read_csv("dataset/True.csv")

for name, df in [("fake", fake), ("real", true)]:
    t = df["text"].fillna("")
    has_apos = t.str.contains("['’]").mean()
    has_split = t.str.contains(r"\b\w+n t\b").mean()
    print(name, "| contains an apostrophe:", round(has_apos, 3),
            "| contains 'couldn t'-style split:", round(has_split, 3))