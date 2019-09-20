# CRUD

# CREATE ENTRY
def test_create_entry(client, api_tokens, db_with_log):
    response = client.post(
        "/api/logs/1/entries",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={"content": "Test content for entry."},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 201
    assert "<Entry 1> created in <Log 1>." in json_data["message"]


def test_create_entry_in_foreign_log(client, api_tokens, db_with_log):
    response = client.post(
        "/api/logs/1/entries",
        headers={"Authorization": f"Bearer {api_tokens.token_user_two.value}"},
        json={"content": "Will fail because of foreign log."},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 404
    assert "<Log 1> not found in your logs. Cannot create Entry." in json_data["message"]


def test_create_entry_in_different_log(client, api_tokens, db_with_log):
    response = client.post(
        "/api/logs/1/entries",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={"content": "Will fail because user provided different log ids.", "log": 2},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 403
    assert "Argument error. Log mismatch." in json_data["message"]


# READ ENTRY
def test_get_entries(client, api_tokens, log_with_entries):
    response = client.get(
        f"/api/logs/{log_with_entries.id}/entries",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 200
    assert len(json_data["entries"]) == 3


def test_get_entry(client, api_tokens):
    response = client.get(
        "/api/entries/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 200
    assert "Test content for entry." in json_data["content"]


# READ FOREIGN ENTRY
def test_get_entry(client, api_tokens):
    response = client.get(
        "/api/entries/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_two.value}"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 404
    assert "Entry <1> not available." in json_data["message"]


# UPDATE ENTRY

# DELETE ENTRY
