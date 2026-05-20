from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    title: str
    content: str
    author_id: int


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class PostRead(PostBase):
    id: int

    model_config = ConfigDict(from_attributes=True)