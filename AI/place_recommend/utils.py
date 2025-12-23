import functools
import traceback
import math
import requests
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

photo_name_URL = "https://places.googleapis.com/v1/places:searchText"


from typing import Optional, Tuple


def find_photo_name(address_name: str) -> Optional[Tuple[str, int, int]]:
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.photos",
    }

    payload = {
        "textQuery": address_name,
        "languageCode": "ko",
        "regionCode": "KR",
        "maxResultCount": 1,
        "locationBias": {
            "rectangle": {
                "low": {"latitude": 33.114115402, "longitude": 126.14625579156079},
                "high": {"latitude": 33.56448276039651, "longitude": 126.969676444},
            }
        },
    }

    try:
        response = requests.post(
            photo_name_URL, headers=headers, json=payload, timeout=5
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None, None, None

    places = data.get("places")
    if not places:
        return None, None, None

    photos = places[0].get("photos")
    if not photos:
        return None, None, None

    photo = photos[0]

    photo_name = photo.get("name")
    width = photo.get("widthPx")
    height = photo.get("heightPx")

    if not photo_name:
        return None, None, None

    return photo_name, width, height


def get_place_photo_url2(
    photo_name: Optional[str],
    max_width: int = 4000,
    max_height: int = 3000,
) -> Optional[str]:
    if not photo_name:
        return None

    url = f"https://places.googleapis.com/v1/{photo_name}/media"

    params = {
        "maxWidthPx": max_width,
        "maxHeightPx": max_height,
        "skipHttpRedirect": "true",
        "key": GOOGLE_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None

    return data.get("photoUri")


def trace_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[ERROR] Function: {func.__name__}")
            print(f"[ERROR] Args: {args}, Kwargs: {kwargs}")
            print(f"[ERROR] Exception: {e}")
            traceback.print_exc()
            raise  # 원래 예외 다시 던짐

    return wrapper


def replace_nan(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, list):
        return [replace_nan(v) for v in obj]
    if isinstance(obj, dict):
        return {k: replace_nan(v) for k, v in obj.items()}
    return obj
