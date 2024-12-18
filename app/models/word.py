from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models._base import BaseModel

class Word(BaseModel):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    word = Column(String(50))
    translate = Column(String(50))
    word_block_id = Column(Integer, ForeignKey('word_blocks.id'))

    word_block = relationship('WordBlock', back_populates='words')

    @classmethod
    def get_all_by_block_id(cls, session, block_id):
        return session.query(cls).filter(cls.word_block_id == block_id).all()
