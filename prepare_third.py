import pandas as pd

df = pd.read_csv("dataset/utk_train.csv", sep=";")
df = df.dropna(subset=["text", "label"])
df["label"] = df["label"].astype(int)   # in this copy 0 = fake, 1 = real, same as ours: NO flipping
df = df[df["text"].str.split().str.len() >= 30].drop_duplicates(subset="text")

# Label sanity check: New York Times articles should sit almost entirely under label 1
nyt = df["text"].str.contains("new york time", regex=False)
print("Articles mentioning 'new york time' -> label 0:", round(nyt[df["label"] == 0].mean(), 3),
        "| label 1:", round(nyt[df["label"] == 1].mean(), 3))

df[["text", "label"]].to_csv("dataset/third_test.csv", index=False)
print("Rows:", len(df))
print(df["label"].value_counts().rename({0: "fake", 1: "real"}))