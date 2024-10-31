from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from models._base import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(32), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_superuser = Column(Boolean, nullable=False, default=False)
    language_id = Column(Integer, ForeignKey('languages.id'), nullable=True)

    language = relationship('Language', back_populates='users')
    word_blocks = relationship('WordBlock', back_populates='user')
    access_requests = relationship('AccessRequest', back_populates='user')

    @classmethod
    def get_by_telegram_id(cls, telegram_id, session):
        return session.query(cls).filter(cls.telegram_id == telegram_id).first()
    
    @classmethod
    def get_default_language_code(cls):
        return 'en'

    def get_language_code(self):
        language = self.language
        if not language:
            return self.__class__.get_default_language_code()
        return language.code
