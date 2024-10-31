from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from models._base import BaseModel

class AccessRequest(BaseModel):
    __tablename__ = 'access_requests'

    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', foreign_keys=[user_id], back_populates='access_requests')

    @classmethod
    def get_active_requests(cls, session):
        return session.query(cls).filter(cls.is_active).all()

    @classmethod
    def get_active_user_request(cls, user_id, session):
        return session.query(cls).filter((cls.user_id == user_id) & (cls.is_active)).first()