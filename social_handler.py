#!/usr/bin/env python3
"""
広報ロジック部 — Threads API 連携（スタブ付きフォールバック）。
外部ライブラリ不使用（標準ライブラリのみ）。
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ENV_FILE = Path(__file__).parent / ".env"
_PLACEHOLDER = "PLACEHOLDER"


def _load_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    # 環境変数で上書き可（CI/テスト用途）
    for key in ("THREADS_TOKEN", "THREADS_USER_ID"):
        if key in os.environ:
            env[key] = os.environ[key]
    return env


def _is_placeholder(token: str) -> bool:
    return not token or token == _PLACEHOLDER


def _post_to_threads_api(token: str, user_id: str, text: str) -> dict:
    """
    Threads Graph API へ投稿する。
    未実装フェーズ: NotImplementedError を上げてスタブにフォールバックさせる。
    実際のAPI実装時はここを書き換える。
    """
    raise NotImplementedError(
        "Threads API 実装待ち。config_server で THREADS_TOKEN を設定後に有効化予定。"
    )

    # --- 将来の実装例（今は到達しない） ---
    # container_url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    # payload = urllib.parse.urlencode({"media_type": "TEXT", "text": text, "access_token": token}).encode()
    # req = urllib.request.Request(container_url, data=payload, method="POST")
    # with urllib.request.urlopen(req, timeout=10) as resp:
    #     container = json.loads(resp.read())
    # publish_url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
    # payload2 = urllib.parse.urlencode({"creation_id": container["id"], "access_token": token}).encode()
    # req2 = urllib.request.Request(publish_url, data=payload2, method="POST")
    # with urllib.request.urlopen(req2, timeout=10) as resp2:
    #     return json.loads(resp2.read())


def _simulate(text: str) -> dict:
    """シミュレーションモード: 実際には送信せず結果を返す"""
    print("[SIMULATION] ─── Threads 投稿プレビュー ───────────────────")
    print(text)
    print("[SIMULATION] ─────────────────────────────────────────────")
    print("[SIMULATION] 実際の投稿は行われていません。")
    print("[SIMULATION] 本番送信するには config_server で THREADS_TOKEN を設定してください。")
    print(f"[SIMULATION]   → python config_server.py  （localhost:8080）")
    return {"simulated": True, "text": text}


def post_text(text: str) -> dict:
    """
    Threads にテキスト投稿するエントリポイント。
    トークン未設定 or 例外発生時はシミュレーションに自動フォールバック。
    """
    env = _load_env()
    token = env.get("THREADS_TOKEN", _PLACEHOLDER)
    user_id = env.get("THREADS_USER_ID", "")

    if _is_placeholder(token):
        print("[social_handler] THREADS_TOKEN が未設定 → シミュレーションモードで続行")
        return _simulate(text)

    try:
        result = _post_to_threads_api(token, user_id, text)
        print(f"[social_handler] 投稿完了: {result}")
        return result
    except NotImplementedError as e:
        print(f"[social_handler] API未実装 ({e}) → シミュレーションモードで続行")
        return _simulate(text)
    except urllib.error.HTTPError as e:
        print(f"[social_handler] HTTP {e.code}: {e.reason} → シミュレーションモードで続行")
        return _simulate(text)
    except Exception as e:
        print(f"[social_handler] 予期しないエラー ({type(e).__name__}: {e}) → シミュレーションモードで続行")
        return _simulate(text)


def compose_garden_post(plants: list[dict], weather: dict) -> str:
    """
    今日のガーデン状態から Threads 向けのテキストを生成する。
    """
    from datetime import date
    from advisor import get_growth_stage, days_since_planted

    today = date.today()
    temp = weather.get("temp_c", "?")
    lines = [
        f"🌱 沼津ガーデン日誌 {today.strftime('%Y/%m/%d')}",
        f"沼津市 気温 {temp}°C",
        "",
    ]

    for p in plants:
        days = days_since_planted(p["planted_date"])
        stage = get_growth_stage(p)
        lines.append(f"▸ {p['name']} — 定植{days}日目")
        lines.append(f"  {stage}")

    lines += [
        "",
        "#沼津 #家庭菜園 #ステラミニ #ラベンダー #固定種",
    ]
    return "\n".join(lines)
