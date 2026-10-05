def test_health_is_ok(client):
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    

def test_database_is_ok(client):
    response = client.get("/health/database")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    