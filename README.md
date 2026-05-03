# Numazu Garden OS

沼津市（静岡県）の気象特性に合わせた家庭菜園・ハーブ管理CLIツール。

**管理植物（2026-05-04 植付）**
- ステラミニ（固定種トマト）
- ストロング系ラベンダー

## 特徴

- 沼津市の気象統計（平均気温・降水量・台風リスク）に基づく育成アドバイス
- 天気APIが使えない場合は自動的にスタブモードで動作
- 固定種トマトの採種管理サポート
- 台風シーズン（7〜9月）の特別対策アドバイス
- 標準ライブラリのみ使用（追加インストール不要）

## 使い方

```bash
# 全体サマリー
python garden_manager.py status

# 植物一覧
python garden_manager.py list

# 育成アドバイス（全植物）
python garden_manager.py advice

# 特定植物のアドバイス
python garden_manager.py advice --plant tomato
python garden_manager.py advice --plant lavender

# 年間管理カレンダー
python garden_manager.py calendar

# 沼津市気象情報
python garden_manager.py weather
```

## ファイル構成

```
numazu-garden-os/
├── garden_manager.py   # メインCLI
├── plants.json         # 植物データ（水やり・施肥・剪定スケジュール）
├── numazu_climate.py   # 沼津市気象データモジュール（APIスタブ設計）
├── advisor.py          # 育成アドバイスロジック
├── requirements.txt    # 依存パッケージ（最小限）
├── lessons.md          # 開発経緯・設計判断の記録
└── README.md
```

## 沼津市の気象特性

| 月 | 平均気温 | 降水量 | 台風リスク |
|---|---|---|---|
| 1〜2月 | 7〜8°C | 90〜100mm | 低 |
| 3〜5月 | 11〜20°C | 155〜195mm | 低 |
| 6月 | 23°C | 257mm | 中（梅雨） |
| 7〜8月 | 27〜28°C | 183〜212mm | **高** |
| 9月 | 25°C | 285mm | **高** |
| 10〜11月 | 14〜20°C | 128〜210mm | 中 |
| 12月 | 10°C | 82mm | 低 |

- 年間平均気温：17.1°C（温暖な海洋性気候）
- 年間降水量：約2,070mm
- 初霜：12月中旬 / 終霜：2月下旬

## 天気API設計

`numazu_climate.py` の `fetch_weather()` は以下の優先順位で動作します：

1. 外部天気API（将来実装予定）
2. **統計平年値ベースのスタブ**（現在のデフォルト）

スタブモードでも気象統計に基づいた有用なアドバイスが得られます。

## 要件

- Python 3.10 以上
- 追加パッケージ不要（標準ライブラリのみ）

## ライセンス

MIT
