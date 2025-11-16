import pytest
from typing import Dict
from fastapi.testclient import TestClient
from app import app

from metadata_service_tests import (
    Fields,
    generateMetadataTests,
    pytest_generate_tests,
    test_valid_item,
    test_nonexistent_item,
    test_invalid_query,
    test_invalid_endpoint,
)

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


generateMetadataTests(
    endpoint="", fieldsMap=FILEDS_MAP, validMap=VALID_MAP, invalidMap=INVALID_MAP
)

# Tests
pytest_generate_tests
test_valid_item
test_nonexistent_item
test_invalid_query
test_invalid_endpoint
