import pytest


pytestmark = pytest.mark.asyncio


async def create_user(client, email="user@example.com", password="secret123"):
    response = await client.post(
        "/api/v1/users/",
        json={"name": "Test User", "email": email, "password": password, "age": 20},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def login(client, email="user@example.com", password="secret123"):
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response


async def create_category(client, name="Books"):
    response = await client.post(
        "/api/v1/products/categories/",
        json={"name": name, "description": "Readable things"},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_product(client, category_name="Product Category"):
    category = await create_category(client, category_name)
    response = await client.post(
        "/api/v1/products/",
        json={
            "name": "Clean Architecture",
            "description": "Book",
            "price": "25.50",
            "stock": 7,
            "category_id": category["id"],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_read_root(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Async Shop API"}


async def test_auth_register_login_me_and_logout(client):
    register = await client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "secret123", "age": 31},
    )
    assert register.status_code == 201, register.text
    assert register.json()["email"] == "alice@example.com"
    assert "access_token" in register.cookies

    duplicate = await client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "secret123", "age": 31},
    )
    assert duplicate.status_code == 400

    me = await client.get("/api/v1/auth/me")
    assert me.status_code == 200, me.text
    assert me.json()["email"] == "alice@example.com"

    logout = await client.post("/api/v1/auth/logout")
    assert logout.status_code == 200
    assert logout.json() == {"message": "Logged out"}

    bad_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "wrong-password"},
    )
    assert bad_login.status_code == 401

    good_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    assert good_login.status_code == 200
    assert good_login.json() == {"message": "Logged in successfully"}


async def test_users_crud_and_current_user_routes(client):
    user = await create_user(client)

    duplicate = await client.post(
        "/api/v1/users/",
        json={"name": "Copy", "email": user["email"], "password": "secret123", "age": 18},
    )
    assert duplicate.status_code == 400

    users = await client.get("/api/v1/users/")
    assert users.status_code == 200
    assert [item["email"] for item in users.json()] == [user["email"]]

    fetched = await client.get(f"/api/v1/users/{user['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == user["id"]

    missing = await client.get("/api/v1/users/999")
    assert missing.status_code == 404

    patched = await client.patch(f"/api/v1/users/{user['id']}", json={"name": "Updated User"})
    assert patched.status_code == 200
    assert patched.json()["name"] == "Updated User"

    await login(client)
    current = await client.get("/api/v1/users/me")
    assert current.status_code == 200
    assert current.json()["email"] == user["email"]

    patched_current = await client.patch("/api/v1/users/me", json={"age": 33})
    assert patched_current.status_code == 200
    assert patched_current.json()["age"] == 33

    deleted = await client.delete(f"/api/v1/users/{user['id']}")
    assert deleted.status_code == 204

    deleted_again = await client.delete(f"/api/v1/users/{user['id']}")
    assert deleted_again.status_code == 404


async def test_profile_routes(client):
    user = await create_user(client)

    created = await client.post(
        "/api/v1/users/profiles/",
        json={"bio": "Backend student", "phone": "+380001112233", "user_id": user["id"]},
    )
    assert created.status_code == 201, created.text
    profile = created.json()

    listed = await client.get("/api/v1/users/profiles/")
    assert listed.status_code == 200
    assert listed.json()[0]["user_id"] == user["id"]

    patched = await client.patch(f"/api/v1/users/profiles/{profile['id']}", json={"bio": "Updated bio"})
    assert patched.status_code == 200
    assert patched.json()["bio"] == "Updated bio"

    missing = await client.patch("/api/v1/users/profiles/999", json={"bio": "Nobody"})
    assert missing.status_code == 404


async def test_posts_routes(client):
    user = await create_user(client)

    created = await client.post(
        "/api/v1/posts/",
        json={"title": "First post", "content": "Hello", "author_id": user["id"]},
    )
    assert created.status_code == 201, created.text
    post = created.json()

    listed = await client.get("/api/v1/posts/")
    assert listed.status_code == 200
    assert listed.json()[0]["title"] == "First post"

    fetched = await client.get(f"/api/v1/posts/{post['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == post["id"]

    missing = await client.get("/api/v1/posts/999")
    assert missing.status_code == 404

    patched = await client.patch(f"/api/v1/posts/{post['id']}", json={"title": "Updated post"})
    assert patched.status_code == 200
    assert patched.json()["title"] == "Updated post"

    missing_patch = await client.patch("/api/v1/posts/999", json={"title": "Nobody"})
    assert missing_patch.status_code == 404

    deleted = await client.delete(f"/api/v1/posts/{post['id']}")
    assert deleted.status_code == 204

    deleted_again = await client.delete(f"/api/v1/posts/{post['id']}")
    assert deleted_again.status_code == 404


async def test_product_category_order_and_review_routes(client):
    user = await create_user(client)
    category = await create_category(client)

    categories = await client.get("/api/v1/products/categories/")
    assert categories.status_code == 200
    assert categories.json()[0]["name"] == "Books"

    patched_category = await client.patch(
        f"/api/v1/products/categories/{category['id']}",
        json={"description": "Updated category"},
    )
    assert patched_category.status_code == 200
    assert patched_category.json()["description"] == "Updated category"

    missing_category = await client.patch("/api/v1/products/categories/999", json={"name": "Missing"})
    assert missing_category.status_code == 404

    product_response = await client.post(
        "/api/v1/products/",
        json={
            "name": "Keyboard",
            "description": "Mechanical",
            "price": "99.99",
            "stock": 4,
            "category_id": category["id"],
        },
    )
    assert product_response.status_code == 201, product_response.text
    product = product_response.json()

    products = await client.get("/api/v1/products/")
    assert products.status_code == 200
    assert products.json()[0]["name"] == "Keyboard"

    fetched = await client.get(f"/api/v1/products/{product['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == product["id"]

    missing_product = await client.get("/api/v1/products/999")
    assert missing_product.status_code == 404

    patched_product = await client.patch(f"/api/v1/products/{product['id']}", json={"stock": 9})
    assert patched_product.status_code == 200
    assert patched_product.json()["stock"] == 9

    missing_patch = await client.patch("/api/v1/products/999", json={"stock": 1})
    assert missing_patch.status_code == 404

    deleted = await client.delete(f"/api/v1/products/{product['id']}")
    assert deleted.status_code == 204

    deleted_again = await client.delete(f"/api/v1/products/{product['id']}")
    assert deleted_again.status_code == 404

    order_product = await create_product(client, "Order Category")

    order_response = await client.post(
        "/api/v1/products/orders/",
        json={"user_id": user["id"], "status": "new", "items": [{"product_id": order_product["id"], "quantity": 2}]},
    )
    assert order_response.status_code == 201, order_response.text
    assert order_response.json()["items"][0]["quantity"] == 2

    orders = await client.get("/api/v1/products/orders/")
    assert orders.status_code == 200
    assert orders.json()[0]["items"][0]["product_id"] == order_product["id"]

    review_product = await create_product(client, "Review Category")

    review_response = await client.post(
        "/api/v1/products/reviews/",
        json={"rating": 5, "comment": "Great", "user_id": user["id"], "product_id": review_product["id"]},
    )
    assert review_response.status_code == 201, review_response.text

    reviews = await client.get("/api/v1/products/reviews/")
    assert reviews.status_code == 200
    assert reviews.json()[0]["rating"] == 5

    metrics = await client.get("/metrics")
    assert metrics.status_code == 200
    assert "shop_orders_created_total" in metrics.text
    assert "shop_purchases_total_price_total" in metrics.text
