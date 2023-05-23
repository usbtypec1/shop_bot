from sqlalchemy import Column, Integer, TIMESTAMP, func
from sqlalchemy.orm import declarative_base

__all__ = ('Base', 'BaseModel',)

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.current_timestamp())

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id})"
