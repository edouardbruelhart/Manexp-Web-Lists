class FetchException(Exception):
    def __init__(self, taxon: str, custom_message: str):
        self.taxon = taxon
        self.custom_message = custom_message
        super().__init__(taxon)

    def __str__(self) -> str:
        return f"Request failed for taxon {self.taxon}: {self.custom_message}"
