import pandas as pd

fake = pd.read_csv("dataset/Fake.csv")
true = pd.read_csv("dataset/True.csv")

print("Fake:", fake.shape, "| Real:", true.shape)
print("Columns:", list(fake.columns))

share_true = true["text"].str.contains(r"\(Reuters\)", regex=True).mean()
share_fake = fake["text"].str.contains(r"\(Reuters\)", regex=True).mean()
print("Real articles containing '(Reuters)':", round(share_true, 3))
print("Fake articles containing '(Reuters)':", round(share_fake, 3))

print("Duplicate texts -> fake:", fake["text"].duplicated().sum(),
        "| real:", true["text"].duplicated().sum())

print("\nSample fake article:\n", fake["text"].iloc[0][:300])