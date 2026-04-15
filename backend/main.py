# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.game import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"status": "ok"}

## uvicorn main:app --reload --port 8000