def test_get_logs(client, api_token):
    response = client.get(
        "/api/logs",
        headers = {"Authorization": f"Bearer {api_token.value}"}
    )
    json_data = response.get_json() or {}
    assert len(json_data["logs"]) > 0


def test_get_log(client, api_token):
    response = client.get(
        "/api/logs/1",
        headers = {"Authorization": f"Bearer {api_token.value}"}
    )
    json_data = response.get_json() or {}
    assert 'Golf' == json_data["title"]
