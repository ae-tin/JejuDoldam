from datetime import date
import random
import copy
import requests
from django.conf import settings

ACCOMPANY_LABEL_MAP = {
    "나홀로 여행": 0,
    "2인 여행(가족 외)": 1,
    "2인 가족 여행": 1,
    "3인 이상 여행(가족 외)": random.randint(2, 8),
    "자녀 동반 여행": random.randint(2, 6),
    "부모 동반 여행": random.randint(2, 8),
    "3대 동반 여행(친척 포함)": random.randint(2, 16),
}

MARR_STTS_LABEL_MAP = {"미혼": 1, "기혼": 2, "사별": 3, "이혼": 4, "기타": 5}
JOB_NM_LABEL_MAP = {
    "관리자": 1,
    "전문가 및 관련 종사자": 2,
    "사무 종사자": 3,
    "서비스 종사자": 4,
    "판매 종사자": 5,
    "농림어업 숙련 종사자": 6,
    "기능원 및 관련 기능 종사자": 7,
    "장치.기계 조작 및 조립 종사자": 8,
    "단순노무종사자": 9,
    "군인": 10,
    "전업주부": 11,
    "학생": 12,
    "기타": 13,
}

INCOME_LABEL_MAP = {
    "소득없음": 1,
    "월평균 100만원 미만": 2,
    "월평균 100만원 ~ 200만원 미만": 3,
    "월평균 200만원 ~ 300만원 미만": 4,
    "월평균 300만원 ~ 400만원 미만": 5,
    "월평균 400만원 ~ 500만원 미만": 6,
    "월평균 500만원 ~ 600만원 미만": 7,
    "월평균 600만원 ~ 700만원 미만": 8,
    "월평균 700만원 ~ 800만원 미만": 9,
    "월평균 800만원 ~ 900만원 미만": 10,
    "월평균 900만원 ~ 1,000만원 미만": 11,
    "월평균 1,000만원 이상": 12,
}

TRAVEL_MOTIVE_1_LABEL_MAP = {
    "일상 탈출": 1,
    "휴식과 충전": 2,
    "동반자와의 유대감": 3,
    "자아 성찰": 4,
    "SNS / 과시": 5,
    "운동 / 건강": 6,
    "새로운 경험": 7,
    "문화 탐방 / 교육": 8,
    "특별한 목적(칠순, 신혼, 수학여행 등)": 9,
    "기타": 10,
}


