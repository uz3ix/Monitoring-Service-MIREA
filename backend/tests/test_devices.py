from datetime import datetime, timezone
from app.db.session import SessionLocal
from app.modules.devices.models import Device


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
    assert "agent_token" not in response.json() and "agent_token_hash" not in response.json()
    
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
        

def test_rotate_agent_token(client, admin):
    old_token = "a"*32
    new_token = "b"*32
    
    response = client.post("/devices", headers = admin, json={
        "name": "test",
        "agent_token": old_token
    })
    
    device_id = response.json()["id"]
    
    assert response.status_code == 201
    
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": 25.5,
    }
    
    response = client.post("/metrics", headers={"X-Agent-Token": old_token}, json=payload)
    
    assert response.status_code == 201
    
    metric_id = response.json()["id"]
    
    response = client.put(f"/devices/{device_id}/agent-token", headers=admin, json={"agent_token": new_token})
    
    assert response.status_code == 200
    assert response.json()["id"] == device_id
    
    response = client.get(f"/devices/{device_id}/metrics/latest", headers=admin)
    
    assert response.status_code == 200
    assert response.json()["id"] == metric_id
    
    response = client.post("/metrics", headers={"X-Agent-Token": old_token}, json=payload)
    
    assert response.status_code == 401
    
    response = client.get(f"/devices/{device_id}/metrics/latest", headers=admin)
        
    assert response.status_code == 200
    assert response.json()["id"] == metric_id
    
    response = client.post("/metrics", headers={"X-Agent-Token": new_token}, json=payload)
        
    assert response.status_code == 201
    
    
def test_delete_device(client, admin):
    response = client.post("/devices", headers = admin, json={
        "name": "test",
        "agent_token": "ab"*16
    })
    
    assert response.status_code ==201
    device_id = response.json()["id"]
    
    response = client.delete(f"/devices/{device_id}", headers=admin)
    
    assert response.status_code == 204
    assert response.content == b""
    
    response = client.get(f"/devices/{device_id}", headers=admin)
    
    assert response.status_code == 404
    
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": 50
    }

    response = client.post("/metrics", headers={"X-Agent-Token": "ab"*16} , json=payload)
    
    assert response.status_code == 401
    
    with SessionLocal() as db:
        assert db.get(Device, device_id) is None