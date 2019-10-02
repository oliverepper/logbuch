# CRUD

# CREATE
def test_create_log(client, api_tokens):
    response = client.post(
        "/api/logs",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={"title": "Test Log"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 201
    assert "<Log 1> created." in json_data["message"]


# TODO: CREATE EXISTING TITLE
def test_create_log_with_existing_title(client, api_tokens):
    response = client.post(
        "/api/logs",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={"title": "Test Log"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 400
    assert 'Your <Log 1> is titled "Test Log" already.' in json_data["message"]


# CREATE BROKEN JSON
def test_create_log_broken_json(client, api_tokens):
    response = client.post(
        "/api/logs",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={"title": "Test Log", "non-existant-in-model": "Test Log"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 400
    assert "{'non-existant-in-model': ['Unknown field.']}" in json_data["message"]


# READ ALL
def test_get_logs(client, api_tokens):
    response = client.get(
        "/api/logs",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
    )
    json_data = response.get_json() or {}
    assert len(json_data["logs"]) > 0


# READ ONE
def test_get_log(client, api_tokens):
    response = client.get(
        "/api/logs/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 200
    assert "Test Log" == json_data["title"]


# READ FOREIGN LOG
def test_get_foreign_log(client, api_tokens):
    response = client.get(
        "/api/logs/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_two.value}"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 404
    assert "<Log 1> not found in your logs." in json_data["message"]


# UPDATE
def test_update_log(client, api_tokens):
    response = client.put(
        "/api/logs/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={"title": "Test new title"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 200
    assert "<Log 1> updated." in json_data["message"]


# UPDATE FOREIGN LOG
def test_update_foreign_log(client, api_tokens):
    response = client.put(
        "/api/logs/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_two.value}"},
        json={"title": "Test another title"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 404
    assert "<Log 1> not found in your logs." in json_data["message"]


# UPDATE DISALLOW ID CHANGE - OLD VERSION
# def test_update_log_disallow_id_change(client, api_tokens):
#     response = client.put(
#         "/api/logs/1",
#         headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
#         json={"title": "Test another title", "id": 1001},
#     )
#     json_data = response.get_json() or {}
#     assert response.status_code == 403
#     assert "You're not allowed to change the id of <Log 1>." in json_data["message"]


# UPDATE DISALLOW ID CHANGE - dump_only id
def test_update_log_disallow_id_change(client, api_tokens):
    response = client.put(
        "/api/logs/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={"title": "Test another title", "id": 1001},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 400
    assert "Unknown field." in json_data["message"]


# UPDATE LOG OWNER
def test_update_log_owner(client, api_tokens):
    response = client.put(
        "/api/logs/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={"title": "Test another title", "owner": "2"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 403
    assert "You are not allowed to update the owner for <Log 1>." in json_data["message"]


# DELETE
def test_delete_log(client, api_tokens):
    response = client.delete(
        "/api/logs/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 200
    assert "<Log 1> deleted." in json_data["message"]


# DELETE FOREIGN LOG
def test_foreign_log(client, api_tokens):
    response = client.delete(
        "/api/logs/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_two.value}"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 404
    assert "<Log 1> not found in your logs." in json_data["message"]
