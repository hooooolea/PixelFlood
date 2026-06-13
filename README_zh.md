# 🌊 PixelFlood

[English](README.md) · [中文](README_zh.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Français](README_fr.md) · [Español](README_es.md)

面向像素画的边缘洪泛透明填充 + 元件表拆分工具。

---

## 问题

传统的"去白底"会把**所有**白色像素变透明。元件本身的白色细节（毛发、眼睛）会被误删。

<p align="center"><img src="docs/comparison.png" width="780" alt="对比"></p>

PixelFlood 只从**图片边缘**开始洪泛。轮廓线像堤坝一样阻断洪水，内部白色完好保留。

---

## 算法

<p align="center"><img src="docs/algorithm.png" alt="原理"></p>

| 步骤 | 说明 |
|------|------|
| 边缘种子 | 扫描四条边，找到背景色像素 |
| 洪泛填充 | BFS 四方向扩散，轮廓线阻断 |
| 最终结果 | 仅边缘连通的背景变透明，内部同色保留 |

---

## 安装

```bash
pip install pixelflood
```

## 使用

```bash
# 去白底
pixelflood sprite.png

# 拆分元件 + 封闭白判断清理
pixelflood spritesheet.png --extract --smart -o out/
```

<p align="center"><img src="docs/extract.png" width="780" alt="提取元件"></p>

```python
from PIL import Image
from pixelflood import flood, extract

# 单元件：去背景
result = flood(Image.open("sprite.png"))

# 元件表：拆分 + 封闭白判断清理
sprites = extract(Image.open("spritesheet.png"), min_size=500,
                  smart=True, smart_bg_threshold=0.5)
for i, sprite in enumerate(sprites):
    sprite.save(f"sprite-{i+1}.png")
```

## 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-c, --color` | `#FFFFFF` | 背景色 |
| `-t, --threshold` | `7` | 每通道容差 |
| `--crop` | 关闭 | 自动裁剪透明边 |
| `--preview` | `0` | 保存 N 倍预览图 |
| `--extract` | 关闭 | 元件表拆分 |
| `--min-size` | `100` | 每个元件最少像素数 |
| `--smart` | 关闭 | 判断清理元件间封闭白 |
| `--smart-aggressiveness` | `0.5` | 清理强度 (0=温和, 1=激进) |

## License

MIT
