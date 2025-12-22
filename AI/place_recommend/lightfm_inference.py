import pandas as pd
import numpy as np
from pathlib import Path
from scipy.sparse import load_npz, csr_matrix
import pickle
import json
from utils import trace_error, replace_nan

BASE_DIR = Path().resolve().parent.parent
save_path = BASE_DIR / "AI" / "place_recommend" / "model"


# 1) LightFM 모델 로드
with open(save_path / "lightfm_model.pkl", "rb") as f:
    model = pickle.load(f)

# 2) item_features_matrix 로드
item_features_matrix = load_npz(save_path / "item_features_matrix.npz")

# 3) item 메타데이터 로드
item_meta = pd.read_csv(save_path / "item_meta.csv")

# 4) user feature 컬럼 순서 로드
with open(save_path / "user_feature_cols.json", "r", encoding="utf-8") as f:
    USER_FEATURE_COLS = json.load(f)

# 5) VISIT_AREA_NM -> item_id 매핑 로드
with open(save_path / "name_to_item_id.pkl", "rb") as f:
    name_to_item_id = pickle.load(f)


# 학습 때 사용했던 prefix 규칙 그대로
USER_PREFIX_MAP = {
    "GENDER": "gender",
    "AGE_GRP": "age_grp",
    "MARR_STTS": "marr_stts",
    "JOB_NM": "job_nm",
    "INCOME": "income",
    "TRAVEL_NUM": "travel_num",
    "TRAVEL_STYL_1": "travel_styl_1",
    "TRAVEL_STATUS_RESIDENCE": "travel_status_residence",
    "TRAVEL_STATUS_DESTINATION": "travel_status_destination",
    "TRAVEL_STATUS_ACCOMPANY": "travel_status_accompany",
    "TRAVEL_MOTIVE_1": "travel_motive_1",
    "TRAVEL_COMPANIONS_NUM": "travel_companions_num",
    "MONTH": "month",
    "SEASON": "season",
    "HOW_LONG": "how_long",
}


@trace_error
def build_new_user_features(new_user: dict) -> csr_matrix:
    """
    new_user = {
      "GENDER": "...",
      "AGE_GRP": "...",
      ...
      "HOW_LONG": ...
    }
    """
    row = np.zeros((1, len(USER_FEATURE_COLS)), dtype=np.float32)

    col_index = {col: idx for idx, col in enumerate(USER_FEATURE_COLS)}

    for field, prefix in USER_PREFIX_MAP.items():
        if field not in new_user:
            continue
        val = new_user[field]
        if pd.isna(val):
            continue

        col_name = f"{prefix}_{val}"
        if col_name in col_index:
            row[0, col_index[col_name]] = 1.0

    return csr_matrix(row)


@trace_error
def recommend_for_new_jeju_user(new_user: dict, topn: int = 5):
    # 1) 새 유저 feature 벡터 (user_id=0 가정)
    new_user_features = build_new_user_features(new_user)

    # 2) 제주 아이템만 필터 (item_meta 기준)
    jeju_items = item_meta[item_meta["SIDO"] == "제주특별자치도"].copy()
    candidate_item_ids = jeju_items["item_id"].values

    # 3) LightFM 점수 예측
    scores = model.predict(
        user_ids=0,
        item_ids=candidate_item_ids,
        user_features=new_user_features,
        item_features=item_features_matrix,
        num_threads=4,
    )

    # 4) 상위 topn 추출
    order = np.argsort(-scores)[:topn]
    top_ids = candidate_item_ids[order]
    top_scores = scores[order]

    rec = jeju_items.set_index("item_id").loc[top_ids].reset_index()
    rec["score"] = top_scores
    rec["rank"] = np.arange(1, len(rec) + 1)

    result = rec[
        [
            "rank",
            "item_id",
            "score",
            "VISIT_AREA_NM",
            "SIDO",
            "VISIT_AREA_TYPE_CD",
            "ratings",
            "ROAD_NM_ADDR",
            "LOTNO_ADDR",
            "X_COORD",
            "Y_COORD",
        ]
    ]
    result = result.where(pd.notna(result), None)
    json_data = result.to_dict(orient="list")
    json_data = replace_nan(json_data)
    if not json_data:
        print("추천 장소가 존재하지 않습니다")
    return json_data
