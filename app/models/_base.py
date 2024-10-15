from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    @classmethod
    def create(cls, session, **data):
        try:
            model = cls()
            for key, value in data.items():
                setattr(model, key, value)
            session.add(model)
            session.commit()
            return model
        except Exception:
            return None

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def get_by_id(cls, session, _id):
        return session.query(cls).get(_id)

    @classmethod
    def update(cls, session, _id, **data):
        try:
            model = cls.get_by_id(session, _id)
            if model:
                for key, value in data.items():
                    if value:
                        setattr(model, key, value)
                session.commit()
                return model
            return None
        except Exception:
            return None

    @classmethod
    def delete(cls, session, _id):
        model = cls.get_by_id(session, _id)
        if model:
            session.delete(model)
            session.commit()
            return model
        return None
