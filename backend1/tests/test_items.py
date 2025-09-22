# tests/test_items.py
# Test cases cho items endpoints
# Kiểm tra các chức năng CRUD của items

import pytest
from fastapi.testclient import TestClient

def test_get_items(client: TestClient):
    """Test lấy danh sách items"""
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 0

def test_get_item_by_id(client: TestClient):
    """Test lấy item theo ID"""
    response = client.get("/api/v1/items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data

def test_get_item_not_found(client: TestClient):
    """Test lấy item không tồn tại"""
    response = client.get("/api/v1/items/999")
    assert response.status_code == 404
    assert "Không tìm thấy item" in response.json()["detail"]

def test_create_item(client: TestClient):
    """Test tạo item mới"""
    item_data = {
        "name": "Test Item",
        "description": "Test Description",
        "price": 150.0
    }
    response = client.post("/api/v1/items/", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]
    assert data["price"] == item_data["price"]
    assert "id" in data

def test_update_item(client: TestClient):
    """Test cập nhật item"""
    item_data = {
        "name": "Updated Item",
        "description": "Updated Description",
        "price": 250.0
    }
    response = client.put("/api/v1/items/1", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]
    assert data["price"] == item_data["price"]

def test_delete_item(client: TestClient):
    """Test xóa item"""
    response = client.delete("/api/v1/items/2")
    assert response.status_code == 200
    assert "đã được xóa thành công" in response.json()["message"]

def test_delete_item_not_found(client: TestClient):
    """Test xóa item không tồn tại"""
    response = client.delete("/api/v1/items/999")
    assert response.status_code == 404
    assert "Không tìm thấy item" in response.json()["detail"]
