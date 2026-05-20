from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr
    age: int | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    age: int | None = None


class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


UserResponse = UserRead


class ProfileBase(BaseModel):
    bio: str | None = None
    phone: str | None = None
    user_id: int


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    bio: str | None = None
    phone: str | None = None


class ProfileRead(ProfileBase):
    id: int

    model_config = ConfigDict(from_attributes=True)