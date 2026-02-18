"""Tests for core/logging_config.py"""

import logging

from manexp_web_lists.core.logging_config import SectionAwareFormatter, configure_logging, log_section, log_sub_section


def test_section_aware_formatter_normal_log():
    formatter = SectionAwareFormatter("%(levelname)s: %(message)s")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Normal log",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert formatted == "INFO: Normal log"


def test_section_aware_formatter_section_log():
    formatter = SectionAwareFormatter("%(levelname)s: %(message)s")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Section log",
        args=(),
        exc_info=None,
    )
    # Mark it as section
    record.section = True
    formatted = formatter.format(record)
    assert formatted == "Section log"


def test_configure_logging_output():
    log_stream = configure_logging()
    # Emit a log
    import logging

    logging.getLogger().info("Test message")

    # Check that the message is captured in the stream
    contents = log_stream.getvalue()
    assert "Test message" in contents


def test_log_section_format(caplog):
    caplog.set_level("INFO")
    log_section("SECTION TITLE")
    # The section marker is not important, just the message
    assert "SECTION TITLE" in caplog.text
    assert "=" * 60 in caplog.text


def test_log_sub_section_format(caplog):
    caplog.set_level("INFO")
    log_sub_section("SUB TITLE")
    assert "SUB TITLE" in caplog.text
    assert "-" * 60 in caplog.text


def test_normal_log_not_in_section_format(caplog):
    caplog.set_level("INFO")
    logging.getLogger().info("Normal text")
    assert "Normal text" in caplog.text
    assert "-" * 60 not in caplog.text
