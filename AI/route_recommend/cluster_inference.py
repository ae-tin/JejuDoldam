import pandas as pd
import numpy as np
from pathlib import Path
from joblib import load
from utils import trace_error, replace_nan

BASE_DIR = Path(__file__).resolve().parent
save_path = BASE_DIR / "model"
gps_data_path = BASE_DIR / "data_local"
# photo url이 존재하는 user만 따로 담은 csv
df_raw = pd.read_csv(save_path / "rating_user_info_all_cluster_photo.csv")
df_raw = df_raw.loc[:, ~df_raw.columns.str.startswith("Unnamed")]
df_desc = pd.read_csv(save_path / "gps_route_desc.csv")
df_desc = df_desc.set_index("TRAVELER_ID")

model_path = save_path / "user_cluster_kproto.joblib"
artifacts = load(model_path)

kproto = artifacts["kproto"]
scaler = artifacts["scaler"]
cat_cols = artifacts["cat_cols"]
num_cols = artifacts["num_cols"]
cat_idx = artifacts["cat_idx"]
cluster_labels = artifacts["cluster_labels"]
num_medians = artifacts["num_medians"]
cluster_name_map = artifacts["cluster_labels_name_map"]

print("✅ 모델 아티팩트 로드 완료")

# ---------------------------------------------------------
# 중점을 둘 변수 ('HOW_LONG' -> num_col, 'TRAVEL_MOTIVE_1'-> cat_col)
# ---------------------------------------------------------

weight_cat_col = ["TRAVEL_MOTIVE_1"]
weight_num_col = ["HOW_LONG"]


# 수치형 컬럼별 min/max
num_mins = df_raw[num_cols].min()
num_maxs = df_raw[num_cols].max()
num_ranges = num_maxs - num_mins
# 0으로 나누는 것 방지
num_ranges[num_ranges == 0] = 1.0


# ---------------------------------------------------------
# 신규 유저용 raw 전처리 함수
# ---------------------------------------------------------
@trace_error
def preprocess_new_user_raw(user_dict):
    new_df = pd.DataFrame([user_dict])

    # 없는 컬럼 자동 보정
    for col in cat_cols:
        if col not in new_df.columns:
            new_df[col] = "Unknown"
    for col in num_cols:
        if col not in new_df.columns:
            new_df[col] = np.nan

    # 결측치 처리
    new_df[cat_cols] = new_df[cat_cols].fillna("Unknown")
    for c in num_cols:
        new_df[c] = new_df[c].fillna(num_medians[c])

    # 타입 정리
    new_df[cat_cols] = new_df[cat_cols].astype(str)
    # 수치형은 float로 두면 됨
    for c in num_cols:
        new_df[c] = new_df[c].astype(float)

    return new_df


# ---------------------------------------------------------
# 군집 내 Gower distance로 최유사 유저 찾기
# ---------------------------------------------------------
@trace_error
def find_most_similar_in_cluster_gower(new_user_raw_df, cluster_id, topn=3):
    """
    new_user_raw_df: preprocess_new_user_raw(user_dict) 결과 (1-row DF, raw scale)
    cluster_id: 이미 예측된 군집 번호

    return: (가장 비슷한 기존 유저 row (df_raw에서), Gower distance 값)
    """
    # 이 군집에 속한 기존 유저만 선택 (raw 기준)
    cluster_members_raw = df_raw[df_raw["cluster"] == cluster_id].copy()

    if len(cluster_members_raw) == 0:
        return None, None

    # 수치형 Gower 부분: |x - y| / range
    # new_user_raw_df[num_cols].iloc[0] : 1D Series
    num_diff = (
        cluster_members_raw[num_cols].astype(float)
        - new_user_raw_df[num_cols].iloc[0].astype(float)
    ).abs() / num_ranges

    # 범주형 Gower 부분: 같으면 0, 다르면 1
    cat_diff = (
        cluster_members_raw[cat_cols].astype(str)
        != new_user_raw_df[cat_cols].iloc[0].astype(str)
    ).astype(int)

    weight_num_diff = (
        (
            cluster_members_raw[weight_num_col].astype(float)
            - new_user_raw_df[weight_num_col].iloc[0].astype(float)
        ).abs()
        / num_ranges
        * 1000
    )

    weight_cat_diff = (
        cluster_members_raw[weight_cat_col].astype(str)
        != new_user_raw_df[weight_cat_col].iloc[0].astype(str)
    ).astype(int) * 10

    # feature-wise distance를 모두 합쳐서 평균
    all_diffs = pd.concat(
        [num_diff, cat_diff, weight_num_diff, weight_cat_diff], axis=1
    )
    gower_dist = all_diffs.mean(axis=1)  # 각 row별 Gower distance

    # best_idx = gower_dist.idxmin()
    # best_user = cluster_members_raw.loc[best_idx]
    # best_dist = float(gower_dist.loc[best_idx])

    # return best_user, best_dist

    topn_idx = gower_dist.nsmallest(topn).index
    topn_users = cluster_members_raw.loc[topn_idx].reset_index(drop=True).copy()
    topn_dists = gower_dist.loc[topn_idx].astype(float).tolist()

    return topn_users, topn_dists


