from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models._base import BaseModel

class AccessRequest(BaseModel):
    __tablename__ = 'access_requests'

    id = Column(Integer, primary_key=True)
    is_approved = Column(String(32))
    approved_by_id = Column(Integer, ForeignKey('users.id'))
    grant_to_id = Column(Integer, ForeignKey('users.id'))

    approved_by = relationship('User', foreign_keys=[approved_by_id], back_populates='access_requests')
    grant_to = relationship('User', foreign_keys=[grant_to_id])
