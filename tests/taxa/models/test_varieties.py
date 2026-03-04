"""Tests for taxa/models/varieties.py"""

from datetime import date

import pytest

from manexp_web_lists.taxa.models.varieties import CurrentDenomination, Varieties


def test_current_denomination():
    data = {
        "denomination": "Vitalion",
        "status": "Approved",
        "validFrom": "2023-04-13",
    }

    current = CurrentDenomination.model_validate(data)

    assert current.denomination == "Vitalion"
    assert current.status.status == "Approved"
    assert current.status.valid_from == date(2023, 4, 13)


def test_current_denomination_extra_field():
    current = CurrentDenomination.model_validate({
        "denomination": "Vitalion",
        "status": "Approved",
        "validFrom": "2023-04-13",
        "extra": "Test extra",
    })

    assert current.denomination == "Vitalion"


def test_current_denomination_missing_status_field():
    with pytest.raises(KeyError):
        CurrentDenomination.model_validate({
            "denomination": "Vitalion",
            "validFrom": "2023-04-13",
        })


def test_current_denomination_json_roundtrip():
    data = {
        "denomination": "Vitalion",
        "status": "Approved",
        "validFrom": "2023-04-13",
    }

    current = CurrentDenomination.model_validate(data)
    json_out = current.model_dump_json()

    loaded = CurrentDenomination.model_validate_json(json_out)

    assert loaded == current


