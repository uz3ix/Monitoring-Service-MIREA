def test_create_device(client, admin):
    payload = {
        "name": "Test",
        "agent_token": "ab"*16
    }
    
    response = client.post("/devices", headers = admin, json = payload)
    
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
    assert response.json()["id"] >=1
    assert response.json()["status"] == "offline"
    assert response.json()["last_seen_at"] is None
    assert "agent_token" and "agent_token_hash" not in response.json()
    
    data = response.json()
    
    response = client.get(f"/devices/{data["id"]}", headers = admin)
    
    assert response.status_code == 200
    assert response.json()["id"] == data["id"]
    assert response.json()["name"] == data["name"]


def test_create_device_with_token_already_exsist(client, admin):
    response = client.post("/devices", headers = admin, json={
        "name": "test1",
        "agent_token": "ab"*16
    })
    
    assert response.status_code == 201
    
    response = client.post("/devices", headers = admin, json={
            "name": "test2",
            "agent_token": "ab"*16
        })
        
    assert response.status_code == 409
    
    
    response = client.get("/devices", headers = admin)
    
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "test1"
        
    