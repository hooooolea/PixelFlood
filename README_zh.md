# 🌊 PixelFlood

[English](README.md) · [中文](README_zh.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Français](README_fr.md) · [Español](README_es.md)

面向像素画的边缘洪泛透明填充工具。去除背景色的同时，保护精灵本体不被误伤。

---

## 问题

传统的"去白底"工具会把**所有**白色像素变透明。如果精灵本身有白色细节（毛发、眼睛、衣服），就会缺洞。

<p align="center"><img src="docs/comparison.png" width="780" alt="对比"></p>

PixelFlood 只从**图片边缘**开始洪泛。精灵轮廓线像堤坝一样阻断洪水，内部白色完好保留。

---

## 算法

<p align="center"><img src="docs/algorithm.png" alt="原理"></p>

| 步骤 | 说明 |
|------|------|
| 边缘种子 | 扫描四条边，找到背景色像素作为起点 |
| 洪泛填充 | BFS 四方向扩散，轮廓线阻断洪水 |
| 最终结果 | 仅边缘连通的背景色变透明，内部同色保留 |

---

## 安装

```bash
pip install pixelflood
```

## 使用

```bash
# 去白底
pixelflood sprite.png

# 自动裁剪 + 8倍预览
pixelflood sprite.png --crop --preview 8

# 从精灵表提取独立精灵
pixelflood spritesheet.png --extract -o out/
```

```python
from PIL import Image
from pixelflood import flood, extract

# 单个精灵：去背景
result = flood(Image.open("sprite.png"))

# 精灵表：拆出每个精灵
sprites = extract(Image.open("spritesheet.png"), min_size=500)
for i, sprite in enumerate(sprites):
    sprite.save(f"sprite-{i+1}.png")
```

## 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-c, --color` | `#FFFFFF` | 背景色（`#RRGGBB` 或 `R,G,B`） |
| `-t, --threshold` | `7` | 每通道容差（`0` = 精确匹配） |
| `--connectivity` | `4` | 洪泛方向数（`4` 或 `8`） |
| `--crop` | 关闭 | 自动裁剪透明边 |
| `--margin` | `0` | 裁剪额外边距 |
| `--preview` | `0` | 保存 N 倍预览图 |
| `--extract` | 关闭 | 从精灵表提取独立精灵 |
| `--min-size` | `100` | 每个精灵最少像素数 |

## License

MIT
