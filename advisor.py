"""
育成アドバイスロジック
沼津市の気象特性と各植物の生育状況を組み合わせてアドバイスを生成
"""

from datetime import date, timedelta
from numazu_climate import get_climate, get_current_season, fetch_weather, NUMAZU_FEATURES


def days_since_planted(planted_date_str: str) -> int:
    planted = date.fromisoformat(planted_date_str)
    return (date.today() - planted).days


def get_growth_stage(plant: dict) -> str:
    """植物の現在の生育ステージを判定"""
    days = days_since_planted(plant["planted_date"])
    plant_id = plant["id"]

    if plant_id == "stella_mini_tomato":
        if days < 14:
            return "定植直後（活着期）"
        elif days < 30:
            return "生育初期（株の充実期）"
        elif days < 60:
            return "開花・着果期"
        elif days < 120:
            return "収穫期"
        else:
            return "収穫末期・採種期"

    elif plant_id == "strong_lavender":
        if days < 21:
            return "定植直後（根付き期）"
        elif days < 60:
            return "活着・生育期"
        elif 60 <= days < 120:
            season = get_current_season()
            if season == "summer":
                return "越夏管理期（要注意）"
            return "生育期"
        else:
            return "定植済み多年草（維持管理期）"

    return "生育中"


def advise_watering(plant: dict, weather: dict) -> list[str]:
    tips = []
    plant_id = plant["id"]
    month = date.today().month
    climate = get_climate(month)
    rain_prob = weather.get("rainfall_probability_pct", 0)

    if rain_prob >= 60:
        tips.append("本日は降雨予報のため水やり不要。")
        return tips

    if plant_id == "stella_mini_tomato":
        if month in (6, 7, 8):
            tips.append("夏季：毎朝水やり（土が完全に乾く前に）。気温が上がる前の早朝推奨。")
            tips.append(f"気温予報：{weather['temp_c']}°C。30°C超の日は夕方に追加水やりを検討。")
        elif month in (9, 10):
            tips.append("秋：土表面が乾いてから水やり（2〜3日に1回が目安）。")
        else:
            tips.append("春：土表面が乾いてから水やり（2日に1回が目安）。定植後2週間は土を乾かしすぎない。")
        if climate["typhoon_risk"] == "high":
            tips.append("台風シーズン：台風接近前日は水やりを控えめに（強雨前の過湿を避ける）。")

    elif plant_id == "strong_lavender":
        if month in (6, 7, 8):
            tips.append("梅雨〜夏：水やりは最小限。鉢植えは土が乾いて2〜3日後に水やり。")
            tips.append("地植えは雨だけで十分な場合が多い。過湿は根腐れの原因。")
        elif month in (12, 1, 2):
            tips.append("冬：月2〜3回程度。土が完全に乾いてから与える。")
        else:
            tips.append("週1〜2回。土の中まで乾いたら鉢底から水が出るまでたっぷり。")
        tips.append("沼津の多湿環境では水やりし過ぎに注意。晴れた日の午前中に与える。")

    return tips


def advise_fertilizing(plant: dict) -> list[str]:
    tips = []
    plant_id = plant["id"]
    month = date.today().month
    days = days_since_planted(plant["planted_date"])

    if plant_id == "stella_mini_tomato":
        if days < 14:
            tips.append("定植直後：元肥が入っていれば追肥不要。株が活着するまで肥料は控える。")
        elif days < 30:
            tips.append("生育初期：第一花房が咲いたら追肥開始（緩効性化成肥料）。")
        elif month in (6, 7, 8):
            tips.append("収穫期：週1回の液体肥料（カリウム・リン重視）。チッソ過多は避ける。")
            tips.append("葉の色が薄くなったら追肥サイン。黄化は窒素不足の可能性。")
        elif month in (9, 10):
            tips.append("収穫末期：施肥はほぼ不要。採種を目的とする場合は一切与えない。")

    elif plant_id == "strong_lavender":
        if days < 30:
            tips.append("定植直後：1ヶ月は施肥不要（植付時の元肥で十分）。")
        elif month == 3:
            tips.append("春の芽吹き前：緩効性肥料を少量施す（規定量の半量）。")
        elif month in (6, 7, 8):
            tips.append("梅雨〜夏：施肥不要。肥料過多は徒長を招き蒸れやすくなる。")
        elif month in (9, 10):
            tips.append("秋の回復期：薄めの液肥を月1回程度。花後剪定後に少量。")
        else:
            tips.append("冬：施肥不要。休眠期は肥料を与えない。")

    return tips


