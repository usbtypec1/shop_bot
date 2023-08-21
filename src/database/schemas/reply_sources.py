import enum

__all__ = ('ReplySource',)


class ReplySource(enum.Enum):
    USER = 'User'
    ADMIN = 'Admin'
