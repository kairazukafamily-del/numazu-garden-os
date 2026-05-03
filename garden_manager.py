#!/usr/bin/env python3
"""
Numazu Garden OS - 沼津市家庭菜園・ハーブ管理CLI
ステラミニ（固定種トマト）＆ストロング系ラベンダー 管理ツール
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import date

from advisor import generate_full_advice
from numazu_climate import NUMAZU_FEATURES, get_climate, fetch_weather

PLANTS_FILE = Path(__file__).parent / "plants.json"


def load_plants() -> list[dict]:
    with open(PLANTS_FILE, encoding="utf-8") as f:
        return json.load(f)["plants"]


def print_separator(char: str = "─", width: int = 60) -> None:
    print(char * width)


def print_header(title: str) -> None:
    print_separator("═")
    print(f"  {title}")
    print_separator("═")


def print_section(title: str) -> None:
    print()
    print_separator("─")
    print(f"  {title}")
    print_separator("─")


def cmd_list(args: argparse.Namespace) -> None:
    """登録植物の一覧表示"""
    plants = load_plants()
    print_header("Numazu Garden OS - 管理植物一覧")
    print(f"  登録日時: {date.today()}  |  場所: {NUMAZU_FEATURES['city']}")
    print()
    for i, p in enumerate(plants, 1):
        days = (date.today() - date.fromisoformat(p["planted_date"])).days
        print(f"  {i}. {p['name']} ({p['name_en']})")
        print(f"     種別: {p['variety_type']}  |  植付: {p['planted_date']}（{days}日目）")
        print(f"     メモ: {p['notes'][:50]}...")
        print()


def cmd_advice(args: argparse.Namespace) -> None:
    """指定植物の育成アドバイス表示"""
    plants = load_plants()

    if args.plant:
        plants = [p for p in plants if args.plant.lower() in p["id"].lower() or args.plant in p["name"]]
    if not plants:
        print(f"植物 '{args.plant}' が見つかりません。")
        cmd_list(args)
        return

    for plant in plants:
        advice = generate_full_advice(plant)
        weather = advice["weather"]

        print_header(f"{advice['plant_name']} 育成アドバイス")
        print(f"  植付から {advice['days_since_planted']} 日目 | 生育ステージ: {advice['growth_stage']}")
        print(f"  天気情報源: {weather['source']} | 気温: {weather['temp_c']}°C | 湿度: {weather['humidity_pct']}%")
        print(f"  台風リスク: {weather['typhoon_risk'].upper()} | 降雨確率: {weather['rainfall_probability_pct']}%")

        cal = advice["seasonal_calendar"]
        print_section(f"今季（{cal['season_ja']}）の管理タスク")
        for task in cal["tasks"]:
            print(f"  ✓ {task}")
        if cal["advice"]:
            print(f"\n  【沼津アドバイス】 {cal['advice']}")

        print_section("水やりアドバイス")
        for tip in advice["watering"]:
            print(f"  → {tip}")

        print_section("施肥アドバイス")
        for tip in advice["fertilizing"]:
            print(f"  → {tip}")

        print_section("剪定・整枝アドバイス")
        for tip in advice["pruning"]:
            print(f"  → {tip}")

        if advice["typhoon"]:
            print_section("台風対策（重要）")
            for tip in advice["typhoon"]:
                print(f"  ⚠ {tip}")

        print()


def cmd_calendar(args: argparse.Namespace) -> None:
    """年間管理カレンダー表示"""
    plants = load_plants()

    if args.plant:
        plants = [p for p in plants if args.plant.lower() in p["id"].lower() or args.plant in p["name"]]

    season_ja = {"spring": "春（3〜5月）", "summer": "夏（6〜8月）", "autumn": "秋（9〜11月）", "winter": "冬（12〜2月）"}

    for plant in plants:
        print_header(f"{plant['name']} 年間管理カレンダー")
        seasons = plant.get("seasons", {})
        for season_key, season_label in season_ja.items():
            data = seasons.get(season_key, {})
            print(f"\n  {season_label}")
            print(f"    {data.get('advice', '')}")
            for task in data.get("tasks", []):
                print(f"    ・{task}")


def cmd_weather(args: argparse.Namespace) -> None:
    """現在の気象情報表示"""
    print_header("沼津市 気象情報")
    weather = fetch_weather()
    climate = get_climate()

    print(f"  データ源  : {weather['source']}")
    print(f"  気温      : {weather['temp_c']}°C")
    print(f"  湿度      : {weather['humidity_pct']}%")
    print(f"  降雨確率  : {weather['rainfall_probability_pct']}%")
    print(f"  台風リスク: {weather['typhoon_risk'].upper()}")
    print(f"  月間降水量: {climate['rainfall_mm']}mm（平年値）")
    print()
    print(f"  【{NUMAZU_FEATURES['city']} 気象特性】")
    for note in NUMAZU_FEATURES["notes"]:
        print(f"  ・{note}")
    if weather["source"] == "stub":
        print()
        print(f"  ※ {weather['note']}")


def cmd_status(args: argparse.Namespace) -> None:
    """全植物のサマリー表示"""
    plants = load_plants()
    weather = fetch_weather()

    print_header(f"Garden Status - {date.today()}")
    print(f"  沼津市 | 気温: {weather['temp_c']}°C | 台風: {weather['typhoon_risk'].upper()}")
    print()

    for p in plants:
        from advisor import get_growth_stage, advise_watering
        days = (date.today() - date.fromisoformat(p["planted_date"])).days
        stage = get_growth_stage(p)
        watering = advise_watering(p, weather)

        print(f"  [{p['name']}]  {days}日目 / {stage}")
        print(f"    水やり: {watering[0] if watering else '標準管理'}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Numazu Garden OS - 沼津市家庭菜園管理ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
コマンド例:
  python garden_manager.py list                    # 植物一覧
  python garden_manager.py advice                  # 全植物のアドバイス
  python garden_manager.py advice --plant tomato   # トマトのアドバイス
  python garden_manager.py calendar                # 年間カレンダー
  python garden_manager.py weather                 # 気象情報
  python garden_manager.py status                  # 全体サマリー
        """,
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="登録植物の一覧")

    advice_parser = subparsers.add_parser("advice", help="育成アドバイス")
    advice_parser.add_argument("--plant", help="植物名またはID（省略時は全植物）")

    cal_parser = subparsers.add_parser("calendar", help="年間管理カレンダー")
    cal_parser.add_argument("--plant", help="植物名またはID（省略時は全植物）")

    subparsers.add_parser("weather", help="沼津市気象情報")
    subparsers.add_parser("status", help="全体サマリー")

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "advice": cmd_advice,
        "calendar": cmd_calendar,
        "weather": cmd_weather,
        "status": cmd_status,
    }

    if args.command is None:
        cmd_status(args)
        print()
        parser.print_help()
        return

    commands[args.command](args)


if __name__ == "__main__":
    main()
