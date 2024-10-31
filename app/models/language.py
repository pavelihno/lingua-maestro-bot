from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from models._base import BaseModel

class Language(BaseModel):
    __tablename__ = 'languages'

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    code = Column(String(10), unique=True)

    users = relationship('User', back_populates='language')

    @classmethod
    def get_by_code(cls, language_code, session):
        return session.query(cls).filter(cls.code == language_code).first()
