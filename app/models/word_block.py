from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models._base import BaseModel

class WordBlock(BaseModel):
    __tablename__ = 'word_blocks'

    id = Column(Integer, primary_key=True)
    title = Column(String(32))
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='word_blocks')
    words = relationship('Word', back_populates='word_block')
