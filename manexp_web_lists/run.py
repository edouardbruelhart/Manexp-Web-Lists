import logging

from manexp_web_lists.core import Mailer, configure_logging, log_section
from manexp_web_lists.countries import get_countries
from manexp_web_lists.phytosanitary_products import get_phytosanitary_products
from manexp_web_lists.register_subtypes import get_register_subtypes
from manexp_web_lists.register_types import get_register_types
from manexp_web_lists.seeds import get_seeds
from manexp_web_lists.taxonomy import get_taxonomy

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
        # Generate countries list
        log_section("GETTING COUNTRIES")
        get_countries()
        logger.info("✅ Done ✅")

        # Generate register types
        log_section("GETTING REGISTER TYPES")
        get_register_types()
        logger.info("✅ Done ✅")

        # Generate register subtypes
        log_section("GETTING REGISTRER SUBTYPES")
        get_register_subtypes()
        logger.info("✅ Done ✅")

        # Generate seeds list
        log_section("GETTING SEEDS")
        get_seeds()
        logger.info("✅ Done ✅")

        # Generate taxonomy list
        log_section("GETTING TAXONOMY")
        get_taxonomy()
        logger.info("✅ Done ✅")

        # Generate phytosanitary products list
        log_section("GETTING PHYTOSANITARY PRODUCTS")
        get_phytosanitary_products()
        logger.info("✅ Done ✅")

        # TODO: Uncomment this for prod
        # Send success recap
        # mailer.send_email(
        #     subject="Manexp-Web-List SUCCESS Report",
        #     body=log_stream.getvalue(),
        # )

    except Exception:
        logger.exception("Error while generating lists")
        mailer.send_email(
            subject="Manexp-Web-List EXCEPTION Report",
            body=log_stream.getvalue(),
        )


if __name__ == "__main__":  # pragma: no cover
    run()
