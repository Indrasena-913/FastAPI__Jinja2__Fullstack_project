
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .main import Base


class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String,nullable=False)
    email=Column(String,unique=True)
    password=Column(String,nullable=False)
    phonenumber=Column(String,nullable=False)

    todos=relationship("Todo",back_populates="owner")


class Todo(Base):
    __tablename__="todos"
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String,nullable=False)
    desc=Column(String,nullable=False)
    priority=Column(Integer,nullable=False)
    completed=Column(Boolean, default=False)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)

    owner=relationship("User",back_populates="todos")