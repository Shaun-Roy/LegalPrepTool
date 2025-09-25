import pandas as pd
import re


def get_balanced_sentences(df_classified: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Select top N FOR and AGAINST sentences and clean them for further use.

    Args:
        df_classified (pd.DataFrame): DataFrame with columns ['sentence', 'page', 'line', 'label']
        top_n (int): Number of top sentences per label

    Returns:
        pd.DataFrame: Balanced DataFrame with top FOR and AGAINST sentences
    """
    if not {"sentence", "page", "line", "label"}.issubset(df_classified.columns):
        raise ValueError("DataFrame must contain ['sentence', 'page', 'line', 'label']")

    # Normalize label casing
    df_classified["label"] = df_classified["label"].str.upper()

    # Separate by label
    df_for = df_classified[df_classified["label"] == "FOR"].head(top_n).copy()
    df_against = df_classified[df_classified["label"] == "AGAINST"].head(top_n).copy()

    # Combine
    balanced_df = pd.concat([df_for, df_against], ignore_index=True)

    # Clean sentences
    def clean(text: str) -> str:
        text = re.sub(r"http\S+", "", text)      # Remove URLs
        text = re.sub(r"\s+", " ", text)         # Normalize spaces
        text = "".join(ch for ch in text if ch.isprintable())  # Drop weird chars
        return text.strip()

    balanced_df["sentence"] = balanced_df["sentence"].astype(str).apply(clean)

    return balanced_df

# Alias for compatibility
get_top_balanced_arguments = get_balanced_sentences

from transformers import pipeline

import pandas as pd
import requests

def summarize_top_sentences(top_10_df: pd.DataFrame, hf_token: str) -> pd.DataFrame:
    """
    Summarize sentences via HuggingFace Inference API (no local model download)
    """
    API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
    headers = {"Authorization": f"Bearer {hf_token}"}

    summaries = []

    for _, row in top_10_df.iterrows():
        payload = {"inputs": row['sentence'], "parameters": {"max_length": 60, "min_length": 15}}
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        summary_text = response.json()[0]['summary_text']

        summaries.append({
            "label": row['label'],
            "page": row['page'],
            "line": row['line'],
            "summary": f"{summary_text} (Page {row['page']}, Line {row['line']})"
        })

    return pd.DataFrame(summaries)

