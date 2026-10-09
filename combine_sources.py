import pandas as pd

a = pd.read_csv("dataset/external.csv")      # McIntire
b = pd.read_csv("dataset/third_test.csv")    # UTK
df = pd.concat([a, b], ignore_index=True)
df.to_csv("dataset/all_extra.csv", index=False)

print(len(a), "+", len(b), "=", len(df))
print(df["label"].value_counts().rename({0: "fake", 1: "real"}))