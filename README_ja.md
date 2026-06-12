# 🌊 PixelFlood

[English](README.md) · [中文](README_zh.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Français](README_fr.md) · [Español](README_es.md)

ドット絵のためのエッジフラッドフィル透過 + スプライトシート分割ツール。

---

## 問題

従来の「白背景除去」は**すべての**白ピクセルを透過します。スプライトの白い部分（毛、目）も消えてしまいます。

<p align="center"><img src="docs/comparison.png" width="780" alt="比較"></p>

PixelFlood は**画像の端**からのみフラッドします。輪郭線が堤防となって内部の白を守ります。

---

## アルゴリズム

<p align="center"><img src="docs/algorithm.png" alt="原理"></p>

| ステップ | 説明 |
|----------|------|
| エッジシード | 四辺を走査し背景色ピクセルを検出 |
| フラッドフィル | BFS 4方向拡散、輪郭線で停止 |
| 結果 | エッジと繋がった背景のみ透過 |

---

## インストール

```bash
pip install pixelflood
```

## 使い方

```bash
# 白背景を透過
pixelflood sprite.png

# スプライトシートから個別スプライトを抽出
pixelflood spritesheet.png --extract -o out/
```

<p align="center"><img src="docs/extract.png" width="780" alt="抽出"></p>

```python
from PIL import Image
from pixelflood import flood, extract

# 単一スプライト：背景除去
result = flood(Image.open("sprite.png"))

# スプライトシート：個別に分割
sprites = extract(Image.open("spritesheet.png"), min_size=500)
for i, sprite in enumerate(sprites):
    sprite.save(f"sprite-{i+1}.png")
```

## オプション

| フラグ | デフォルト | 説明 |
|--------|-----------|------|
| `-c, --color` | `#FFFFFF` | 背景色 |
| `-t, --threshold` | `7` | チャンネル毎の許容値 |
| `--connectivity` | `4` | フラッド方向数 (`4` または `8`) |
| `--crop` | オフ | 透過部分を自動トリミング |
| `--margin` | `0` | トリミング余白 |
| `--preview` | `0` | N倍プレビュー保存 |
| `--extract` | オフ | スプライトシート分割 |
| `--min-size` | `100` | 抽出最小ピクセル数 |

## License

MIT
