# utils/scoring.py
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def clean_for_scoring(text: str) -> str:
    """
    Basic cleaning for scoring.
    Removes URLs and extra spaces.
    """
    text = re.sub(r"http\S+", "", text)  # Remove URLs
    text = re.sub(r"\s+", " ", text)     # Collapse whitespace
    return text.strip()

def score_sentences(candidate_sentences, top_n=50):
    """
    Score candidate sentences using TF-IDF and return top N.
    Input: list of dicts {page, line, sentence}
    Output: list of dicts {page, line, sentence}
    """
    # Convert to DataFrame
    df_sentences = pd.DataFrame(candidate_sentences)

    if df_sentences.empty:
        return []

    # Clean sentences
    df_sentences["cleaned_sentence"] = df_sentences["sentence"].apply(clean_for_scoring)

    # TF-IDF
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(df_sentences["cleaned_sentence"])

    # Score = sum of weights
    sentence_scores = tfidf_matrix.sum(axis=1)
    df_sentences["score"] = np.array(sentence_scores).flatten()

    # Select top N
    top_candidates = df_sentences.sort_values(by="score", ascending=False).head(top_n)

    # Return as list of dicts
    return top_candidates[["page", "line", "sentence"]].to_dict(orient="records")
