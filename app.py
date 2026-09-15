from fastapi import FastAPI
from core.deal_finder import find_deals
from utils.database import load_seen

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Pedal Hunter API is running"}

@app.get("/deals")
def read_deals():
    return load_seen()

@app.get("/search")
def search(query: str):
    return find_deals(query)