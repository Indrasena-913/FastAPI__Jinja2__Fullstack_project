from datetime import timedelta, datetime, UTC
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from starlette.staticfiles import StaticFiles

from ..database import db_dependency
from ..models import User
from ..schema import RegisterUserStruct, LoginUserStruct
from passlib.context import CryptContext
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
load_dotenv()
app=FastAPI()

router=APIRouter()

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRES_IN = int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", 15))
REFRESH_TOKEN_EXPIRES_IN = int(os.getenv("REFRESH_TOKEN_EXPIRES_IN", 7))



pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_the_password(userdata):
    hash_password=pwd_context.hash(userdata.password)
    return hash_password

def verify_the_password(given_password,user_password):
    return pwd_context.verify(given_password,user_password)


def create_access_token(userdata:dict,expires_minutes:int | None =ACCESS_TOKEN_EXPIRES_IN):
    to_encode=userdata.copy()
    expire= datetime.now(UTC) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp":expire})
    access_token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return access_token

def create_refresh_token(userdata:dict,expires_day : int | None = REFRESH_TOKEN_EXPIRES_IN):
    to_encode = userdata.copy()
    expire = datetime.now(UTC) + timedelta( days=expires_day)
    to_encode.update({"exp": expire})
    refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return refresh_token

def get_current_user(req:Request):
    token=req.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=404,detail="Token missing")
    bearer,token=token.split(" ")
    if bearer.lower()!="bearer":
        raise HTTPException(status_code=401,detail="Invalid token type")
    payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
    return payload


user_dependency=Annotated[dict,Depends(get_current_user)]


templates=Jinja2Templates(directory="TodoApp/templates")


@router.get("/login")
def test(req:Request):
    return templates.TemplateResponse("login.html",{"request":req})

@router.get("/register")
def test(req:Request):
    return templates.TemplateResponse("register.html",{"request":req})




@router.post("/auth/register",status_code=status.HTTP_201_CREATED)
async def register_user(userdata:RegisterUserStruct,db:db_dependency):
    existing_user = db.query(User).filter(User.email == userdata.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password=hash_the_password(userdata)
    new_user=User(
        name=userdata.name,
        email=userdata.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/auth/login",status_code=status.HTTP_201_CREATED)
async def login_user(userdata:LoginUserStruct,db:db_dependency,req:Request,res:Response):
    user=db.query(User).filter(User.email==userdata.email).first()
    if user is None:
        raise HTTPException(status_code=404,detail="User not found")
    user_password=user.password

    isMatching=verify_the_password(userdata.password,user_password)

    if isMatching:
        access_token=create_access_token({"sub":user.name,"id":user.id,"email":user.email},expires_minutes=ACCESS_TOKEN_EXPIRES_IN)
        refresh_token=create_refresh_token({"sub":user.name,"id":user.id,"email":user.email},expires_day=REFRESH_TOKEN_EXPIRES_IN)
        res.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=REFRESH_TOKEN_EXPIRES_IN * 24 * 60 * 60
        )
        return {
            "access_token":access_token,
            "refresh_token":refresh_token,
            "token_type":"bearer"
        }
    else:
        raise HTTPException(status_code=401,detail="Invalid credentials")





@router.get("/auth/refresh",status_code=status.HTTP_201_CREATED)
async def refresh_token_route(req:Request,res:Response):
    refresh_token=req.cookies.get("refresh_token")
    if refresh_token is None:
        raise HTTPException(status_code=404,detail="No refresh token found")

    try:
        payload=jwt.decode(refresh_token,SECRET_KEY,algorithms=ALGORITHM)
        user_data={"sub":payload["sub"],"id":payload["id"],"email":payload["email"]}

        new_access_token=create_access_token(user_data,expires_minutes=ACCESS_TOKEN_EXPIRES_IN)
        new_refresh_token=create_refresh_token(user_data,expires_day=REFRESH_TOKEN_EXPIRES_IN)
        res.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=REFRESH_TOKEN_EXPIRES_IN * 24 * 60 * 60
        )
        return {
            "access_token":new_access_token,
            "token_type":"bearer"
        }
    except JWTError:
        raise HTTPException(status_code=401,detail="refresh token is valid or expired")