def get_age_group(birth_date: date) -> int:
    """
    birth_date (datetime.date) → 연령대 문자열 반환
    예: 20, 30, 40, 50, 60
    """
    if birth_date is None:
        return None
    today = date.today()

    # 만 나이 계산
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    # 연령대 계산
    age_group = (age // 10) * 10

    # 최소/최대 방어
    if age_group < 10:
        return 10
    if age_group >= 60:
        return 60

    return age_group


def get_current_month_and_season():
    """
    현재 날짜 기준으로 month(int)와 season(str)을 반환
    season: spring / summer / autumn / winter
    """
    today = date.today()
    month = today.month

    if month in (3, 4, 5):
        season = "spring"
    elif month in (6, 7, 8):
        season = "summer"
    elif month in (9, 10, 11):
        season = "autumn"
    else:  # 12, 1, 2
        season = "winter"

    return month, season


def preprocessing_input_data(user_data: dict, rec="route") -> dict:
    """
    루트추천로직 내에서 place, route의 input 처리기능
    필요한 정보가 다 들어왔을 때를 가정
    """

    user_info = copy.deepcopy(user_data)

    for key in user_info.keys():
        if key == "AGE_GRP":
            user_info["AGE_GRP"] = get_age_group(user_info["AGE_GRP"])
        elif key == "MARR_STTS":
            user_info["MARR_STTS"] = MARR_STTS_LABEL_MAP[user_info["MARR_STTS"]]
        elif key == "JOB_NM":
            user_info["JOB_NM"] = JOB_NM_LABEL_MAP[user_info["JOB_NM"]]
        elif key == "INCOME":
            user_info["INCOME"] = INCOME_LABEL_MAP[user_info["INCOME"]]
        elif key == "TRAVEL_MOTIVE_1":
            user_info["TRAVEL_MOTIVE_1"] = TRAVEL_MOTIVE_1_LABEL_MAP[
                user_info["TRAVEL_MOTIVE_1"]
            ]
    else:
        user_info["TRAVEL_COMPANIONS_NUM"] = ACCOMPANY_LABEL_MAP[
            user_info["TRAVEL_STATUS_ACCOMPANY"]
        ]
        user_info["MONTH"], user_info["SEASON"] = get_current_month_and_season()

    if rec == "place":
        user_info["TRAVEL_STATUS_DESTINATION"] = "제주"

    return user_info


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

user_info = {
            "GENDER": user_data.gender, # pass
            "AGE_GRP": user_data.birth_date, # pass
            "MARR_STTS": user_data.marriage_status, # pass
            "JOB_NM": user_data.job, # pass
            "INCOME": user_data.income, # pass
            "TRAVEL_NUM": user_data.travel_num, # pass
            "TRAVEL_STATUS_RESIDENCE": user_data.residence, # pass
        }
"""


def preprocessing_input_data_no_add_info(user_data: dict, rec="route") -> dict:
    """
    루트추천로직 외의 place 추천 input 처리기능
    기본 사용자 정보 외 없는 데이터는 랜덤으로 처리
    """

    user_info = copy.deepcopy(user_data)

    # user 기본정보만 전처리
    for key in user_info.keys():
        if key == "AGE_GRP":
            user_info["AGE_GRP"] = get_age_group(user_info["AGE_GRP"])
        elif key == "MARR_STTS":
            user_info["MARR_STTS"] = MARR_STTS_LABEL_MAP[user_info["MARR_STTS"]]
        elif key == "JOB_NM":
            user_info["JOB_NM"] = JOB_NM_LABEL_MAP[user_info["JOB_NM"]]
        elif key == "INCOME":
            user_info["INCOME"] = INCOME_LABEL_MAP[user_info["INCOME"]]
    # 나머지 필요한 정보들은 랜덤으로 처리
    else:
        user_info["TRAVEL_MOTIVE_1"] = random.choice(
            list(TRAVEL_MOTIVE_1_LABEL_MAP.values())
        )
        user_info["TRAVEL_STYL_1"] = random.choice(range(1, 8))
        user_info["TRAVEL_STATUS_ACCOMPANY"] = random.choice(
            list(ACCOMPANY_LABEL_MAP.keys())
        )
        user_info["TRAVEL_COMPANIONS_NUM"] = ACCOMPANY_LABEL_MAP[
            user_info["TRAVEL_STATUS_ACCOMPANY"]
        ]
        user_info["MONTH"], user_info["SEASON"] = get_current_month_and_season()
        user_info["HOW_LONG"] = random.choice(range(1, 9))

        if rec == "place":
            user_info["TRAVEL_STATUS_DESTINATION"] = "제주"

    return user_info


def fetch_place_id(name, latitude, longitude):
    """
    장소 이름과 좌표를 받아 카카오 API를 검색하고
    가장 정확한 장소의 id를 반환합니다.
    """
    if not name:
        return None

    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"}

    # 1. 검색 파라미터 설정
    # x: 경도(longitude), y: 위도(latitude), radius: 반경(미터)
    # sort='distance'로 설정하여 해당 좌표에서 가장 가까운 같은 이름의 장소를 찾습니다.
    params = {
        "query": name,
        "x": longitude,
        "y": latitude,
        "radius": 1000,  # 1km 반경 내 검색
        "sort": "distance",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=3)
        if response.status_code == 200:
            data = response.json()
            documents = data.get("documents", [])

            if documents:
                # 가장 가까운(첫 번째) 결과의 id를 반환
                return documents[0]["id"]

    except Exception as e:
        print(f"카카오 API 호출 실패 {name}: {e}")

    return None
