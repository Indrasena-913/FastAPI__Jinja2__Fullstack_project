from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Database_url="sqlite:///./todos.db"
engine=create_engine(Database_url,connect_args={"check_same_thread":False})
SessionLocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)
Base=declarative_base()

Base.metadata.create_all(bind=engine)


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]