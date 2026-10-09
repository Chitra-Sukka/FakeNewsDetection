import joblib
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
from preprocess import prepare_text

model = joblib.load("model/fake_news_model.pkl")
vec = joblib.load("model/vectorizer.pkl")
df = pd.read_csv("dataset/external.csv")

pred = model.predict(vec.transform(df["text"].map(prepare_text)))

print(confusion_matrix(df["label"], pred))
print(classification_report(df["label"], pred, target_names=["Fake", "Real"]))
print("Share of articles predicted REAL:", round(pred.mean(), 3))