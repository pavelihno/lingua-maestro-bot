import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = os.getenv('DB_URL')

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)

def init_db():
    """
    Initialize the database by creating all tables.
    """
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

def get_db_session():
    """
    Get a new database session.
    """
    return Session()
