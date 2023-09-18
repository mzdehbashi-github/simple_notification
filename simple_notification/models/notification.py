from sqlmodel import SQLModel, Field


class NotificationBase(SQLModel):
    text: str
    sender_id: int = Field(foreign_key='user.id')
    receiver_id: int = Field(foreign_key='user.id')
    is_read: bool = Field(default=False)


class Notification(NotificationBase, table=True):
    id: int = Field(primary_key=True, index=True)


class NotificationCreate(NotificationBase):
    pass
