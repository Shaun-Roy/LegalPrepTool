import pandas as pd
import streamlit as st
from utils import pdf_processing, scoring, classification, postprocess, emailer
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
HUGGINGFACEHUB_API_TOKEN = os.getenv("SHAUN_TOKEN")
MYGMAIL = os.getenv("MYGMAIL")
GMAIL_APP_PW = os.getenv("GMAIL_APP_PW")

st.set_page_config(page_title="LegalPrepTool", layout="wide")
st.title("Legal Preparation Tool 🏛️")

# Step 1: Upload PDF
uploaded_file = st.file_uploader("Upload a legal PDF", type="pdf")
if uploaded_file:
    st.success("PDF uploaded successfully!")
    
    # Step 2: Extract sentences
    st.info("Extracting sentences...")
    candidate_sentences = pdf_processing.extract_sentences_from_pdf(uploaded_file)
    st.write(f"Extracted {len(candidate_sentences)} candidate sentences.")
    
    # Step 3: Score sentences
    st.info("Scoring sentences...")
    top_candidates = scoring.score_sentences(candidate_sentences, top_n=50)
    st.write(f"Top {len(top_candidates)} candidate sentences selected.")

    # Step 4: Classify sentences
    st.info("Classifying sentences...")
    df_classified = classification.classify_sentences(top_candidates, HUGGINGFACEHUB_API_TOKEN)
    st.write("Classification done. Sample:")
    st.dataframe(df_classified.head())
    
    # Step 5: Post-process to get balanced top arguments
    st.info("Selecting top FOR and AGAINST sentences...")
    top_10_df = postprocess.get_top_balanced_arguments(df_classified)
    st.dataframe(top_10_df)

    # Step 6: Summarize top arguments
    st.info("Summarizing top arguments...")
    if 'df_summaries' not in st.session_state:
        df_summaries = postprocess.summarize_top_sentences(top_10_df, HUGGINGFACEHUB_API_TOKEN)
        st.session_state.df_summaries = df_summaries
    else:
        df_summaries = st.session_state.df_summaries

    # Ensure summaries are full sentences
    df_summaries['summary'] = df_summaries['summary'].apply(lambda x: x if x.endswith('.') else x + '.')
    
    st.write("Summaries:")
    st.dataframe(df_summaries)

    # Step 7: Email functionality
    st.subheader("Share Summaries via Email")
    recipient_email = st.text_input("Enter recipient Gmail ID")
    if st.button("Share via Email") and recipient_email:
        try:
            st.info(f"Sending email to {recipient_email}...")
            emailer.send_email(recipient_email, df_summaries, MYGMAIL, GMAIL_APP_PW)
            st.success(f"Summaries sent successfully to {recipient_email}!")
        except Exception as e:
            st.error(f"Failed to send email: {e}")
