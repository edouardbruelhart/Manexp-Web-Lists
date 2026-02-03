from manexp_web_lists.client import DownloadJsonClient as APIClient

# from manexp_web_lists.mail import Mailer


def main() -> None:
    """Main function to fetch and validate crops list."""

    client = APIClient(
        "https://raw.githubusercontent.com/blw-ofag-ufag/blw-ogd-data/refs/heads/main/data/plant_varieties_in_switzerland.json",
        "../lists/test/test2.json",
    )

    try:
        # 1. Use the client to download raw json
        client.download_file()

    except Exception as e:
        # TODO: Uncomment the email notification once code is in production and remove print
        print(f"An error occurred in the main process: {e}")
        # mailer = Mailer()

        # mailer.send_email(
        #     subject="Error fetching crops list",
        #    body=f"An error occurred in the main process: {e}"
        # )


if __name__ == "__main__":
    main()
