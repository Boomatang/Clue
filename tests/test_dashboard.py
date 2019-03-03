

from tests.conftest import login_standard_user


def test_user_deletes_bom_result(client, simple_bom):
    login_standard_user(client)
    bom = simple_bom
    view_url = f'/BOM/result/{bom.asset}'
    url = f"/BOM/results/remove/{bom.asset}"

    resp = client.get(url)

    assert resp.status_code == 200
    url = f"/BOM/results/remove/{bom.asset}/agree"
    resp = client.get(url)
    assert resp.status_code == 302

    view_resp = client.get(view_url)
    assert view_resp.status_code == 404
