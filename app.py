from flask import Flask, render_template, request, jsonify
import joblib
import re

app = Flask(__name__)

# Load trained model and vectorizer
model = joblib.load("model/fake_news_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    news = data.get("news", "")

    if not news.strip():
        return jsonify({
            "error": "Please enter some news text."
        }), 400

    cleaned_news = clean_text(news)

    # Convert text into TF-IDF features
    news_vector = vectorizer.transform([cleaned_news])

    # Prediction
    prediction = model.predict(news_vector)[0]

    # Probability / confidence
    probabilities = model.predict_proba(news_vector)[0]
    confidence = max(probabilities) * 100

    if prediction == 0:
        result = "FAKE NEWS"
    else:
        result = "REAL NEWS"

    return jsonify({
        "result": result,
        "confidence": round(confidence, 2)
    })


if __name__ == "__main__":
    app.run(debug=True)