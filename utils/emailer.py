from transformers import pipeline
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

sender_email = os.getenv("MYGMAIL") 
app_password = os.getenv("GMAIL_APP_PW")

def send_email(recipient_email, df_summaries, sender_email, app_password):
    """
    df_summaries: DataFrame with ['label', 'page', 'line', 'summary']
    """
    # Compile email body
    email_body = ""
    for _, row in df_summaries.iterrows():
        email_body += f"Label: {row['label']}\nPage: {row['page']}, Line: {row['line']}\nSummary: {row['summary']}\n\n"

    # Set up email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = 'Summarized Legal Arguments'
    msg.attach(MIMEText(email_body, 'plain'))

    # Send via Gmail SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.send_message(msg)
    server.quit()
