from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    email: str


class User(UserBase, table=True):
    id: int = Field(primary_key=True, index=True)


class UserCreate(UserBase):
    pass


class NotificationBase(SQLModel):
    text: str
    user_id: int = Field(foreign_key='user.id')
    is_read: bool = Field(default=False)
    is_published: bool = Field(default=False)


class Notification(NotificationBase, table=True):
    id: int = Field(primary_key=True, index=True)


class NotificationCreate(NotificationBase):
    pass