@trace_error
def assign_new_user(user_dict):
    """
    완전 신규 유저에 대해 군집 ID와 라벨을 반환하는 함수.

    user_dict 예시:
    {
        "GENDER": "남",
        "AGE_GRP": "30",
        "MARR_STTS": "1",
        "JOB_NM": "3",
        "INCOME": 4,
        "TRAVEL_STYL_1": "2",
        "TRAVEL_STATUS_RESIDENCE": "서울특별시",
        "TRAVEL_STATUS_ACCOMPANY": "2인 여행(가족 외)",
        "TRAVEL_MOTIVE_1": "7",
        "TRAVEL_NUM": 3,
        "TRAVEL_COMPANIONS_NUM": 1,
        "MONTH": "8",
        "SEASON": "summer",
        "HOW_LONG": 3,
    }
    """
    # 1) dict → DataFrame
    new_df = pd.DataFrame([user_dict])

    # 2) 없는 컬럼 자동 추가 (완전 신규 유저 대비)
    for col in cat_cols:
        if col not in new_df.columns:
            new_df[col] = "Unknown"
    for col in num_cols:
        if col not in new_df.columns:
            new_df[col] = np.nan

    # 3) 결측값 처리
    new_df[cat_cols] = new_df[cat_cols].fillna("Unknown")
    for c in num_cols:
        new_df[c] = new_df[c].fillna(num_medians[c])

    # 4) 타입 정리
    new_df[cat_cols] = new_df[cat_cols].astype(str)

    # 5) 스케일링
    new_df[num_cols] = scaler.transform(new_df[num_cols])

    # 6) numpy 변환 (dtype=object 필수)
    new_np = new_df[cat_cols + num_cols].to_numpy(dtype=object)

    # 7) 군집 예측
    cluster = int(kproto.predict(new_np, categorical=cat_idx)[0])
    label = cluster_labels[cluster]

    return cluster, label


@trace_error
def assign_and_find_similar_gower(user_dict):
    """
    1) 신규 유저 군집 예측
    2) 그 군집 안에서 Gower distance 기준 최유사 유저 찾기
    """
    # 1) 군집 예측 (기존에 만든 함수 사용)
    cluster_id, label = assign_new_user(user_dict)

    # 2) raw 전처리
    new_user_raw_df = preprocess_new_user_raw(user_dict)

    # 3) Gower 기반 최유사 유저 탐색
    topn_user, topn_dist = find_most_similar_in_cluster_gower(
        new_user_raw_df, cluster_id
    )
    topn_user = topn_user.TRAVELER_ID.to_list()
    print("cluster_id : ", cluster_id)
    print("cluster_name : ", cluster_name_map[cluster_id])
    return {
        "cluster_id": cluster_id,
        "cluster_label": label,
        "cluster_name": cluster_name_map[cluster_id],
        "similar_user": topn_user,  # df_raw의 한 row (Series)
        "distance": topn_dist,
    }


@trace_error
def find_route(rec_result: dict) -> dict:
    """
    assign_and_find_similar_gower의 output에서
    가장 유사한 유저의 루트 추천
    """
    top_users = rec_result["similar_user"]

    result = []
    for user in top_users:
        fname = str(user) + ".csv"
        df = pd.read_csv(gps_data_path / fname)
        df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
        df = df.where(pd.notna(df), None)
        json_data = df.to_dict(orient="list")
        json_data = replace_nan(json_data)
        # title, description 추가
        json_data["TITLE"] = df_desc.loc[user, "TITLE"]
        json_data["DESCRIPTION"] = df_desc.loc[user, "DESCRIPTION"]
        result.append(json_data)
    if not result:
        print("추천 루트가 존재하지 않습니다")
    return result


"""
example_user = {
    "GENDER": "남",
    "AGE_GRP": "30",
    "MARR_STTS": "1",
    "JOB_NM": "3",
    "INCOME": 4,
    "TRAVEL_STYL_1": "2",
    "TRAVEL_STATUS_RESIDENCE": "서울특별자치도",
    "TRAVEL_STATUS_ACCOMPANY": "2인 여행(가족 외)",
    "TRAVEL_MOTIVE_1": "7",
    "TRAVEL_NUM": 3,
    "TRAVEL_COMPANIONS_NUM": 1,
    "MONTH": "8",
    "SEASON": "summer",
    "HOW_LONG": 3,
}
"""
