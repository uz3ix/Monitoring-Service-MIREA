def test_without_auth(client):
    response = client.get("/devices")
    
    assert response.status_code == 401


def test_auth_with_wrong_password(client):
    response = client.post("/auth/login", json = {
        "username": "admin",
        "password": "wrong-password"
    })
    
    assert response.status_code == 401
    assert "access_token" not in response.json()
    

def test_auth_with_right_password(client):
    response = client.post("/auth/login", json = {
        "username": "admin",
        "password": "testing-admin-password"
    })
    data = response.json()    
    
    assert response.status_code == 200
    assert data["token_type"] == "bearer"
    assert data["access_token"] != ""
    
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }
    me_response = client.get("/auth/me", headers=headers)
    
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "admin"
    
    
def test_logout_system(client, admin):
    response = client.get("/auth/me", headers=admin)
        
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
    
    response = client.post("/auth/logout", headers=admin)
    
    assert response.status_code == 204
    assert response.content == b""
    
    response = client.get("/auth/me", headers=admin)
            
    assert response.status_code == 401
    
    
