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

    language = data.get("language", "english")
    print("Selected Language:", language)
    
    if not news.strip():
        return jsonify({
            "error": "Please enter some news text."
        }), 400

    cleaned_news = clean_text(news)

    # Convert text into TF-IDF features
    news_vector = vectorizer.transform([cleaned_news])

    # Prediction
    prediction = model.predict(news_vector)[0]

    # Explainable AI
    feature_names = vectorizer.get_feature_names_out()
    coefficients = model.coef_[0]

    word_scores = news_vector.toarray()[0] * coefficients

    important_words = []

    for i, score in enumerate(word_scores):
        if score != 0:
            important_words.append((feature_names[i], score))

    important_words = sorted(
        important_words,
        key=lambda x: abs(x[1]),
        reverse=True
    )[:10]

    # Separate important words
    fake_words = []
    real_words = []

    for word, score in important_words:
        if score < 0:
            fake_words.append(word)
        else:
            real_words.append(word)

    # Probability / confidence
    probabilities = model.predict_proba(news_vector)[0]
    confidence = max(probabilities) * 100

    if prediction == 0:
        result = "FAKE NEWS"
    else:
        result = "REAL NEWS"

    return jsonify({
        "result": result,
        "confidence": round(confidence, 2),
        "fake_words": fake_words,
        "real_words": real_words
    })


if __name__ == "__main__":
    app.run(debug=True)