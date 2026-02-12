import logging
from io import StringIO

log_stream = StringIO()

logger = logging.getLogger(__name__)


class SectionAwareFormatter(logging.Formatter):
    """
    Avoid to print headers for section and sub sections logs
    """

    def format(self, record: logging.LogRecord) -> str:
        # Section headers: no time, no level
        if getattr(record, "section", False):
            return record.getMessage()

        # Normal logs
        return super().format(record)


def configure_logging() -> StringIO:
    """
    Configure logging

    :return: The log stream for further use
    :rtype: StringIO
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = SectionAwareFormatter("%(levelname)s: %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    memory = logging.StreamHandler(log_stream)
    memory.setFormatter(formatter)

    root_logger.handlers.clear()
    root_logger.addHandler(console)
    root_logger.addHandler(memory)

    return log_stream


def log_section(title: str) -> None:
    """
    Create a section in the log

    :param title: Title of the section
    :type title: str
    """
    line = "=" * 60
    logger.info(
        "\n%s\n%s\n%s",
        line,
        title,
        line,
        extra={"section": True},
    )


def log_sub_section(title: str) -> None:
    """
    Create a sub section in the log

    :param title: Title of the sub section
    :type title: str
    """
    line = "-" * 60
    logger.info(
        "\n%s\n%s\n%s",
        line,
        title,
        line,
        extra={"section": True},
    )
