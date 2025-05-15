
from fastapi import FastAPI, Request, HTTPException
from TodoApp.database import Base, engine, db_dependency
from TodoApp.models import Todo
from TodoApp.routers import auth, todos
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from TodoApp.routers.auth import user_dependency

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)
app.include_router(todos.router)

templates=Jinja2Templates(directory="TodoApp/templates")
app.mount("/static",StaticFiles(directory="TodoApp/static"),name="static")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/create")
async def create(request: Request):
    return templates.TemplateResponse("create_todo.html", {"request": request})


@app.get("/edit/{todo_id}")
async def edit(request: Request, todo_id: int, user: user_dependency, db: db_dependency):
    userid = user["id"]
    todo = db.query(Todo).filter(Todo.user_id == userid, Todo.id == todo_id).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    return templates.TemplateResponse("edit_todo.html", {"request": request, "todo": todo})



