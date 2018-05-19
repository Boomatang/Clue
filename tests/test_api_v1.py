import pytest
from flask import jsonify

paths = ['t1', 't10', 'tf']


@pytest.mark.parametrize('path', paths)
def test_end_points_good_status(client, path):
    assert client.get(f"/api/v1/bom/{path}").status_code == 200


paths = [2, 5, 8]


@pytest.mark.parametrize('path', paths)
def test_single_bom_results(client, path):
    compare = f"\"data id\": {path}"

    compare = str.encode(compare)

    result = client.get(f"/api/v1/bom/{path}").data

    assert compare in result


def test_single_bom_end_point_fail(client):
    assert 404 == client.get("/api/v1/bom/fail").status_code


paths = [("t1", {"job number": "t1 test",
                 "material": [{"size": "beam size 1", "qty": "1"}],
                 "total": 1,
                 "massage": "Found data for ID t1"}),
         ('t5', {"job number": "t5 test",
                 "material": [{"size": "beam size 1", "qty": "1"},
                              {"size": "beam size 2", "qty": "2"},
                              {"size": "beam size 3", "qty": "3"},
                              {"size": "beam size 4", "qty": "4"},
                              {"size": "beam size 5", "qty": "5"}],
                 "total": 5,
                 "massage": "Found data for ID t5"}),
         ('t10', {"job number": "t10 test",
                  "material": [{"size": "beam size 1", "qty": "1"},
                               {"size": "beam size 2", "qty": "2"},
                               {"size": "beam size 3", "qty": "3"},
                               {"size": "beam size 4", "qty": "4"},
                               {"size": "beam size 5", "qty": "5"},
                               {"size": "beam size 6", "qty": "6"},
                               {"size": "beam size 7", "qty": "7"},
                               {"size": "beam size 8", "qty": "8"},
                               {"size": "beam size 9", "qty": "9"},
                               {"size": "beam size 10", "qty": "10"}],
                  "total": 10,
                  "massage": "Found data for ID t10"})]


@ pytest.mark.parametrize('path', paths)
def test_single_bom_is_good_test_call(client, path):
    check = path[1]

    check = jsonify(check).data

    result = client.get(f"/api/v1/bom/{path[0]}").data

    assert check == result


def test_single_bom_is_good_fail_test_call(client):
    check = jsonify({"error": "BOM ID not found \nPlease check your input"}).data
    result = client.get("/api/v1/bom/tf").data

    assert check == result


paths = [2, 5, 8]


@pytest.mark.parametrize('path', paths)
def test_single_bom_is_not_test_call(client, path):
    check = b"test"

    result = client.get(f"/api/v1/bom/{path}")

    assert check not in result.data and 200 == result.status_code


def test_seeded_data_found(client):
    check = b'\"massage\": \"Found data for ID 2'
    result = client.get(f"/api/v1/bom/2").data
    assert check in result


def test_seed_data_not_found(client):
    assert 404 == client.get("/api/v1/bom/100").status_code


