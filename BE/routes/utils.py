from datetime import date
import random

ACCOMPANY_LABEL_MAP = {
  "나홀로 여행": 0,
  "2인 여행(가족 외)":1,
  "2인 가족 여행":1,
  "3인 이상 여행(가족 외)":random.randint(2, 8),
  "자녀 동반 여행":random.randint(2, 6),
  "부모 동반 여행":random.randint(2, 8),
  "3대 동반 여행(친척 포함)":random.randint(2, 16),
}

MARR_STTS_LABEL_MAP = {
    "미혼":1, 
    "기혼":2, 
    "사별":3, 
    "이혼":4,
    "기타":5
    }
JOB_NM_LABEL_MAP = {
    "관리자":1, 
    "전문가 및 관련 종사자":2, 
    "사무 종사자":3, 
    "서비스 종사자":4, 
    "판매 종사자":5, 
    "농림어업 숙련 종사자":6, 
    "기능원 및 관련 기능 종사자":7, 
    "장치.기계 조작 및 조립 종사자":8, 
    "단순노무종사자":9,
    "군인":10, 
    "전업주부":11,
    "학생":12, 
    "기타":13
    }

INCOME_LABEL_MAP = {
    "소득없음":1, 
    "월평균 100만원 미만":2,
    "월평균 100만원 ~ 200만원 미만":3,
    "월평균 200만원 ~ 300만원 미만":4,
    "월평균 300만원 ~ 400만원 미만":5,
    "월평균 400만원 ~ 500만원 미만":6,
    "월평균 500만원 ~ 600만원 미만":7,
    "월평균 600만원 ~ 700만원 미만":8,
    "월평균 700만원 ~ 800만원 미만":9,
    "월평균 800만원 ~ 900만원 미만":10,
    "월평균 900만원 ~ 1,000만원 미만":11, 
    "월평균 1,000만원 이상":12
    }

TRAVEL_MOTIVE_1_LABEL_MAP = {
    "일상 탈출":1, 
    "휴식과 충전":2,
    "동반자와의 유대감":3, 
    "자아 성찰":4, 
    "SNS / 과시":5, 
    "운동 / 건강":6, 
    "새로운 경험":7, 
    "문화 탐방 / 교육":8, 
    "특별한 목적(칠순, 신혼, 수학여행 등)":9, 
    "기타":10
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


def preprocessing_input_data(user_info: dict) -> dict:
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
            user_info["TRAVEL_MOTIVE_1"] = TRAVEL_MOTIVE_1_LABEL_MAP[user_info["TRAVEL_MOTIVE_1"]]
    else:
        user_info["TRAVEL_COMPANIONS_NUM"] = ACCOMPANY_LABEL_MAP[user_info["TRAVEL_STATUS_ACCOMPANY"]]
        user_info["MONTH"], user_info["SEASON"] = get_current_month_and_season()

    return user_info
