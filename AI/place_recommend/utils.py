import functools
import traceback
import math


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
