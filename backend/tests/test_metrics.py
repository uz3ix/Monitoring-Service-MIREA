from datetime import datetime, timezone


def test_agent_send_metrics(client, admin):
    response = client.post("/devices", headers = admin, json={
            "name": "test1",
            "agent_token": "ab"*16
        })
        
    assert response.status_code == 201
    
    id = response.json()["id"]
    
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": 33.3,
        "memory_used_bytes": 4000,
        "memory_total_bytes": 8000,
        "disks": [
            {
                "name": "C://",
                "disk_used_bytes": 10000,
                "disk_total_bytes": 20000,
            }
        ],
        "services": {
            "win": "running"
        },
    }
    
    response = client.post("/metrics", headers = {"X-Agent-Token": "ab"*16}, json = payload)
    
    assert response.status_code == 201
    assert response.json()["id"] == id 
    assert response.json()["cpu_percent"] ==  33.3
    assert response.json()["memory_used_bytes"] ==  4000
    assert response.json()["memory_total_bytes"] ==  8000
    
    
    response = client.get(f"/devices/{id}/metrics/latest", headers = admin)
    
    assert response.status_code == 200
    assert response.json()["id"] == id