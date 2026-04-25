from pydantic import BaseModel


class UserLogin(BaseModel):
    login: str
    password: str


class UserCreate(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
