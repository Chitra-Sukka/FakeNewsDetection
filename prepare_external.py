import sys
import pandas as pd

df = pd.read_csv(sys.argv[1])
print("Columns:", list(df.columns))

df["label"] = df["label"].astype(str).str.strip().str.lower().map({"fake": 0, "real": 1})
df["text"] = (df["title"].fillna("") + " " + df["text"].fillna("")).str.strip()
df = df.dropna(subset=["label"])
df = df[df["text"].str.split().str.len() >= 10].drop_duplicates(subset="text")

df[["text", "label"]].astype({"label": int}).to_csv("dataset/external.csv", index=False)
print(df["label"].value_counts().rename({0: "fake", 1: "real"}))