def test_varieties():
    data = {
        "varieties": [
            {
                "id": "e6367871-435a-3c6e-aed7-20fee0b10ae9",
                "dossierStatus": "Finalized",
                "breedersReference": "NUN 09398 TOF",
                "breedingCountry": "BO",
                "cropCategory": "Vegetable Crops",
                "botanicalInformation": {
                    "family": "Solanaceae",
                    "genus": "Solanum L.",
                    "species": "Solanum lycopersicum L.",
                    "upovCode": "SOLAN_LYC",
                },
                "currentlyRelevantDenomination": {
                    "denomination": "Vitalion",
                    "status": "Approved",
                    "validFrom": "2023-04-13",
                },
                "denominations": [
                    {
                        "denomination": "Vitalion",
                        "statusHistory": [
                            {"status": "Approved", "validFrom": "2023-04-13"},
                            {"status": "Proposed", "validFrom": "2023-04-13"},
                        ],
                    }
                ],
                "plantBreedersRight": {
                    "status": "Registered",
                    "request": {"number": "23-3559", "entryDate": "2023-04-13"},
                    "register": {"number": "25.3179", "grantOfProtection": "2025-02-28", "maxProtectionYears": 25},
                    "contacts": {
                        "agent": {
                            "name": "Micheli \u0026 Cie SA",
                            "address": "Rue de Gen\u00e8ve 122",
                            "postBox": "",
                            "postalCode": "1226",
                            "city": "Th\u00f4nex",
                            "country": "CH",
                        }
                    },
                },
                "contacts": {
                    "owners": [
                        {
                            "name": "Nunhems B.V.",
                            "address": "Napoleonsweg 152",
                            "postBox": "",
                            "postalCode": "6083 AB",
                            "city": "Nunhem",
                            "country": "NL",
                        }
                    ],
                    "breeders": [
                        {
                            "name": "Nunhems B.V.",
                            "address": "Napoleonsweg 152",
                            "postBox": "",
                            "postalCode": "6083 AB",
                            "city": "Nunhem",
                            "country": "NL",
                        }
                    ],
                },
            },
            {
                "id": "91e9cdb5-86c5-5549-d27c-4b7e3a895db2",
                "dossierStatus": "Finalized",
                "breedingCountry": "DE",
                "tradeNames": ["Royal@Amethyst"],
                "cropCategory": "Ornamental and medicinal plants",
                "botanicalInformation": {
                    "family": "Geraniaceae",
                    "genus": "Pelargonium L\u0027H\u00e9r. ex Ait.",
                    "species": "Pelargonium peltatum (L.) L\u0027H\u00e9r.",
                    "upovCode": "PELAR_PEL",
                },
                "currentlyRelevantDenomination": {
                    "denomination": "KLEPP 23766",
                    "status": "Approved",
                    "validFrom": "2023-05-15",
                },
                "denominations": [
                    {
                        "denomination": "KLEPP 23766",
                        "statusHistory": [
                            {"status": "Approved", "validFrom": "2023-05-15"},
                            {"status": "Proposed", "validFrom": "2023-05-15"},
                        ],
                    }
                ],
                "plantBreedersRight": {
                    "status": "Registered",
                    "request": {"number": "23-3577", "entryDate": "2023-05-15"},
                    "register": {"number": "25.3180", "grantOfProtection": "2025-02-28", "maxProtectionYears": 25},
                    "contacts": {
                        "agent": {
                            "name": "Beck AG",
                            "address": "Feldmattstrasse 29",
                            "postBox": "",
                            "postalCode": "6032",
                            "city": "Emmen",
                            "country": "CH",
                        }
                    },
                },
                "contacts": {
                    "owners": [
                        {
                            "name": "Klemm \u002b Sohn GmbH \u0026 Co KG",
                            "address": "Hanf\u00e4cker 10",
                            "postBox": "",
                            "postalCode": "70378",
                            "city": "Stuttgart",
                            "country": "DE",
                        }
                    ],
                    "breeders": [
                        {
                            "name": "Nina Neu c/o Klemm \u002b Sohn GmbH \u0026 Co KG",
                            "address": "Hanf\u00e4cker 10",
                            "postBox": "",
                            "postalCode": "70378",
                            "city": "Stuttgart",
                            "country": "DE",
                        }
                    ],
                },
            },
            {
                "id": "ed347a6f-b861-e0a0-c86c-8e0799d94b7a",
                "dossierStatus": "Finalized",
                "breedingCountry": "DE",
                "tradeNames": ["Marcada Violet"],
                "cropCategory": "Ornamental and medicinal plants",
                "botanicalInformation": {
                    "family": "Geraniaceae",
                    "genus": "Pelargonium L\u0027H\u00e9r. ex Ait.",
                    "species": "hybrids between Pelargonium peltatum and Pelargonium zonale",
                    "upovCode": "PELAR_PZO",
                },
                "currentlyRelevantDenomination": {
                    "denomination": "KLEIP 23785",
                    "status": "Approved",
                    "validFrom": "2023-05-15",
                },
                "denominations": [
                    {
                        "denomination": "KLEIP 23785",
                        "statusHistory": [
                            {"status": "Approved", "validFrom": "2023-05-15"},
                            {"status": "Proposed", "validFrom": "2023-05-15"},
                        ],
                    }
                ],
                "plantBreedersRight": {
                    "status": "Registered",
                    "request": {"number": "23-3578", "entryDate": "2023-05-15"},
                    "register": {"number": "25.3181", "grantOfProtection": "2025-02-28", "maxProtectionYears": 25},
                    "contacts": {
                        "agent": {
                            "name": "Beck AG",
                            "address": "Feldmattstrasse 29",
                            "postBox": "",
                            "postalCode": "6032",
                            "city": "Emmen",
                            "country": "CH",
                        }
                    },
                },
                "contacts": {
                    "owners": [
                        {
                            "name": "Klemm \u002b Sohn GmbH \u0026 Co KG",
                            "address": "Hanf\u00e4cker 10",
                            "postBox": "",
                            "postalCode": "70378",
                            "city": "Stuttgart",
                            "country": "DE",
                        }
                    ],
                    "breeders": [
                        {
                            "name": "Nina Neu c/o Klemm \u002b Sohn GmbH \u0026 Co KG",
                            "address": "Hanf\u00e4cker 10",
                            "postBox": "",
                            "postalCode": "70378",
                            "city": "Stuttgart",
                            "country": "DE",
                        }
                    ],
                },
            },
        ]
    }

    data = Varieties.model_validate(data)

    assert len(data.varieties) == 3
    assert data.varieties[0].id == "e6367871-435a-3c6e-aed7-20fee0b10ae9"
    assert data.varieties[1].current_denomination.status.valid_from == date(2023, 5, 15)
