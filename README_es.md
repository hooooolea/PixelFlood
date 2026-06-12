# 🌊 PixelFlood

[English](README.md) · [中文](README_zh.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Français](README_fr.md) · [Español](README_es.md)

Transparencia por flood-fill de borde + extracción de sprites para pixel art.

---

## Problema

Las herramientas tradicionales de "quitar fondo blanco" destruyen los detalles blancos del sprite (pelaje, ojos).

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

# Extraer sprites de una hoja
pixelflood spritesheet.png --extract -o out/
```

<p align="center"><img src="docs/extract.png" width="780" alt="Extracción"></p>

```python
from PIL import Image
from pixelflood import flood, extract

# Sprite único: quitar fondo
result = flood(Image.open("sprite.png"))

# Hoja de sprites: separar cada sprite
sprites = extract(Image.open("spritesheet.png"), min_size=500)
for i, sprite in enumerate(sprites):
    sprite.save(f"sprite-{i+1}.png")
```

## Opciones

| Flag | Por defecto | Descripción |
|------|-------------|-------------|
| `-c, --color` | `#FFFFFF` | Color de fondo |
| `-t, --threshold` | `7` | Tolerancia por canal |
| `--connectivity` | `4` | Direcciones del flood (`4` u `8`) |
| `--crop` | off | Recorte automático |
| `--margin` | `0` | Margen de recorte |
| `--preview` | `0` | Guardar vista previa Nx |
| `--extract` | off | Extraer sprites de una hoja |
| `--min-size` | `100` | Píxeles mínimos por sprite |

## License

MIT
