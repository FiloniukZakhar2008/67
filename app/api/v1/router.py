from fastapi import APIRouter
from app.api.v1.endpoints import users, posts, products # імпортуй нові модулі

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(products.router, prefix="/products", tags=["products"])