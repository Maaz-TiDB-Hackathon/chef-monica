from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str

class ChatCreate(BaseModel):
    id: str
    user_id: int
    messages: list
