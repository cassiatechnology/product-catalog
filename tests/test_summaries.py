import pytest

@pytest.mark.asyncio
async def test_summaries_and_cache_invalidation(async_client):
    # Seed minimal structure
    men = (await async_client.post("/departments/", json={"name": "Men"})).json()
    women = (await async_client.post("/departments/", json={"name": "Women"})).json()

    cat_m_shirt = (await async_client.post("/categories/", json={"name": "Shirt", "department_id": men["id"]})).json()
    cat_w_blouse = (await async_client.post("/categories/", json={"name": "Blouse", "department_id": women["id"]})).json()

    # Create two products (one in each department)
    p1 = {
        "name": "Men Tee",
        "description": "Basic tee",
        "price": 50.0,
        "stock": 10,
        "category_id": cat_m_shirt["id"],
    }
    p2 = {
        "name": "Women Blouse",
        "description": "Silk blouse",
        "price": 120.0,
        "stock": 5,
        "category_id": cat_w_blouse["id"],
    }
    r1 = await async_client.post("/products/", json=p1); assert r1.status_code == 201
    r2 = await async_client.post("/products/", json=p2); assert r2.status_code == 201

    # First read - builds cache
    resp = await async_client.get("/products/summary/count-by-department")
    assert resp.status_code == 200
    data1 = resp.json()
    # normalize to dict {dept_id: count}
    counts1 = {row["department_id"]: row["product_count"] for row in data1}
    assert counts1.get(men["id"], 0) >= 1
    assert counts1.get(women["id"], 0) >= 1

    # Create another product in "Men" dept -> should invalidate summaries cache automatically
    p3 = {
        "name": "Men Oxford",
        "description": "Oxford shirt",
        "price": 140.0,
        "stock": 2,
        "category_id": cat_m_shirt["id"],
    }
    r3 = await async_client.post("/products/", json=p3)
    assert r3.status_code == 201

    # Read again - cache was invalidated on POST -> counts must reflect new total
    resp = await async_client.get("/products/summary/count-by-department")
    assert resp.status_code == 200
    data2 = resp.json()
    counts2 = {row["department_id"]: row["product_count"] for row in data2}

    assert counts2[men["id"]] == counts1.get(men["id"], 0) + 1
