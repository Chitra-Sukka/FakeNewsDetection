"""Train the English fake-news classifier (TF-IDF + Logistic Regression).

Usage
-----
    python train_model.py                       # unigrams, safest on RAM
    python train_model.py --ngram-max 2         # unigrams + bigrams (more RAM)
    python train_model.py --external dataset/external.csv   # test only (never trained on)
    python train_model.py --mix dataset/external.csv        # train on ISOT + 70% of it, test on the other 30%

Expects dataset/Fake.csv and dataset/True.csv (Kaggle: "Fake and Real News
Dataset" / ISOT). --external is an OPTIONAL CSV with columns `text,label`
(label 0 = fake, 1 = real) from a different source; its score is the honest
estimate of how the model behaves outside the ISOT dataset.
"""
import argparse
import json
import os
import sys
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import GridSearchCV, train_test_split

from preprocess import prepare_text

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "dataset")
MODEL_DIR = os.path.join(BASE, "model")


def load_isot() -> pd.DataFrame:
    fake_p = os.path.join(DATA_DIR, "Fake.csv")
    true_p = os.path.join(DATA_DIR, "True.csv")
    if not (os.path.exists(fake_p) and os.path.exists(true_p)):
        sys.exit(
            "Dataset not found. Put Fake.csv and True.csv inside the 'dataset/' "
            "folder (Kaggle: 'Fake and Real News Dataset')."
        )
    fake, true = pd.read_csv(fake_p), pd.read_csv(true_p)
    fake["label"], true["label"] = 0, 1
    df = pd.concat([fake, true], ignore_index=True)
    df["raw"] = df["title"].fillna("").astype(str) + " " + df["text"].fillna("").astype(str)
    print(f"Loaded: fake={len(fake)}, real={len(true)}")
    return df[["raw", "label"]]


def load_external(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df["label"].dtype == object:
        df["label"] = df["label"].str.lower().map(
            {"fake": 0, "false": 0, "real": 1, "true": 1}
        )
    df = df.dropna(subset=["text", "label"])
    df["label"] = df["label"].astype(int)
    return df[["text", "label"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ngram-max", type=int, default=1, choices=[1, 2])
    ap.add_argument("--max-features", type=int, default=100_000)
    ap.add_argument("--external", default=None,
                    help="CSV used ONLY for testing")
    ap.add_argument("--mix", default=None,
                    help="CSV whose 70%% joins the training data; the other 30%% is a separate test")
    ap.add_argument("--ext-weight", type=float, default=3.0,
                    help="how much more each --mix article counts in training (default 3)")
    args = ap.parse_args()

    t0 = time.time()
    df = load_isot()

    print("Cleaning text (this takes a minute)...")
    df["content"] = df["raw"].map(prepare_text)
    df = df[df["content"].str.split().str.len() >= 10]

    # ISOT contains many duplicated articles; if a copy lands in the test set
    # the score is inflated. Remove them BEFORE splitting.
    before = len(df)
    df = df.drop_duplicates(subset="content").reset_index(drop=True)
    print(f"Removed {before - len(df)} duplicate/near-empty rows -> {len(df)} left")

    X_train, X_test, y_train, y_test = train_test_split(
        df["content"], df["label"], test_size=0.20, random_state=42, stratify=df["label"]
    )
    X_train, y_train = X_train.reset_index(drop=True), y_train.reset_index(drop=True)
    n_isot_train = len(X_train)
    print(f"Train={len(X_train)}  Test={len(X_test)}")

    mix_test = None
    if args.mix:
        mx = load_external(args.mix)
        mx["content"] = mx["text"].map(prepare_text)
        mx = mx[mx["content"].str.split().str.len() >= 10]
        mx = mx.drop_duplicates(subset="content").reset_index(drop=True)
        mx_tr, mx_te = train_test_split(
            mx, test_size=0.30, random_state=42, stratify=mx["label"]
        )
        X_train = pd.concat([X_train, mx_tr["content"]], ignore_index=True)
        y_train = pd.concat([y_train, mx_tr["label"]], ignore_index=True)
        mix_test = mx_te
        print(f"Mixed in {len(mx_tr)} articles from {args.mix} "
              f"(each counts x{args.ext_weight}); kept {len(mx_te)} for a separate test")
    weights = np.where(np.arange(len(X_train)) < n_isot_train, 1.0, args.ext_weight)

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, args.ngram_max),
        min_df=3,
        max_df=0.7,
        max_features=args.max_features,
        sublinear_tf=True,
        dtype=np.float32,
    )
    Xtr = vectorizer.fit_transform(X_train)
    Xte = vectorizer.transform(X_test)
    print(f"TF-IDF matrix: {Xtr.shape}")

    print("Tuning C with 3-fold cross-validation...")
    grid = GridSearchCV(
        LogisticRegression(solver="liblinear", max_iter=1000),
        {"C": [1, 4, 10]},
        cv=3,
        scoring="f1",
        n_jobs=1,
    )
    grid.fit(Xtr, y_train, sample_weight=weights)
    model = grid.best_estimator_
    print("Best C:", grid.best_params_["C"])

    pred = model.predict(Xte)
    acc = accuracy_score(y_test, pred)
    print("\n=== HELD-OUT TEST (same distribution as training) ===")
    print("Accuracy:", round(acc, 4))
    print(classification_report(y_test, pred, target_names=["Fake", "Real"]))
    print("Confusion matrix:\n", confusion_matrix(y_test, pred))

    metrics = {
        "accuracy": float(acc),
        "f1": float(f1_score(y_test, pred)),
        "best_C": grid.best_params_["C"],
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "ngram_max": args.ngram_max,
    }

    if mix_test is not None:
        pm = model.predict(vectorizer.transform(mix_test["content"]))
        metrics["mix_test_accuracy"] = float(accuracy_score(mix_test["label"], pm))
        print("\n=== HELD-OUT 30% OF THE MIXED-IN DATASET ===")
        print("Accuracy:", round(metrics["mix_test_accuracy"], 4))
        print(classification_report(mix_test["label"], pm, target_names=["Fake", "Real"]))
        print("Confusion matrix:\n", confusion_matrix(mix_test["label"], pm))

    if args.external:
        ext = load_external(args.external)
        pe = model.predict(vectorizer.transform(ext["text"].map(prepare_text)))
        metrics["external_accuracy"] = float(accuracy_score(ext["label"], pe))
        print("\n=== EXTERNAL DATASET (the honest number) ===")
        print("Accuracy:", round(metrics["external_accuracy"], 4))
        print("Confusion matrix:\n", confusion_matrix(ext["label"], pe))

    # Sanity check: the strongest words should be about style/content, NOT
    # publisher names ("reuters") or datelines.
    names = np.array(vectorizer.get_feature_names_out())
    order = np.argsort(model.coef_[0])
    top_fake, top_real = list(names[order[:25]]), list(names[order[-25:]][::-1])
    print("\nTop FAKE words:", top_fake)
    print("Top REAL words:", top_real)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODEL_DIR, "fake_news_model.pkl"))
    joblib.dump(vectorizer, os.path.join(MODEL_DIR, "vectorizer.pkl"))
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump({**metrics, "top_fake": top_fake, "top_real": top_real}, f, indent=2)
    print(f"\nSaved to model/  (total time {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()