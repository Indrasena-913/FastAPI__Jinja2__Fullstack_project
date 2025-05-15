from pydantic import BaseModel, Field


class RegisterUserStruct(BaseModel):
    name:str=Field(min_length=3)
    email:str=Field(min_length=10)
    password:str=Field(min_length=6)


class LoginUserStruct(BaseModel):
    email:str
    password:str



class CreateTodoStruct(BaseModel):
    title:str=Field(min_length=6)
    desc:str=Field(min_length=10)
    priority:int=Field(gt=0,lt=6)
    completed:bool


