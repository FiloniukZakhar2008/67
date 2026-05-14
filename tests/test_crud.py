from crud import create_user

def test_create_user(db_session):
    user_data = {"email": "test@example.com", "password": "password123"}
    user = create_user(db_session, user_data)

    assert user.id is not None
    assert user.email == "test@example.com"