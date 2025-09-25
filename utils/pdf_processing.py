
import pdfplumber
import re
import nltk
from nltk.tokenize import sent_tokenize

# Ensure punkt is available
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

def extract_paragraphs(pdf_path):
    """
    Extract paragraphs from a PDF using pdfplumber.
    Returns a list of dicts: [{"page": int, "text": str}]
    """
    paragraphs = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                # Strip empty lines and merge into paragraph
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                paragraph_text = " ".join(lines)
                paragraphs.append({
                    "page": page_num,
                    "text": paragraph_text
                })
    return paragraphs


def paragraphs_to_sentences(paragraphs):
    """
    Convert paragraphs into tokenized sentences.
    Returns a list of dicts: [{"page": int, "line": int, "sentence": str}]
    """
    candidate_sentences = []
    for para in paragraphs:
        sentences = sent_tokenize(para["text"])
        for idx, sent in enumerate(sentences, 1):
            cleaned_sent = sent.strip()
            if cleaned_sent:
                candidate_sentences.append({
                    "page": para["page"],
                    "line": idx,
                    "sentence": cleaned_sent
                })
    return candidate_sentences


def extract_sentences_from_pdf(pdf_path):
    """
    Main helper: extract sentences directly from PDF.
    This is the function your main.py and app.py will call.
    """
    paragraphs = extract_paragraphs(pdf_path)
    return paragraphs_to_sentences(paragraphs)
