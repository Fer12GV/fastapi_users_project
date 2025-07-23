import pytest
from httpx import AsyncClient
from app.schemas.user_schema import UserCreate

class TestUserAPI:
    
    async def test_register_user(self, client: AsyncClient):
        """Test user registration"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = await client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data
    
    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test registration with duplicate email"""
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "password123"
        }
        
        # First registration
        await client.post("/api/v1/users/register", json=user_data)
        
        # Second registration with same email
        user_data["username"] = "user2"
        response = await client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == 400
    
    async def test_login_user(self, client: AsyncClient):
        """Test user login"""
        # Register user first
        user_data = {
            "email": "login@example.com",
            "username": "loginuser",
            "password": "loginpassword123"
        }
        await client.post("/api/v1/users/register", json=user_data)
        
        # Login
        login_data = {
            "email": "login@example.com",
            "password": "loginpassword123"
        }
        response = await client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = await client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 401
    
    async def test_get_current_user(self, client: AsyncClient, auth_headers):
        """Test getting current user info"""
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "email" in data
        assert "username" in data
        assert "id" in data
    
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without authentication"""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401
    
    async def test_get_users(self, client: AsyncClient, auth_headers):
        """Test getting all users"""
        response = await client.get("/api/v1/users/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    async def test_update_user(self, client: AsyncClient, auth_headers, test_user_id):
        """Test updating user"""
        update_data = {
            "username": "updateduser"
        }
        response = await client.put(f"/api/v1/users/{test_user_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == "updateduser"
    
    async def test_delete_user(self, client: AsyncClient, auth_headers, test_user_id):
        """Test deleting user"""
        response = await client.delete(f"/api/v1/users/{test_user_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify user is deleted
        response = await client.get(f"/api/v1/users/{test_user_id}", headers=auth_headers)
        assert response.status_code == 404
    
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint"""
        response = await client.get("/")
        assert response.status_code == 200
        assert "FastAPI Users API is running!" in response.json()["message"]
    
    async def test_get_users_unauthorized(self, client: AsyncClient):
        """Test getting users without authentication"""
        response = await client.get("/api/v1/users/")
        assert response.status_code == 403
