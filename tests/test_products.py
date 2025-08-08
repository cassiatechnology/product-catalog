import pytest

@pytest.mark.asyncio
async def test_create_department_category_and_product(async_client):
    # Create departments
    resp = await async_client.post("/departments/", json={"name": "Men"})
    assert resp.status_code == 201
    men = resp.json()

    resp = await async_client.post("/departments/", json={"name": "Women"})
    assert resp.status_code == 201
    women = resp.json()

    # Create categories
    resp = await async_client.post("/categories/", json={"name": "Shirt", "department_id": men["id"]})
    assert resp.status_code == 201
    cat_shirt = resp.json()

    resp = await async_client.post("/categories/", json={"name": "Blouse", "department_id": women["id"]})
    assert resp.status_code == 201
    cat_blouse = resp.json()

    # Create product (valid category_id)
    payload = {
        "name": "Oxford White Shirt",
        "description": "Men's oxford shirt",
        "price": 149.90,
        "stock": 20,
        "category_id": cat_shirt["id"],
    }
    resp = await async_client.post("/products/", json=payload)
    assert resp.status_code == 201, resp.text
    product = resp.json()
    assert product["name"] == payload["name"]
    assert product["category"]["id"] == cat_shirt["id"]
    assert product["category"]["department"]["id"] == men["id"]

    # Get by id (should load relationships)
    resp = await async_client.get(f"/products/{product['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == product["id"]
    assert data["category"]["department"]["name"] == "Men"

    # Update product (change stock)
    update = {"stock": 33}
    resp = await async_client.put(f"/products/{product['id']}", json=update)
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["stock"] == 33

    # List with filter by department_id
    resp = await async_client.get("/products", params={"department_id": men["id"]})
    assert resp.status_code == 200
    items = resp.json()
    assert any(p["id"] == product["id"] for p in items)

@pytest.mark.asyncio
async def test_create_product_invalid_category(async_client):
    # Creating a product with non-existing category must return 400
    payload = {
        "name": "Invalid Cat Product",
        "description": "Should fail",
        "price": 10.0,
        "stock": 1,
        "category_id": 999999,
    }
    resp = await async_client.post("/products/", json=payload)
    assert resp.status_code == 400
    assert "category" in resp.text or "category_id" in resp.text
