import json

from sqlalchemy import create_engine, MetaData, Engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional

Base = declarative_base()

class SQLDatabase:
    """
    A class for managing database connections and sessions using SQLAlchemy.
    """
    _engine: Optional[Engine] = None
    _metadata: Optional[MetaData] = None
    _Session: Optional[scoped_session] = None

    def __init__(self, db_url: str) -> None:
        """
        Initializes the database connection and session.

        :param db_url: The database URL for the connection.
        """
        if not SQLDatabase._engine:
            SQLDatabase._engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_recycle=600,
                json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False)
            )
            SQLDatabase._metadata = MetaData()
            SQLDatabase._Session = scoped_session(sessionmaker(bind=SQLDatabase._engine))
    
    @classmethod
    def get_session(cls) -> Session:
        """
        Returns a session for database operations.

        :return: A SQLAlchemy session object.
        """
        return cls._Session()
    
    @classmethod
    def _ensure_session_started(cls) -> bool:
        """
        Ensures that a session has been started before committing or closing.
        
        :return: True if a session is active, False otherwise.
        """
        if cls._Session is None or not cls._Session.registry.has():
            return False
        return True
    
    @classmethod
    def commit(cls) -> None:
        """
        Commits the current transaction in the session.
        """
        if cls._ensure_session_started():
            cls._Session().commit()
    
    @classmethod
    def rollback(cls) -> None:
        """
        Rolls back the current transaction in the session.
        """
        if cls._ensure_session_started():
            cls._Session().rollback()
        
    @classmethod
    def close(cls) -> None:
        """
        Closes the session.
        """
        if cls._ensure_session_started():
            cls._Session().close()