import logging

from manexp_web_lists.core import Mailer, configure_logging, log_section
from manexp_web_lists.phytosanitary_products import get_phytosanitary_products
from manexp_web_lists.seeds import get_seeds

# Initialize mailer
mailer = Mailer()

# Initialize logger
logger = logging.getLogger(__name__)


def run() -> None:
    """
    The main function to fetch all the lists
    """

    # Configure logging
    log_stream = configure_logging()

    try:
        # Generate seeds lists
        log_section("GETTING SEEDS")
        get_seeds()
        logger.info("✅ Done ✅")

        # Generate phytosanitary products lists
        log_section("GETTING PHYTOSANITARY PRODUCTS")
        get_phytosanitary_products()
        logger.info("✅ Done ✅")

        # Send success recap
        mailer.send_email(
            subject="Manexp-Web-List SUCCESS Report",
            body=log_stream.getvalue(),
        )

    except Exception:
        logger.exception("Error while generating lists")
        mailer.send_email(
            subject="Manexp-Web-List EXCEPTION Report",
            body=log_stream.getvalue(),
        )


if __name__ == "__main__":  # pragma: no cover
    run()