def advise_pruning(plant: dict) -> list[str]:
    tips = []
    plant_id = plant["id"]
    month = date.today().month
    days = days_since_planted(plant["planted_date"])

    if plant_id == "stella_mini_tomato":
        tips.append("脇芽管理：週1〜2回、腋芽が5cm以下のうちに手で摘む。")
        if month in (6, 7, 8, 9):
            tips.append("下葉の除去：地面から30cm以内の葉は取り除き、疫病・泥はねを防ぐ。")
        if get_climate(month)["typhoon_risk"] in ("medium", "high"):
            tips.append("台風対策：上部の葉を間引き風通しを改善。支柱との結束を確認。")

    elif plant_id == "strong_lavender":
        if month == 3:
            tips.append("春の剪定：木質化した古い茎を1/3カット。新芽の出ている位置の上で切る。")
        elif month in (5, 6):
            tips.append("花後剪定（最重要）：花茎を付け根でカット。梅雨前に風通しを確保。")
            tips.append("梅雨対策：株の中心部の込み入った茎も間引き、蒸れを防ぐ。")
            if month == 6:
                tips.append("梅雨入り前の今が剪定の最重要タイミング。遅れると越夏が困難になる。")
        elif month in (9, 10):
            tips.append("秋の軽剪定：伸びすぎた枝を軽く整える。強い剪定は避ける。")
        else:
            tips.append("この時期の強い剪定は避ける。枯れた枝のみ除去。")

    return tips


def advise_typhoon(plant: dict, weather: dict) -> list[str]:
    tips = []
    risk = weather.get("typhoon_risk", "low")
    if risk == "low":
        return tips

    plant_id = plant["id"]
    tips.append(f"台風リスク：{risk.upper()}。沼津市は台風の直撃・接近が多い地域。")

    if plant_id == "stella_mini_tomato":
        tips.append("支柱の補強：複数箇所で茎を誘引し直す。支柱同士を横棒で連結するとより安全。")
        tips.append("台風通過後：倒伏・折れた茎の確認、泥はねによる病気予防のため下葉を除去。")

    elif plant_id == "strong_lavender":
        tips.append("多年草で根が張っていれば比較的風に強いが、鉢植えは室内移動を推奨。")
        tips.append("台風後は株元の土が流れていないか確認。水はけの悪い土では根腐れに注意。")

    return tips


def get_seasonal_calendar(plant: dict) -> dict:
    """年間管理カレンダーを返す"""
    season = get_current_season()
    plant_id = plant["id"]
    seasons_data = plant.get("seasons", {})
    current = seasons_data.get(season, {})
    return {
        "current_season": season,
        "season_ja": {"spring": "春", "summer": "夏", "autumn": "秋", "winter": "冬"}[season],
        "tasks": current.get("tasks", []),
        "advice": current.get("advice", ""),
        "all_seasons": seasons_data,
    }


def generate_full_advice(plant: dict) -> dict:
    """植物の総合アドバイスを生成"""
    weather = fetch_weather()
    climate = get_climate()
    days = days_since_planted(plant["planted_date"])
    stage = get_growth_stage(plant)
    calendar = get_seasonal_calendar(plant)

    return {
        "plant_name": plant["name"],
        "planted_date": plant["planted_date"],
        "days_since_planted": days,
        "growth_stage": stage,
        "weather": weather,
        "climate_month": {
            "avg_temp": climate["avg_temp"],
            "rainfall_mm": climate["rainfall_mm"],
            "typhoon_risk": climate["typhoon_risk"],
        },
        "seasonal_calendar": calendar,
        "watering": advise_watering(plant, weather),
        "fertilizing": advise_fertilizing(plant),
        "pruning": advise_pruning(plant),
        "typhoon": advise_typhoon(plant, weather),
        "numazu_notes": NUMAZU_FEATURES["notes"],
    }
