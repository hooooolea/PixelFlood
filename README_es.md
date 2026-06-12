# 🌊 PixelFlood

[English](../README.md) · [中文](../README_zh.md) · [日本語](../README_ja.md) · [Español](README_es.md)

Herramienta de transparencia por flood-fill de borde para pixel art. Elimina el color de fondo sin dañar el sprite.

---

## Problema

Las herramientas tradicionales de "quitar fondo blanco" vuelven transparentes **todos** los píxeles blancos. Si tu sprite tiene detalles blancos (pelaje, ojos, ropa), se destruyen.

<p align="center"><img src="../docs/comparison.png" width="780" alt="Comparación"></p>

PixelFlood solo inunda desde los **bordes** de la imagen. El contorno actúa como barrera, preservando el blanco interior.

---

## Algoritmo

<p align="center"><img src="../docs/algorithm.png" alt="Cómo funciona"></p>

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
# CLI
pixelflood sprite.png                      # fondo blanco → transparente
pixelflood sprite.png --crop --preview 8   # recorte auto + vista previa 8x

# Python API
from pixelflood import flood, process
result = flood(Image.open("sprite.png"))
process("sprite.png", output_path="out.png", crop=True)
```

## Opciones

| Flag | Por defecto | Descripción |
|------|-------------|-------------|
| `-c` | `#FFFFFF` | Color de fondo |
| `-t` | `7` | Tolerancia por canal |
| `--crop` | off | Recorte automático |
| `--preview` | `0` | Guardar vista previa Nx |

## License

MIT
