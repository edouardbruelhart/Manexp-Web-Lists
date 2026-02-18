"""Tests for run.py"""

from unittest.mock import patch

from manexp_web_lists.run import run


# Just to make codecov happy
def test_run_calls_fetches_and_mailer():
    with (
        patch("manexp_web_lists.run.fetch_taxa") as mock_taxa,
        patch("manexp_web_lists.run.fetch_pesticides") as mock_pest,
        patch("manexp_web_lists.run.mailer.send_email") as mock_mail,
        patch("manexp_web_lists.run.configure_logging") as mock_log,
        patch("manexp_web_lists.run.log_section") as mock_section,
    ):

        class DummyLog:
            def getvalue(self):
                return "log content"

        mock_log.return_value = DummyLog()

        # Run
        run()

        # Assertions
        mock_taxa.assert_called_once()
        mock_pest.assert_called_once()
        mock_mail.assert_called_once_with(subject="Manexp-Web-List SUCCESS Report", body="log content")
        mock_section.assert_any_call("TEST_SECTION")
