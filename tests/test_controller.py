import pytest
from typing import Dict
from fastapi.testclient import TestClient
from app import app

from metadata_service_tests import Fields, generateMetadataTests, test_valid_item, test_nonexistent_item, test_invalid_query, test_invalid_endpoint

VALID_MAP: Dict[str, str] = {
    "Clair Obscur": "152016",
    "Helldivers 2": "129232",
    "League of Legends": "5203",
}

INVALID_MAP: Dict[str, str] = {
    "adasdasa": "-1",
    "": "nothing",
    "nonExistentGame": "nonExistentId",
}

FILEDS_MAP: Dict[str, Fields] = {
    "options": {
        "id": {"type": "string"},
        "name": {"type": "string"},
    },
    "info": {
        "name": {"type": "string"},
        "main": {"type": "number", "empty": True},
        "main_extra": {"type": "number", "empty": True},
        "completionist": {"type": "number", "empty": True},
        "coop": {"type": "number", "empty": True},
        "multiplayer": {"type": "number", "empty": True},
        "singleplayer": {"type": "numberArray", "empty": True},
    },
}

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture
def mediaType():
    return "game"

tests = generateMetadataTests(
    endpoint="",
    fieldsMap=FILEDS_MAP,
    validMap=VALID_MAP,
    invalidMap=INVALID_MAP
)

# Generate pytests
def pytest_generate_tests(metafunc):
    if metafunc.function.__name__ == "test_valid_item":
        combinations = [
            (data["endpoint"], data["queryParameter"], item)
            for data in tests.values()
            for item in data["validItems"]
        ]

        ids = [f"endpoint={ep}&{qp}={item}" for ep, qp, item in combinations]
        metafunc.parametrize("endpoint,queryParameter,item", combinations, ids=ids)

    elif metafunc.function.__name__ == "test_nonexistent_item":
        combinations = [
            (data["endpoint"], data["queryParameter"], item)
            for data in tests.values()
            for item in data["nonExistentItems"]
        ]
        
        ids = [f"endpoint={ep}&{qp}={item}" for ep, qp, item in combinations]
        metafunc.parametrize("endpoint,queryParameter,item", combinations, ids=ids)

    elif metafunc.function.__name__ == "test_invalid_query":
        combinations = [
            (data["endpoint"], query)
            for data in tests.values()
            for query in data["invalidQueries"]
        ]

        ids = [f"endpoint={ep}&{q}" for ep, q in combinations]
        metafunc.parametrize("endpoint,invalidQuery", combinations, ids=ids)

    elif metafunc.function.__name__ == "test_invalid_endpoint":
        combinations = [
            (data["endpoint"])
            for data in tests.values()
        ]

        ids = [f"endpoint={ep}" for ep in combinations]
        metafunc.parametrize("endpoint", combinations, ids=ids)


# Test functions
test_valid_item
test_nonexistent_item
test_invalid_query
test_invalid_endpoint
