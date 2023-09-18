from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    username: str


class User(UserBase, table=True):
    id: int = Field(primary_key=True, index=True)
    hashed_password: str


class UserCreate(UserBase):
    raw_password: str
