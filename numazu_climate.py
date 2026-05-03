"""
沼津市（静岡県）気象データモジュール
実データに基づく月別統計値 + 天気APIスタブ設計
"""

from datetime import date
from typing import Optional

# 沼津市月別平均気象データ（気象庁統計 1991-2020平年値ベース）
MONTHLY_CLIMATE = {
    1:  {"avg_temp": 7.2,  "min_temp": 3.1,  "max_temp": 11.6, "rainfall_mm": 89,  "rainy_days": 7,  "typhoon_risk": "low",    "humidity": 65},
    2:  {"avg_temp": 8.0,  "min_temp": 3.6,  "max_temp": 12.7, "rainfall_mm": 97,  "rainy_days": 8,  "typhoon_risk": "low",    "humidity": 63},
    3:  {"avg_temp": 11.4, "min_temp": 6.4,  "max_temp": 16.5, "rainfall_mm": 155, "rainy_days": 11, "typhoon_risk": "low",    "humidity": 66},
    4:  {"avg_temp": 15.8, "min_temp": 10.5, "max_temp": 21.2, "rainfall_mm": 177, "rainy_days": 12, "typhoon_risk": "low",    "humidity": 70},
    5:  {"avg_temp": 19.8, "min_temp": 14.9, "max_temp": 24.8, "rainfall_mm": 195, "rainy_days": 12, "typhoon_risk": "low",    "humidity": 73},
    6:  {"avg_temp": 22.9, "min_temp": 18.5, "max_temp": 27.3, "rainfall_mm": 257, "rainy_days": 15, "typhoon_risk": "medium", "humidity": 82},
    7:  {"avg_temp": 26.6, "min_temp": 22.4, "max_temp": 31.0, "rainfall_mm": 212, "rainy_days": 12, "typhoon_risk": "high",   "humidity": 80},
    8:  {"avg_temp": 28.1, "min_temp": 23.7, "max_temp": 32.7, "rainfall_mm": 183, "rainy_days": 10, "typhoon_risk": "high",   "humidity": 78},
    9:  {"avg_temp": 24.7, "min_temp": 20.5, "max_temp": 29.1, "rainfall_mm": 285, "rainy_days": 14, "typhoon_risk": "high",   "humidity": 80},
    10: {"avg_temp": 19.5, "min_temp": 14.8, "max_temp": 24.5, "rainfall_mm": 210, "rainy_days": 11, "typhoon_risk": "medium", "humidity": 74},
    11: {"avg_temp": 14.2, "min_temp": 9.5,  "max_temp": 19.2, "rainfall_mm": 128, "rainy_days": 8,  "typhoon_risk": "low",    "humidity": 69},
    12: {"avg_temp": 9.5,  "min_temp": 5.0,  "max_temp": 14.3, "rainfall_mm": 82,  "rainy_days": 6,  "typhoon_risk": "low",    "humidity": 64},
}

NUMAZU_FEATURES = {
    "city": "沼津市",
    "prefecture": "静岡県",
    "latitude": 35.09,
    "longitude": 138.86,
    "annual_avg_temp": 17.1,
    "annual_rainfall_mm": 2070,
    "first_frost_date_approx": "12月中旬",
    "last_frost_date_approx": "2月下旬",
    "notes": [
        "伊豆半島の付け根に位置し温暖な海洋性気候",
        "梅雨（6月上旬〜7月中旬）は高温多湿",
        "台風は7〜9月に集中、上陸・接近リスク高",
        "冬は比較的温暖だが駿河湾からの寒風あり",
        "夏の日照時間は長く、熱帯夜も発生する",
    ],
}


def get_climate(month: Optional[int] = None) -> dict:
    """指定月（省略時は当月）の気象データを返す。APIが使えなくてもスタブで動作。"""
    if month is None:
        month = date.today().month
    return MONTHLY_CLIMATE.get(month, MONTHLY_CLIMATE[date.today().month])


def get_current_season() -> str:
    month = date.today().month
    if month in (3, 4, 5):
        return "spring"
    elif month in (6, 7, 8):
        return "summer"
    elif month in (9, 10, 11):
        return "autumn"
    return "winter"


def get_weather_stub(target_date: Optional[date] = None) -> dict:
    """
    天気APIのスタブ実装。外部API障害時のフォールバック。
    実運用では OpenWeatherMap / 気象庁API に切り替え可能。
    """
    if target_date is None:
        target_date = date.today()
    climate = get_climate(target_date.month)
    return {
        "source": "stub",
        "date": str(target_date),
        "temp_c": climate["avg_temp"],
        "humidity_pct": climate["humidity"],
        "rainfall_probability_pct": int(climate["rainy_days"] / 30 * 100),
        "typhoon_risk": climate["typhoon_risk"],
        "note": "統計平年値ベースのスタブデータ（実APIが使えない場合のフォールバック）",
    }


def fetch_weather(target_date: Optional[date] = None) -> dict:
    """
    天気情報を取得。実APIが使えない場合はスタブへ自動切替。
    将来的にはここで requests.get() 等に差し替える。
    """
    try:
        # 将来のAPI実装プレースホルダー
        # resp = requests.get(f"https://api.openweathermap.org/...", timeout=5)
        # resp.raise_for_status()
        # return resp.json()
        raise NotImplementedError("外部天気APIは未設定（スタブモードで動作）")
    except Exception:
        return get_weather_stub(target_date)
