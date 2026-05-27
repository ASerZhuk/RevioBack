from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    device_id: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class GoogleLogin(BaseModel):
    id_token: str
    device_id: str | None = None


class UserRead(BaseModel):
    id: int
    username: str
    email: str | None
    tokens: int
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
