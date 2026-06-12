# 🌊 PixelFlood

[English](../README.md) · [中文](../README_zh.md) · [日本語](../README_ja.md) · [Français](README_fr.md)

Outil de transparence par flood-fill depuis les bords pour le pixel art. Supprime la couleur de fond sans abîmer le sprite.

---

## Problème

Les outils classiques de "suppression du fond blanc" rendent transparents **tous** les pixels blancs. Si votre sprite contient des détails blancs (fourrure, yeux, vêtements), ils sont détruits.

<p align="center"><img src="../docs/comparison.png" width="780" alt="Comparaison"></p>

PixelFlood ne remplit qu'à partir des **bords** de l'image. Le contour agit comme une barrière, préservant le blanc intérieur.

---

## Algorithme

<p align="center"><img src="../docs/algorithm.png" alt="Principe"></p>

| Étape | Description |
|-------|-------------|
| Graines aux bords | Scan des 4 bords pour trouver les pixels de fond |
| Flood-fill | BFS 4 directions, bloqué par les pixels de contour |
| Résultat | Seul le fond connecté aux bords devient transparent |

---

## Installation

```bash
pip install pixelflood
```

## Utilisation

```bash
# CLI
pixelflood sprite.png                      # fond blanc → transparent
pixelflood sprite.png --crop --preview 8   # recadrage auto + aperçu 8x

# Python API
from pixelflood import flood, process
result = flood(Image.open("sprite.png"))
process("sprite.png", output_path="out.png", crop=True)
```

## Options

| Option | Défaut | Description |
|--------|--------|-------------|
| `-c` | `#FFFFFF` | Couleur de fond |
| `-t` | `7` | Tolérance par canal |
| `--crop` | off | Recadrage automatique |
| `--preview` | `0` | Aperçu Nx |

## License

MIT
