import os
from utils.pdf_processing import extract_sentences_from_pdf
from utils.scoring import score_sentences
from utils.classification import classify_sentences
from utils.postprocess import get_top_balanced_sentences
from utils.emailer import summarize_top_sentences, send_email

def main():
    # --------------------------
    # 1. Input PDF
    # --------------------------
    pdf_path = input("Enter path to PDF file: ")
    if not os.path.exists(pdf_path):
        print("PDF file not found!")
        return

    # --------------------------
    # 2. Extract sentences from PDF
    # --------------------------
    candidate_sentences = extract_sentences_from_pdf(pdf_path)
    print(f"Extracted {len(candidate_sentences)} candidate sentences.")

    # --------------------------
    # 3. Score sentences (TF-IDF)
    # --------------------------
    top_candidates = score_sentences(candidate_sentences, top_n=50)
    print(f"Selected top {len(top_candidates)} candidates based on score.")

    # --------------------------
    # 4. Classify sentences as FOR/AGAINST
    # --------------------------
    hf_token = os.getenv("SHAUN_TOKEN")  # secure token
    classified_df = classify_sentences(top_candidates, hf_token)
    print("Classification complete.")

    # --------------------------
    # 5. Postprocess: select top balanced FOR/AGAINST
    # --------------------------
    top_10_df = get_top_balanced_sentences(classified_df, top_n_each=5)
    print("Selected balanced top FOR/AGAINST sentences.")

    # --------------------------
    # 6. Summarize top sentences
    # --------------------------
    summaries_df = summarize_top_sentences(top_10_df, hf_token)
    print("Summarization complete.")

    # --------------------------
    # 7. Optional: send summaries via email
    # --------------------------
    send_email_flag = input("Do you want to send the summaries via Gmail? (y/n): ").strip().lower()
    if send_email_flag == 'y':
        recipient = input("Enter recipient Gmail ID: ")
        sender_email = os.getenv("MYGMAIL")
        app_password = os.getenv("GMAIL_APP_PW")
        send_email(recipient, summaries_df, sender_email, app_password)

    print("Pipeline completed successfully!")


if __name__ == "__main__":
    main()
