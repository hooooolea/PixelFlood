# 🌊 PixelFlood

[English](../README.md) · [中文](../README_zh.md) · [日本語](../README_ja.md) · [한국어](README_ko.md)

픽셀 아트를 위한 엣지 플러드 필 투명화 도구. 배경색을 제거하면서 스프라이트 본체는 보호합니다.

---

## 문제점

기존의 "흰색 배경 제거" 도구는 **모든** 흰색 픽셀을 투명하게 만듭니다. 스프라이트에 흰색 디테일(털, 눈, 의상)이 있으면 함께 사라집니다.

<p align="center"><img src="../docs/comparison.png" width="780" alt="비교"></p>

PixelFlood는 **이미지 가장자리**에서만 플러드를 시작합니다. 윤곽선이 제방처럼 홍수를 막아 내부의 흰색은 그대로 보존됩니다.

---

## 알고리즘

<p align="center"><img src="../docs/algorithm.png" alt="원리"></p>

| 단계 | 설명 |
|------|------|
| 가장자리 시드 | 이미지 네 가장자리를 스캔하여 배경색 픽셀을 찾음 |
| 플러드 필 | BFS 4방향 확산, 윤곽선 픽셀이 차단 |
| 결과 | 가장자리와 연결된 배경만 투명, 내부 동일 색상은 유지 |

---

## 설치

```bash
pip install pixelflood
```

## 사용법

```bash
# CLI
pixelflood sprite.png                      # 흰색 배경을 투명하게
pixelflood sprite.png --crop --preview 8   # 자동 자르기 + 8배 프리뷰

# Python API
from pixelflood import flood, process
result = flood(Image.open("sprite.png"))
process("sprite.png", output_path="out.png", crop=True)
```

## 옵션

| 플래그 | 기본값 | 설명 |
|--------|-------|------|
| `-c` | `#FFFFFF` | 배경색 |
| `-t` | `7` | 채널당 허용 오차 |
| `--crop` | 꺼짐 | 투명 테두리 자동 자르기 |
| `--preview` | `0` | N배 프리뷰 저장 |

## License

MIT
