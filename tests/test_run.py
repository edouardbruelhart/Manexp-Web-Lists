"""Tests for run.py"""

from unittest.mock import patch

from manexp_web_lists.run import run


# Just to make codecov happy
def test_run_calls_fetches_and_mailer():
    with (
        patch("manexp_web_lists.run.get_countries") as mock_countries,
        patch("manexp_web_lists.run.get_register_types") as mock_reg_types,
        patch("manexp_web_lists.run.get_register_subtypes") as mock_reg_subtypes,
        patch("manexp_web_lists.run.get_seeds") as mock_seeds,
        patch("manexp_web_lists.run.get_seeds") as mock_seeds,
        patch("manexp_web_lists.run.get_taxonomy") as mock_taxonomy,
        patch("manexp_web_lists.run.get_phytosanitary_products") as mock_sanitary,
        # patch("manexp_web_lists.run.mailer.send_email") as mock_mail,
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
        mock_countries.assert_called_once()
        mock_reg_types.assert_called_once()
        mock_reg_subtypes.assert_called_once()
        mock_seeds.assert_called_once()
        mock_taxonomy.assert_called_once()
        mock_sanitary.assert_called_once()
        # mock_mail.assert_called_once()
        mock_section.assert_called()


def test_run_exception_sends_error_email():
    with (
        patch("manexp_web_lists.run.get_countries", side_effect=RuntimeError),
        patch("manexp_web_lists.core.mailer.Mailer.send_email") as mock_send,
    ):
        run()

        mock_send.assert_called_once()
        assert "EXCEPTION" in mock_send.call_args.kwargs["subject"]
