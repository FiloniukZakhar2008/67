from app.crud.base import CRUDBase
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


post = CRUDBase[Post, PostCreate, PostUpdate](Post)