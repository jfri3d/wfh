from api.model import Actions


def test_post_valid_action(client):
    for action in Actions:
        response = client.post(f"/{action.name}")
        assert response.status_code == 200


def test_post_invalid_action(client):
    response = client.post("/BAD")
    assert response.json["status"] == 400


def test_get_valid_action(client):
    for action in Actions:
        response = client.get(f"/actions/{action.name}")
        print(response.json)
        # FIXME - this is blank!
        assert response.status_code == 200


def test_get_today(client):
    response = client.get("/today")
    print(response.json)
    # FIXME - this is blank!
    assert response.status_code == 200


def test_get_invalid_action(client):
    response = client.get(f"/actions/BAD")
    assert response.status_code == 400
