from pydantic import BaseModel, ConfigDict, EmailStr


class Message(BaseModel):
    message: str


class User(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int
    model_config = ConfigDict(from_attributes=True)
    # permite o pydantic a ler nao so dicionarios
    # e sim objetos.


class UserList(BaseModel):
    users: list[UserPublic]
