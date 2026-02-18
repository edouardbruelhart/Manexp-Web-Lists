"""Tests for core/mailer.py"""

from unittest.mock import MagicMock, patch

from manexp_web_lists.core.mailer import Mailer


def test_send_email_calls_smtp_ssl_correctly(monkeypatch):
    # Set environment variables for the test
    monkeypatch.setenv("EMAIL_SENDER", "sender@example.com")
    monkeypatch.setenv("SMTP", "smtp.example.com")
    monkeypatch.setenv("EMAIL_RECEIVER", "receiver@example.com")
    monkeypatch.setenv("PASSWORD", "password123")

    mailer = Mailer()

    # Patch SMTP_SSL
    with patch("manexp_web_lists.core.mailer.smtplib.SMTP_SSL") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Call the method
        mailer.send_email("Test Subject", "Test Body")

        # Assertions
        mock_smtp.assert_called_once_with("smtp.example.com", 465)
        mock_server.login.assert_called_once_with("sender@example.com", "password123")
        sent_msg = mock_server.send_message.call_args[0][0]  # get the EmailMessage sent
        assert sent_msg["From"] == "sender@example.com"
        assert sent_msg["To"] == "receiver@example.com"
        assert sent_msg["Subject"] == "Test Subject"
        assert sent_msg.get_content() == "Test Body\n"
