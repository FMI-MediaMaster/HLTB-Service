from typing import Dict
from fastapi.testclient import TestClient
from app import app

from metadata_service_tests import runMetadataTests, Fields

client: TestClient = TestClient(app)


def testController():
    validMap: Dict[str, str] = {
        "Clair Obscur": "152016",
        "Helldivers 2": "129232",
        "League of Legends": "5203",
    }

    invalidMap: Dict[str, str] = {
        "adasdasa": "-1",
        "": "nothing",
        "nonExistentGame": "nonExistentId",
    }

    fieldsMap: Dict[str, Fields] = {
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

    runMetadataTests(
        server=client,
        endpoint="",
        fieldsMap=fieldsMap,
        validMap=validMap,
        invalidMap=invalidMap,
        mediaType="game",
    )
