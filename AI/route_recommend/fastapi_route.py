from fastapi import FastAPI
from cluster_inference import assign_and_find_similar_gower, find_route
from pydantic import BaseModel

"""
example_user = {
    "GENDER": "남",
    "AGE_GRP": 30,
    "MARR_STTS": 1,
    "JOB_NM": 3,
    "INCOME": 4,
    "TRAVEL_STYL_1": 2,
    "TRAVEL_STATUS_RESIDENCE": "서울특별자치도",
    "TRAVEL_STATUS_ACCOMPANY": "2인 여행(가족 외)",
    "TRAVEL_MOTIVE_1": 7,
    "TRAVEL_NUM": 3,
    "TRAVEL_COMPANIONS_NUM": 1,
    "MONTH": 8,
    "SEASON": "summer",
    "HOW_LONG": 3,
}
"""

app = FastAPI()


class PredictRequest(BaseModel):
    GENDER: str
    AGE_GRP: int
    MARR_STTS: int
    JOB_NM: int
    INCOME: int
    TRAVEL_STYL_1: int
    TRAVEL_STATUS_RESIDENCE: str
    TRAVEL_STATUS_ACCOMPANY: str
    TRAVEL_MOTIVE_1: int
    TRAVEL_NUM: int
    TRAVEL_COMPANIONS_NUM: int
    MONTH: int
    SEASON: str
    HOW_LONG: int


# ------------------
# 엔드포인트
# ------------------
@app.post("/route_rec_ai")
def predict(req: PredictRequest):
    top_users = assign_and_find_similar_gower(req.dict())
    result = find_route(top_users)
    return {"result": result}
