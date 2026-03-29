from dotenv import load_dotenv
import os

load_dotenv()
from fastapi import FastAPI
from api.routes import router
from config.database import engine
from models.db_models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router)

@app.get("/")
def home():
    return {"message": "Server running"}