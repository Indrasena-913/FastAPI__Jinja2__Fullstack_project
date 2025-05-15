from fastapi import FastAPI, APIRouter, Path, HTTPException
from starlette import status

from TodoApp.database import db_dependency
from TodoApp.models import Todo
from TodoApp.routers.auth import user_dependency
from TodoApp.schema import CreateTodoStruct

router=APIRouter()


@router.post("/todos/create-todo",status_code=status.HTTP_201_CREATED)
async def create_new_todo(new_todo:CreateTodoStruct,user:user_dependency,db:db_dependency):
    userid=user["id"]
    todo=Todo(
        title=new_todo.title,
        desc=new_todo.desc,
        priority=new_todo.priority,
        completed=new_todo.completed,
        user_id=userid
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@router.get("/todos",status_code=status.HTTP_200_OK)
async def get_all_todos(user:user_dependency,db:db_dependency):
    userid=user["id"]
    all_todos=db.query(Todo).filter(Todo.user_id==userid).all()
    return all_todos

@router.get("/todos/{todo_id}",status_code=status.HTTP_200_OK)
async def get_all_todos(user:user_dependency,db:db_dependency,todo_id:int=Path(gt=0)):
    userid=user["id"]
    todo=db.query(Todo).filter(Todo.user_id==userid,Todo.id==todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.put("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(
    updated_todo: CreateTodoStruct,
    user: user_dependency,
    db: db_dependency ,
    todo_id: int = Path(gt=0)
):
    userid = user["id"]
    todo = db.query(Todo).filter(Todo.user_id == userid, Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo.title = updated_todo.title
    todo.desc = updated_todo.desc
    todo.priority = updated_todo.priority
    todo.completed = updated_todo.completed

    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency ,
    db: db_dependency ,
    todo_id: int = Path(gt=0),
):
    userid = user["id"]
    todo = db.query(Todo).filter(Todo.user_id == userid, Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()
    return None

