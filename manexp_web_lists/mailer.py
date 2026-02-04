import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv


class Mailer:
    """Simple mailer class to send emails using SMTP."""

    load_dotenv()

    def send_email(self, subject: str, body: str) -> None:
        # Get environment variables
        email_sender = str(os.getenv("EMAIL_SENDER"))
        smtp = str(os.getenv("SMTP"))
        email_receiver = str(os.getenv("EMAIL_RECEIVER"))
        password = str(os.getenv("PASSWORD"))

        msg = EmailMessage()
        msg["From"] = email_sender
        msg["To"] = email_receiver
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL(smtp, 465) as server:
            server.login(email_sender, password)
            server.send_message(msg)
