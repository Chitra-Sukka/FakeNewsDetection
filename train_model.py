import pandas as pd
import re
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# =========================
# 1. Load Dataset
# =========================

fake_path = "dataset/Fake.csv"
true_path = "dataset/True.csv"

fake = pd.read_csv(fake_path)
true = pd.read_csv(true_path)

print("Fake News Dataset:", fake.shape)
print("Real News Dataset:", true.shape)


# =========================
# 2. Add Labels
# =========================

fake["label"] = 0
true["label"] = 1


# =========================
# 3. Combine Datasets
# =========================

data = pd.concat([fake, true], ignore_index=True)

print("Combined Dataset:", data.shape)


# =========================
# 4. Create Full Text
# =========================

data["title"] = data["title"].fillna("")
data["text"] = data["text"].fillna("")

data["content"] = data["title"] + " " + data["text"]


# =========================
# 5. Clean Text
# =========================

def clean_text(text):
    text = str(text)
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


data["content"] = data["content"].apply(clean_text)


# =========================
# 6. Remove Empty Rows
# =========================

data = data[data["content"].str.len() > 0]


# =========================
# 7. Features and Labels
# =========================

X = data["content"]
y = data["label"]


# =========================
# 8. Train/Test Split
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# =========================
# 9. TF-IDF
# =========================

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_df=0.7,
    max_features=50000
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print("TF-IDF conversion completed.")


# =========================
# 10. Train Model
# =========================

model = LogisticRegression(
    max_iter=1000
)

model.fit(X_train_tfidf, y_train)

print("Model training completed.")


# =========================
# 11. Prediction
# =========================

y_pred = model.predict(X_test_tfidf)


# =========================
# 12. Evaluation
# =========================

accuracy = accuracy_score(y_test, y_pred)

print("\n==============================")
print("MODEL PERFORMANCE")
print("==============================")

print("Accuracy:", accuracy)

print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    target_names=["Fake", "Real"]
))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))


# =========================
# 13. Create Model Folder
# =========================

os.makedirs("model", exist_ok=True)


# =========================
# 14. Save Model
# =========================

joblib.dump(model, "model/fake_news_model.pkl")
joblib.dump(vectorizer, "model/vectorizer.pkl")

print("\n==============================")
print("MODEL SAVED SUCCESSFULLY")
print("==============================")

print("model/fake_news_model.pkl")
print("model/vectorizer.pkl")