#!/usr/bin/env python3
"""
設定用Webサーバー — localhost:8080 で動作。
外部ライブラリ不使用（標準ライブラリのみ）。
"""

import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ENV_FILE = Path(__file__).parent / ".env"

HTML_FORM = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Numazu Garden OS — 設定</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 640px; margin: 60px auto; padding: 0 20px; background: #fafaf7; color: #2c2c2c; }}
  h1 {{ font-size: 1.4rem; color: #4a7c59; }}
  label {{ display: block; margin-top: 20px; font-weight: bold; font-size: .9rem; }}
  input[type=text], input[type=password] {{ width: 100%; padding: 8px 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem; box-sizing: border-box; }}
  .hint {{ font-size: .8rem; color: #777; margin-top: 4px; }}
  button {{ margin-top: 28px; background: #4a7c59; color: white; border: none; padding: 10px 24px; border-radius: 6px; font-size: 1rem; cursor: pointer; }}
  button:hover {{ background: #3a6048; }}
  .status {{ margin-top: 24px; padding: 12px 16px; border-radius: 6px; font-size: .9rem; }}
  .ok {{ background: #e6f4ea; color: #2d6a3f; }}
  .warn {{ background: #fff3cd; color: #856404; }}
  .placeholder {{ color: #999; font-style: italic; }}
</style>
</head>
<body>
<h1>🌱 Numazu Garden OS — API設定</h1>
<p>各APIトークンを入力してください。<br>
<span class="placeholder">PLACEHOLDER のままの項目はシミュレーションモードで動作します。</span></p>

{status_block}

<form method="POST" action="/save">
  <label>Threads API トークン</label>
  <input type="password" name="THREADS_TOKEN" value="{threads_token}" placeholder="Threads APIトークンを貼り付け">
  <div class="hint">Meta Developers → Threads API → アクセストークン</div>

  <label>Open-Meteo URL（省略可・デフォルト使用）</label>
  <input type="text" name="WEATHER_API_URL" value="{weather_url}" placeholder="https://api.open-meteo.com/v1/forecast?...">
  <div class="hint">空白にするとスタブ（平年値）を使用</div>

  <button type="submit">保存して適用</button>
</form>

<hr style="margin-top:40px;border:none;border-top:1px solid #ddd">
<p style="font-size:.8rem;color:#aaa">設定は .env ファイルに保存されます。.env は .gitignore 対象のため GitHub には上がりません。</p>
</body>
</html>
"""


def read_env() -> dict:
    env = {"THREADS_TOKEN": "PLACEHOLDER", "WEATHER_API_URL": ""}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def write_env(data: dict) -> None:
    lines = [f"{k}={v}" for k, v in data.items()]
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


class ConfigHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[config_server] {fmt % args}")

    def _send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path not in ("/", "/config"):
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return
        env = read_env()
        is_placeholder = env["THREADS_TOKEN"] == "PLACEHOLDER"
        status_block = (
            '<div class="status warn">⚠ トークンが未設定です（PLACEHOLDER）。下記フォームで入力してください。</div>'
            if is_placeholder
            else '<div class="status ok">✓ APIトークンが設定済みです。変更する場合は上書き保存してください。</div>'
        )
        html = HTML_FORM.format(
            threads_token=env["THREADS_TOKEN"],
            weather_url=env["WEATHER_API_URL"],
            status_block=status_block,
        )
        self._send_html(html)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8")
        params = urllib.parse.parse_qs(raw, keep_blank_values=True)

        env = read_env()
        for key in ("THREADS_TOKEN", "WEATHER_API_URL"):
            if key in params:
                val = params[key][0].strip()
                if val:
                    env[key] = val
        write_env(env)

        redirect_html = """<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta http-equiv="refresh" content="2;url=/">
</head><body style="font-family:system-ui;text-align:center;margin-top:80px;">
<p style="font-size:1.2rem;color:#4a7c59">✓ 設定を保存しました。2秒後に戻ります...</p>
</body></html>"""
        self._send_html(redirect_html)


def run(port: int = 8080) -> None:
    server = HTTPServer(("127.0.0.1", port), ConfigHandler)
    print(f"[Numazu Garden OS] 設定サーバー起動中 → http://localhost:{port}/")
    print("  Ctrl+C で停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[config_server] 停止しました。")


if __name__ == "__main__":
    run()
