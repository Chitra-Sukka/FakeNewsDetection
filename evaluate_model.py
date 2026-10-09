import sys
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from preprocess import prepare_text

model = joblib.load("model/fake_news_model.pkl")
vec = joblib.load("model/vectorizer.pkl")
df = pd.read_csv(sys.argv[1])          # needs columns: text, label (0 = fake, 1 = real)

pred = model.predict(vec.transform(df["text"].map(prepare_text)))

print("Articles:", len(df))
print("Accuracy:", round((pred == df["label"]).mean(), 4))
print("Confusion matrix (rows = actual fake/real, columns = predicted fake/real):")
print(confusion_matrix(df["label"], pred))
print(classification_report(df["label"], pred, target_names=["Fake", "Real"]))
print("Share predicted REAL:", round(pred.mean(), 3))