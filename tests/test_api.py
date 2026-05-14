def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_create_item_endpoint(client):
    payload = {"name": "Minecraft Stone", "type": "Block"}
    response = client.post("/items/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Minecraft Stone"
    assert "id" in data