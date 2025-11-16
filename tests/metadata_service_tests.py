from typing import Callable, Any, Dict, List, Union

TypeMap = {
    "number": Union[int, float],
    "string": str,
    "object": dict,
    "stringArray": list,
    "numberArray": list,
    "objectArray": list,
}

Fields = Dict[str, Dict[str, str]]


fields: Dict
tests: Dict


def checkFields(method: str, item: Dict):
    assert item.keys() == fields[method].keys()

    for key, props in fields[method].items():
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


def test_valid_item(client, endpoint, queryParameter, item):
    queryType = endpoint.split("/")[-1]

    response = client.get(endpoint, params={queryParameter: item})
    assert response.status_code == 200
    body = response.json()

    queryType = endpoint.split("/")[-1]
    if queryType == "info":
        assert isinstance(body, dict)
        assert body is not None
        checkFields(queryType, body)
    else:
        assert isinstance(body, list)
        assert len(body) > 0
        for it in body:
            checkFields(queryType, it)


def test_nonexistent_item(client, mediaType, endpoint, queryParameter, item):
    queryType = endpoint.split("/")[-1]

    response = client.get(endpoint, params={queryParameter: item})
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


def test_invalid_query(client, endpoint, invalidQuery):
    response = client.get(endpoint, params={invalidQuery: ""})
    assert response.status_code == 400

    body = response.json()
    assert "error" in body

    queryType = endpoint.split("/")[-1]
    assert body["error"] == f"Missing parameter for the {queryType} endpoint"


def test_invalid_endpoint(client, endpoint):
    response = client.get(endpoint)
    assert response.status_code == 400

    body = response.json()
    assert "error" in body

    queryType = endpoint.split("/")[-1]
    assert body["error"] == f"Missing parameter for the {queryType} endpoint"


def generateMetadataTests(
    endpoint: str,
    fieldsMap: Dict[str, Dict[str, dict]],
    validMap: Dict[str, str],
    invalidMap: Dict[str, str],
):
    global fields
    global tests

    fields = fieldsMap
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

    queryParameterMap: Dict = {
        "options": "name",
        "info": "id",
    }

    testsMap: Dict = {
        "options": buildConfig(lambda d: list(d.keys()), queryParameterMap["options"]),
        "info": buildConfig(lambda d: list(d.values()), queryParameterMap["info"]),
    }

    validMethods = fieldsMap.keys()
    tests = {
        method: {
            "endpoint": f"{endpoint}/{method}",
            "queryParameter": queryParameterMap[method],
            "validItems": params["validItems"],
            "nonExistentItems": params["nonExistentItems"],
            "invalidQueries": params["invalidQueries"],
        }
        for method, params in testsMap.items()
        if method in validMethods
    }


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
        combinations = [(data["endpoint"]) for data in tests.values()]

        ids = [f"endpoint={ep}" for ep in combinations]
        metafunc.parametrize("endpoint", combinations, ids=ids)
