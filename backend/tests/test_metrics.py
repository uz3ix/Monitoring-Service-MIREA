from datetime import datetime, timezone


def test_agent_send_metrics(client, admin):
    response = client.post("/devices", headers = admin, json={
            "name": "test1",
            "agent_token": "ab"*16
    })
        
    assert response.status_code == 201
    
    device_id = response.json()["id"]
    
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": 33.3,
        "memory_used_bytes": 4000,
        "memory_total_bytes": 8000,
        "disks": [
            {
                "name": "C://",
                "disk_used_bytes": 10000,
                "disk_total_bytes": 20000
            }
        ],
        "services": {
            "win": "running"
        }
    }
    
    response = client.post("/metrics", headers = {"X-Agent-Token": "ab"*16}, json = payload)
    
    metrics_id = response.json()["id"]
    
    assert response.status_code == 201
    assert response.json()["device_id"] == device_id 
    assert response.json()["cpu_percent"] ==  33.3
    assert response.json()["memory_used_bytes"] ==  4000
    assert response.json()["memory_total_bytes"] ==  8000
    
    
    response = client.get(f"/devices/{device_id}/metrics/latest", headers = admin)
    
    assert response.status_code == 200
    assert response.json()["id"] == metrics_id
    assert response.json()["device_id"] == device_id
    
    
def test_invalid_cpu_more_100(client, admin):
    response = client.post("/devices", headers = admin, json={
                "name": "test1",
                "agent_token": "ab"*16
    })
    
    assert response.status_code == 201
        
    id = response.json()["id"]
    
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": 101,
    }
    
    response = client.post("/metrics", headers = {"X-Agent-Token": "ab"*16}, json = payload)
    
    # device_id = response.json()["device_id"]
    
    assert response.status_code == 422
    
    response = client.get(f"/devices/{id}/metrics/latest", headers = admin)
        
    assert response.status_code == 404
    # assert response.json()["id"] == id
    # assert response.json()["device_id"] == device_id
    

def test_invalid_cpu_less_0(client, admin):
    response = client.post("/devices", headers = admin, json={
                "name": "test1",
                "agent_token": "ab"*16
    })
    
    assert response.status_code == 201
    
    id = response.json()["id"]
    
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": -1
    }
    
    response = client.post("/metrics", headers = {"X-Agent-Token": "ab"*16}, json = payload)
    
    assert response.status_code == 422
    
    response = client.get(f"/devices/{id}/metrics/latest", headers = admin)
        
    assert response.status_code == 404
    
    
def test_invalid_disk(client, admin):
    response = client.post("/devices", headers = admin, json={
                "name": "test1",
                "agent_token": "ab"*16
    })
        
    assert response.status_code == 201
    
    id = response.json()["id"]
    
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "disks": [
                {
                    "name": "C://",
                    "disk_used_bytes": 40000,
                    "disk_total_bytes": 20000,
                }
            ]
    }
    
    response = client.post("/metrics", headers = {"X-Agent-Token": "ab"*16}, json = payload)
    
    assert response.status_code == 422
    
    response = client.get(f"/devices/{id}/metrics/latest", headers = admin)
        
    assert response.status_code == 404


def test_invalid_memory(client, admin):
    response = client.post("/devices", headers = admin, json={
                "name": "test1",
                "agent_token": "ab"*16
    })
        
    assert response.status_code == 201
    
    id = response.json()["id"]
    
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "memory_used_bytes": 10000,
        "memory_total_bytes": 8000
    }
    
    response = client.post("/metrics", headers = {"X-Agent-Token": "ab"*16}, json = payload)
    
    assert response.status_code == 422
    
    response = client.get(f"/devices/{id}/metrics/latest", headers = admin)
        
    assert response.status_code == 404
    

def test_correct_services_metrics(client, admin):
    response = client.post("/devices", headers = admin, json={
                "name": "test1",
                "agent_token": "ab"*16
    })
        
    assert response.status_code == 201
    
    id = response.json()["id"]
    
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "services": {
            "Spooler": "running",
            "W32Time": "stopped"
        }
    }
    
    response = client.post("/metrics", headers = {"X-Agent-Token": "ab"*16}, json = payload)
    
    assert response.status_code == 201
    
    response = client.get(f"/devices/{id}/metrics/latest", headers = admin)
    
    assert response.status_code == 200
    
    assert "Spooler" in response.json()["services"] and "W32Time" in response.json()["services"]
    
    assert response.json()["services"]["Spooler"] == "running"
    assert response.json()["services"]["W32Time"] == "stopped"
    
    
def test_metrics_to_2_devices(client, admin):
    response = client.post("/devices", headers = admin, json={
        "name": "test1",
        "agent_token": "ab"*16
    })

    device_id_a = response.json()["id"]
    
    assert response.status_code == 201
    
    response = client.post("/devices", headers = admin, json={
        "name": "test2",
        "agent_token": "ba"*16
    })
    
    device_id_b = response.json()["id"]
    
    assert response.status_code == 201
    
    payload_a = {
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "cpu_percent": 50
        }

    response = client.post("/metrics", headers={"X-Agent-Token": "ab"*16}, json=payload_a)
    
    assert response.status_code == 201 
    
    response = client.get(f"/devices/{device_id_a}/metrics/latest", headers=admin)
    
    assert response.status_code == 200 
    assert response.json()["device_id"] == device_id_a
    assert response.json()["cpu_percent"] == 50
    
    
    payload_b = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": 70
    }

    response = client.post("/metrics", headers={"X-Agent-Token": "ba"*16}, json=payload_b)
    
    assert response.status_code == 201 
    
    response = client.get(f"/devices/{device_id_b}/metrics/latest", headers=admin)
    
    assert response.status_code == 200 
    assert response.json()["device_id"] == device_id_b
    assert response.json()["cpu_percent"] == 70
    
    
def test_send_metrics_with_incorrect_agent_token(client, admin):
    response = client.post("/devices", headers = admin, json={
        "name": "test1",
        "agent_token": "ab"*16
    })
    assert response.status_code == 201
    
    payload = {
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "cpu_percent": 50
        }

    response = client.post("/metrics", headers={"X-Agent-Token": "b"*32}, json=payload)
    
    assert response.status_code == 401
    

def test_send_metrics_without_agent_token(client, admin):
    response = client.post("/devices", headers = admin, json={
        "name": "test1",
        "agent_token": "ab"*16
    })
    assert response.status_code == 201
    
    payload = {
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "cpu_percent": 50
        }

    response = client.post("/metrics", json=payload)
    
    assert response.status_code == 401