# 📰 AI-Based Explainable Multilingual Fake News Detection System

An AI-based web application that detects whether a given news article is likely to be **Fake or Real** using Machine Learning and Natural Language Processing (NLP).

## 🎯 Objective

The main objective of this project is to help users identify potentially fake news by analyzing the text of a news article and providing a prediction with a confidence score.

## ✨ Features

- 📰 Fake News Detection
- 🤖 Machine Learning based prediction
- 📊 Confidence Score
- 🌐 Web-based interface
- ⚡ Real-time prediction using Flask
- 🔍 Text preprocessing using NLP
- 🌍 Multilingual: auto language detection (English / Hindi / Telugu) + translation to English
- 🎤🔊 Voice assistant: speak the news, hear the verdict (Chrome / Edge)

## 🛠️ Technologies Used

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- Flask

### Machine Learning / NLP
- Pandas
- NumPy
- Scikit-learn
- NLTK
- TF-IDF
- Logistic Regression

## 🧠 Machine Learning Model

The current version uses:

**TF-IDF Vectorization + Logistic Regression**

The dataset contains:

- 23,481 Fake news articles
- 21,417 Real news articles
- Total: 44,898 articles

The model achieved approximately **98.76% accuracy** on the held-out test set.

## 📁 Project Structure

```text
Fake-News-Detection/
│
├── app.py
├── train_model.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── model/
│   ├── fake_news_model.pkl
│   └── vectorizer.pkl
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js

## ▶️ How to run

```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
# put Fake.csv and True.csv in dataset/
python train_model.py            # trains and writes model/*.pkl
python app.py                    # open http://127.0.0.1:5000
```
