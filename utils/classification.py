# utils/classification.py
from transformers import pipeline
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def classify_sentences(candidate_data, hf_token=None):
    """
    Classify candidate sentences as FOR or AGAINST using zero-shot classification.

    Args:
        candidate_data (list of dict): Each item should have keys 'sentence', 'page', 'line'.
        hf_token (str, optional): Hugging Face API token. If None, pulled from .env.

    Returns:
        pd.DataFrame: DataFrame with sentence, page, line, and predicted label.
    """
    if hf_token is None:
        hf_token = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("SHAUN_TOKEN")

    if not hf_token:
        raise ValueError("Hugging Face API token not provided. Set HUGGINGFACE_TOKEN in .env")

    # Load zero-shot classifier
    classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        token=hf_token
    )

    candidate_labels = ["FOR", "AGAINST"]
    classified_candidates = []

    for item in candidate_data:
        result = classifier(item['sentence'], candidate_labels=candidate_labels)
        # Pick label with highest score
        label = result['labels'][0]

        classified_candidates.append({
            "sentence": item['sentence'],
            "page": item['page'],
            "line": item['line'],
            "label": label
        })

    return pd.DataFrame(classified_candidates)
