from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class User(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserDB(User):  # agora UserDB tem todos os campos de User + o campo id
    id: int


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int


class UserList(BaseModel):
    users: list[UserPublic]
