import requests
from pathlib import Path

import os
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# ---------------------------------------------------------
# 경로 설정
# ---------------------------------------------------------
GOOGLE_API_KEY = env("GOOGLE_API_KEY")
URL = "https://places.googleapis.com/v1/places:searchText"


def find_photo(address_name: str) -> dict:
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": ("places.id,places.displayName,places.photos,"),
    }

    payload = payload = {
        "textQuery": address_name,
        "languageCode": "ko",
        "regionCode": "KR",
        "locationBias": {
            "rectangle": {
                "low": {"latitude": 33.114115402, "longitude": 126.14625579156079},
                "high": {"latitude": 33.56448276039651, "longitude": 126.969676444},
            }
        },
    }

    response = requests.post(URL, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()
    print(data)
    return data
