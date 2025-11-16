from typing import Callable, Any, Dict, List, Union
from fastapi.testclient import TestClient

TypeMap = {
    "number": Union[int, float],
    "string": str,
    "object": dict,
    "stringArray": list,
    "numberArray": list,
    "objectArray": list,
}

Fields = Dict[str, Dict[str, str]]


def runEndpointTests(
    server: TestClient,
    endpoint: str,
    fields: Dict[str, Any],
    validItems: List[str],
    nonExistentItems: List[str],
    invalidQueries: List[str],
    mediaType: str,
):
    fieldKeys = fields.keys()
    queryType = endpoint.split("/")[-1]
    queryParameter = "name" if queryType == "options" else "id"

    def checkFields(item: Dict):
        assert item.keys() == fieldKeys

        for key, props in fields.items():
            type_str = props.get("type", "")
            value = item.get(key)

            if value is not None:
                if "Array" in type_str:
                    type_str = type_str.replace("Array", "")
                    expected_type = TypeMap.get(type_str, object)
                    assert all(isinstance(x, expected_type) for x in value), (
                        f"All elements in {key} must be {type_str}"
                    )
                else:
                    expected_type = TypeMap.get(type_str, object)
                    assert isinstance(value, expected_type), f"{key} must be {type_str}"

            if not props.get("empty", False):
                assert value is not None, f"{key} must not be None"

    def capitalize(s: str) -> str:
        return s if not s else s[0].upper() + s[1:]

    for item in validItems:
        response = server.get(endpoint, params={queryParameter: item})
        assert response.status_code == 200
        body = response.json()

        if queryType == "info":
            assert isinstance(body, dict)
            assert body is not None
            checkFields(body)
        else:
            assert isinstance(body, list)
            assert len(body) > 0
            for it in body:
                checkFields(it)

    for item in nonExistentItems:
        response = server.get(endpoint, params={queryParameter: item})
        body = response.json()

        if queryType == "info":
            assert response.status_code == 404
            assert isinstance(body, dict)
            assert "error" in body
            assert body["error"] == f"{capitalize(mediaType)} not found"
        else:
            assert response.status_code == 200
            assert isinstance(body, list)
            assert len(body) == 0

    response = server.get(endpoint)
    assert response.status_code == 400
    body = response.json()
    assert "error" in body
    assert body["error"] == f"Missing parameter for the {queryType} endpoint"

    for invalidQuery in invalidQueries:
        response = server.get(endpoint, params={invalidQuery: ""})
        assert response.status_code == 400
        body = response.json()
        assert "error" in body
        assert body["error"] == f"Missing parameter for the {queryType} endpoint"


def runMetadataTests(
    server: TestClient,
    endpoint: str,
    fieldsMap: Dict[str, Dict[str, dict]],
    validMap: Dict[str, str],
    invalidMap: Dict[str, str],
    mediaType: str,
):
    first = next(iter(validMap.items()))

    def destroyQuery(method: str, key: str, value: str) -> str:
        options = {
            "split": f"{key[0]} {key[1:]}={value}",
            "duplicate": f"{key[0] * 2}{key}={value}",
        }
        return options.get(method, f"{key}={value}")

    def buildConfig(
        objectFn: Callable[[Dict[str, Any]], List], queryName: str
    ) -> Dict[str, List]:
        return {
            "validItems": objectFn(validMap),
            "nonExistentItems": objectFn(invalidMap),
            "invalidQueries": list(
                map(
                    lambda m: destroyQuery(m, queryName, first[int(queryName == "id")]),
                    ["split", "duplicate"],
                )
            ),
        }

    testsMap: Dict = {
        "options": buildConfig(lambda d: list(d.keys()), "name"),
        "info": buildConfig(lambda d: list(d.values()), "id"),
    }

    validMethods = fieldsMap.keys()
    for method, params in testsMap.items():
        if method not in validMethods:
            continue

        runEndpointTests(
            server=server,
            endpoint=f"{endpoint}/{method}",
            fields=fieldsMap[method],
            validItems=params["validItems"],
            nonExistentItems=params["nonExistentItems"],
            invalidQueries=params["invalidQueries"],
            mediaType=mediaType,
        )
