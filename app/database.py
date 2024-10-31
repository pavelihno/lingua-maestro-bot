import os

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = os.getenv('DB_URL')

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)

def init_db():
    from models.language import Language
    from models.user import User
    from models.word_block import WordBlock
    from models.word import Word
    from models.access_request import AccessRequest

    # important
    import_order = [
        Language,
        User,
        WordBlock,
        Word,
        AccessRequest
    ]

    for model in import_order:
        model.metadata.create_all(engine)

@contextmanager
def get_db_session():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
