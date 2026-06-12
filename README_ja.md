# 🌊 PixelFlood

ドット絵のためのエッジフラッドフィル透過ツール。背景色を除去しつつ、スプライト本体を保護します。

---

## 問題

従来の「白背景除去」は**すべての**白ピクセルを透過してしまいます。スプライトに白い部分（毛、目、服）があると、それも消えてしまいます。

<p align="center"><img src="docs/comparison.png" width="780" alt="比較"></p>

PixelFlood は**画像の端**からのみフラッドします。輪郭線が堤防となって洪水をせき止め、内部の白はそのまま残ります。

---

## アルゴリズム

<p align="center"><img src="docs/algorithm.png" alt="原理"></p>

| ステップ | 説明 |
|----------|------|
| エッジシード | 画像の四辺を走査し、背景色ピクセルを起点にする |
| フラッドフィル | BFS 4方向に拡散、輪郭線で停止 |
| 結果 | エッジと繋がった背景のみ透過、内部の同色は保持 |

---

## インストール

```bash
pip install pixelflood
```

## 使い方

```bash
# CLI
pixelflood sprite.png                      # 白背景を透過
pixelflood sprite.png --crop --preview 8   # 自動トリミング + 8倍プレビュー

# Python API
from pixelflood import flood, process
result = flood(Image.open("sprite.png"))
process("sprite.png", output_path="out.png", crop=True)
```

## オプション

| フラグ | デフォルト | 説明 |
|--------|-----------|------|
| `-c` | `#FFFFFF` | 背景色 |
| `-t` | `7` | チャンネル毎の許容値 |
| `--crop` | オフ | 透過部分を自動トリミング |
| `--preview` | `0` | N倍のプレビュー画像を保存 |

## License

MIT
