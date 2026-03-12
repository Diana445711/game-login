from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()


# Allow Unity / WebGL access

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing only, will be replaced with URL after itch.io
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model

class User(BaseModel):
    username: str
    password: str


# Connect to Postgres

DATABASE_URL = os.getenv("DATABASE_URL")  # Set automatically by Render

conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
cursor = conn.cursor()


# Create users table if it doesn't exist

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
""")
conn.commit()


# Register endpoint

@app.post("/register")
def register(user: User):
    username = user.username.strip()
    password = user.password.strip()

    print(f"Register attempt: {repr(username)}, {repr(password)}")

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        print("Username already exists in DB")
        return {"status": "username_taken"}

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, password)
    )
    conn.commit()
    print("Account successfully created")
    return {"status": "account_created"}


# Login endpoint

@app.post("/login")
def login(user: User):
    username = user.username.strip()
    password = user.password.strip()

    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    if cursor.fetchone():
        print("Login successful")
        return {"status": "success"}

    print("Login failed")
    return {"status": "invalid"}


# root endpoint to check service

@app.get("/")
def root():
    return {"message": "Backend is running!"}