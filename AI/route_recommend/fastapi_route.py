from fastapi import FastAPI
from contextlib import asynccontextmanager
from model import TravelModel
from functools import lru_cache

@lru_cache
def get_model():
    return TravelModel()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔥 startup
    app.state.model = TravelModel()
    yield
    # 🔻 shutdown (필요 시 자원 해제)
    del app.state.model

app = FastAPI(lifespan=lifespan)

@app.post("/predict")
def predict(data: list[int]):
    model = app.state.model
    return {"result": model.predict(data)}