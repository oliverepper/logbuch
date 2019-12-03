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


# CREATE ENTRY BROKEN JSON
def test_create_entry_broken_json(client, api_tokens, db_with_log):
    response = client.post(
        "/api/logs/1/entries",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={
            "content": "Test content for entry.",
            "non-existant-in-model": "Test content for entry",
        },
    )
    json_data = response.get_json() or {}
    assert response.status_code == 400
    assert "{'non-existant-in-model': ['Unknown field.']}" in json_data["message"]


# CREATE ENTRY IN FOREIGN LOG
def test_create_entry_in_foreign_log(client, api_tokens, db_with_log):
    response = client.post(
        "/api/logs/1/entries",
        headers={"Authorization": f"Bearer {api_tokens.token_user_two.value}"},
        json={"content": "Will fail because of foreign log."},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 404
    assert "<Log 1> not found in your logs. Cannot create entry." in json_data["message"]


# CREATE ENTRY IN DIFFERENT LOG
def test_create_entry_in_different_log(client, api_tokens, db_with_log):
    response = client.post(
        "/api/logs/1/entries",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={"content": "Will fail because user provided different log ids.", "log": 2},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 403
    assert "Argument error. Log mismatch." in json_data["message"]


# READ ENTRIES
def test_get_entries(client, api_tokens, log_with_entries):
    response = client.get(
        f"/api/logs/{log_with_entries.id}/entries",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 200
    # assert len(json_data["entries"]) == 3
    assert len(json_data) == 3


# READ ENTRIES FROM FOREIGN LOG
def test_get_entries_foreign_log(client, api_tokens, log_with_entries):
    response = client.get(
        f"/api/logs/{log_with_entries.id}/entries",
        headers={"Authorization": f"Bearer {api_tokens.token_user_two.value}"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 404
    assert f"{log_with_entries} not found in your logs." in json_data["message"]


# READ ENTRY
def test_get_entry(client, api_tokens):
    response = client.get(
        "/api/entries/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 200
    assert "Test content for entry." in json_data["content"]


# READ FOREIGN ENTRY
def test_get_entry_foreign_key(client, api_tokens):
    response = client.get(
        "/api/entries/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_two.value}"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 404
    assert "<Entry 1> not found in your logs." in json_data["message"]


# UPDATE ENTRY
def test_update_entry(client, api_tokens):
    response = client.put(
        "/api/entries/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={"content": "New content for the test entry."},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 200
    assert "<Entry 1> updated." in json_data["message"]


# UPDATE FOREIGN ENTRY
def test_update_foreign_entry(client, api_tokens):
    response = client.put(
        "/api/entries/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_two.value}"},
        json={"content": "New content for the test entry."},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 404
    assert "<Entry 1> not found in your logs." in json_data["message"]


# UPDATE ENTRY BROKEN JSON
def test_update_entry_broken_json(client, api_tokens):
    response = client.put(
        "/api/entries/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={
            "content": "New content for the test entry.",
            "non-existant-in-model": "New content for the test entry",
        },
    )
    json_data = response.get_json() or {}
    assert response.status_code == 400
    assert "{'non-existant-in-model': ['Unknown field.']}" in json_data["message"]


# UPDATE MOVE ENTRY IN OTHER LOG (USER OWNS LOG)
def test_update_entry_move_to_other_log_of_user(client, api_tokens, src_dst_logs):
    assert len(src_dst_logs.src_log.entries) == 1
    assert len(src_dst_logs.dst_log.entries) == 0
    response = client.put(
        f"/api/entries/{src_dst_logs.src_log.entries[0].id}",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={"log": src_dst_logs.dst_log.id},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 200
    assert len(src_dst_logs.src_log.entries) == 0
    assert len(src_dst_logs.dst_log.entries) == 1
    assert f"{src_dst_logs.dst_log.entries[0]} updated." in json_data["message"]


# UPDATE MOVE ENTRY IN OTHER LOG (USER DOES NOT OWN LOG)
def test_update_entry_move_to_other_log_of_another_user(client, api_tokens, src_dst_logs):
    assert len(src_dst_logs.src_log.entries) == 1
    assert len(src_dst_logs.dst_log.entries) == 0
    response = client.put(
        f"/api/entries/{src_dst_logs.src_log.entries[0].id}",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
        json={"log": src_dst_logs.dst_log_other_user.id},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 403
    assert len(src_dst_logs.src_log.entries) == 1
    assert len(src_dst_logs.dst_log.entries) == 0
    assert f"You're not allowed to perform this update." in json_data["message"]


# DELETE ENTRY
def test_delete_entry(client, api_tokens):
    response = client.delete(
        "/api/entries/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_one.value}"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 200
    assert "<Entry 1> deleted from <Log 1>" in json_data["message"]


# DELETE FOREIGN ENTRY
def test_delete_foreign_entry(client, api_tokens):
    response = client.delete(
        "/api/entries/1",
        headers={"Authorization": f"Bearer {api_tokens.token_user_two.value}"},
    )
    json_data = response.get_json() or {}
    assert response.status_code == 404
    assert "<Entry 1> not found in your logs." in json_data["message"]
