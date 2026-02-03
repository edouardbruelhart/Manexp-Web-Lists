from manexp_web_lists.mail import Mailer

mailer = Mailer()

mailer.send_email(subject="Test Email", body="This is a test email sent from the MailClient.")
