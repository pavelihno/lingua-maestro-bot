from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from models._base import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    is_active = Column(Boolean)
    is_superuser = Column(Boolean)
    language_id = Column(Integer, ForeignKey('languages.id'))

    language = relationship('Language', back_populates='users')
    word_blocks = relationship('WordBlock', back_populates='user')
    access_requests = relationship('AccessRequest', back_populates='approved_by')
