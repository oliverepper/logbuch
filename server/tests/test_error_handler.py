def test_404_page(client):
    response = client.get('/nonexistant')
    assert response.status_code == 404