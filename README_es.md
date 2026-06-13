# 🌊 PixelFlood

[English](README.md) · [中文](README_zh.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Français](README_fr.md) · [Español](README_es.md)

Transparencia por flood-fill de borde + extracción de elementos para pixel art.

---

## Problema

Las herramientas tradicionales de "quitar fondo blanco" destruyen los detalles blancos del elemento (pelaje, ojos).

<p align="center"><img src="docs/comparison.png" width="780" alt="Comparación"></p>

PixelFlood solo inunda desde los **bordes**. El contorno protege el blanco interior.

---

## Algoritmo

<p align="center"><img src="docs/algorithm.png" alt="Cómo funciona"></p>

| Paso | Descripción |
|------|-------------|
| Semillas en bordes | Escanea los 4 bordes buscando píxeles de fondo |
| Flood-fill | BFS 4 direcciones, bloqueado por el contorno |
| Resultado | Solo el fondo conectado a los bordes se vuelve transparente |

---

## Instalación

```bash
pip install pixelflood
```

## Uso

```bash
# Fondo blanco → transparente
pixelflood sprite.png

# Extracción + limpieza de blanco atrapado
pixelflood spritesheet.png --extract --smart -o out/
```

<p align="center"><img src="docs/extract.png" width="780" alt="Extracción"></p>

```python
from PIL import Image
from pixelflood import flood, extract

# Elemento único: quitar fondo
result = flood(Image.open("sprite.png"))

# Hoja de elementos: separar + limpieza
sprites = extract(Image.open("spritesheet.png"), min_size=500,
                  smart=True, smart_bg_threshold=0.5)
for i, sprite in enumerate(sprites):
    sprite.save(f"sprite-{i+1}.png")
```

## Opciones

| Flag | Por defecto | Descripción |
|------|-------------|-------------|
| `-c, --color` | `#FFFFFF` | Color de fondo |
| `-t, --threshold` | `7` | Tolerancia por canal |
| `--crop` | off | Recorte automático |
| `--preview` | `0` | Guardar vista previa Nx |
| `--extract` | off | Extraer elementos de una hoja |
| `--min-size` | `100` | Píxeles mínimos por elemento |
| `--smart` | off | Eliminar blanco atrapado |
| `--smart-aggressiveness` | `0.5` | Fuerza del filtro (0=suave, 1=agresivo) |

## License

MIT
