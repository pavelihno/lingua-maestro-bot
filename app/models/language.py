from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from models._base import BaseModel

class Language(BaseModel):
    __tablename__ = 'languages'

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    code = Column(String(10))

    users = relationship('User', back_populates='language')
    words = relationship('Word', back_populates='word_block')
