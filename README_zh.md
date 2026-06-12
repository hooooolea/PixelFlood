# 🌊 PixelFlood

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
# 命令行
pixelflood sprite.png                      # 白底变透明
pixelflood sprite.png --crop --preview 8   # 自动裁剪 + 8倍预览

# Python API
from pixelflood import flood, process
result = flood(Image.open("sprite.png"))
process("sprite.png", output_path="out.png", crop=True)
```

## 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-c` | `#FFFFFF` | 背景色 |
| `-t` | `7` | 每通道容差 |
| `--crop` | 关闭 | 自动裁剪透明边 |
| `--preview` | `0` | 保存 N 倍预览图 |

## License

MIT
