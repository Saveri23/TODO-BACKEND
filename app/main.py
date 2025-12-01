from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import hashlib

app = FastAPI()

# Allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
users_db = {}
todos_db = {}

# ===== MODELS =====
class SignupRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TodoCreate(BaseModel):
    title: str

class Todo(BaseModel):
    id: int
    title: str
    completed: bool

# ===== UTILS =====
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ===== ENDPOINTS =====

@app.post("/signup")
def signup(data: SignupRequest):
    if data.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    users_db[data.username] = {
        "username": data.username,
        "password": hash_password(data.password)
    }
    todos_db[data.username] = []

    return {"message": "Signup successful"}


@app.post("/login")
def login(data: LoginRequest):
    user = users_db.get(data.username)
    if not user or user["password"] != hash_password(data.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "username": data.username
    }


@app.get("/todos", response_model=List[Todo])
def get_todos(username: str):
    if username not in todos_db:
        raise HTTPException(status_code=404, detail="User not found")
    return todos_db[username]


@app.post("/todos", response_model=Todo)
def create_todo(data: TodoCreate, username: str):
    if username not in todos_db:
        raise HTTPException(status_code=404, detail="User not found")

    new_id = len(todos_db[username]) + 1
    todo = {"id": new_id, "title": data.title, "completed": False}
    todos_db[username].append(todo)
    return todo


@app.post("/todos/{todo_id}/complete", response_model=Todo)
def complete_todo(todo_id: int, username: str):
    if username not in todos_db:
        raise HTTPException(status_code=404, detail="User not found")

    for todo in todos_db[username]:
        if todo["id"] == todo_id:
            todo["completed"] = True
            return todo

    raise HTTPException(status_code=404, detail="Todo not found")
