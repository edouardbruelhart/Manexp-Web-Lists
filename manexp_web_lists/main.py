from manexp_web_lists.taxa.fetch_taxa import fetch_taxa


def main() -> None:
    """Main function to fetch and validate all lists"""

    try:
        # Crops and species lists
        fetch_taxa()

    except Exception as e:
        print(f"An error occurred in the main process: {e}")
        # mailer = Mailer()

        # mailer.send_email(subject="Error fetching lists", body=f"An error occurred in the main process: {e}")


if __name__ == "__main__":
    main()
