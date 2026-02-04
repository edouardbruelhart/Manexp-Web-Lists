from manexp_web_lists.client import JsonClient

# from manexp_web_lists.mail import Mailer


def main() -> None:
    """Main function to fetch and validate crops list."""

    # initialize the client
    url = "https://raw.githubusercontent.com/blw-ofag-ufag/blw-ogd-data/refs/heads/main/data/plant_varieties_in_switzerland.json"
    file_path = "../lists/raw/crops_list.json"
    client = JsonClient(url, file_path)

    try:
        # 1. Use the client to download raw json
        client.download_file()

        # 2. Load and validate the downloaded json
        data = client.load_file()

        # print(data)
        print(type(data))

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
