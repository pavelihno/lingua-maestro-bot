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
            return model
        except Exception as e:
            print(f"Error creating {cls.__name__}: {e}")
            return None

    @classmethod
    def get_all(cls, session):
        try:
            return session.query(cls).all()
        except Exception as e:
            print(f"Error retrieving all {cls.__name__} instances: {e}")
            return []

    @classmethod
    def get_by_id(cls, _id, session):
        try:
            return session.query(cls).get(_id)
        except Exception as e:
            print(f"Error retrieving {cls.__name__} by ID: {e}")
            return None

    @classmethod
    def update(cls, _id, session, **data):
        try:
            model = cls.get_by_id(_id, session=session)
            if model:
                for key, value in data.items():
                    if value is not None:
                        setattr(model, key, value)
                return model
            return None
        except Exception as e:
            print(f"Error updating {cls.__name__}: {e}")
            return None

    @classmethod
    def delete(cls, _id, session):
        try:
            model = cls.get_by_id(_id, session=session)
            if model:
                session.delete(model)
                return model
            return None
        except Exception as e:
            print(f"Error deleting {cls.__name__}: {e}")
            return None
