import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

from manexp_web_lists.exceptions import InvalidEnvironmentError


class Mailer:
    """Client to send emails using SMTP."""

    load_dotenv()

    def send_email(self, subject: str, body: str) -> None:
        """
        Docstring pour send_email

        Args:
            subject: The subject of the email
            body: The body of the email

        Raises:
            InvalidEnvironmentError: Raised when environment variables are invalid or incomplete
        """

        # Get environment variables
        email_sender = os.getenv("EMAIL_SENDER")
        smtp = os.getenv("SMTP")
        email_receiver = os.getenv("EMAIL_RECEIVER")
        password = os.getenv("PASSWORD")

        # Check that variables are not null
        if email_sender is None or smtp is None or email_receiver is None or password is None:
            raise InvalidEnvironmentError

        msg = EmailMessage()
        msg["From"] = email_sender
        msg["To"] = email_receiver
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL(smtp, 465) as server:
            server.login(email_sender, password)
            server.send_message(msg)
