# 🌊 PixelFlood

[English](README.md) · [中文](README_zh.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Français](README_fr.md) · [Español](README_es.md)

Outil de transparence par flood-fill depuis les bords pour le pixel art. Supprime la couleur de fond sans abîmer le sprite.

---

## Problème

Les outils classiques de "suppression du fond blanc" rendent transparents **tous** les pixels blancs. Si votre sprite contient des détails blancs (fourrure, yeux, vêtements), ils sont détruits.

<p align="center"><img src="docs/comparison.png" width="780" alt="Comparaison"></p>

PixelFlood ne remplit qu'à partir des **bords** de l'image. Le contour agit comme une barrière, préservant le blanc intérieur.

---

## Algorithme

<p align="center"><img src="docs/algorithm.png" alt="Principe"></p>

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
# Fond blanc → transparent
pixelflood sprite.png

# Recadrage auto + aperçu 8x
pixelflood sprite.png --crop --preview 8

# Extraire les sprites individuels d'une planche
pixelflood spritesheet.png --extract -o out/
```

```python
from PIL import Image
from pixelflood import flood, extract

# Sprite unique : supprimer le fond
result = flood(Image.open("sprite.png"))

# Planche de sprites : extraire chaque sprite
sprites = extract(Image.open("spritesheet.png"), min_size=500)
for i, sprite in enumerate(sprites):
    sprite.save(f"sprite-{i+1}.png")
```

## Options

| Option | Défaut | Description |
|--------|--------|-------------|
| `-c, --color` | `#FFFFFF` | Couleur de fond (`#RRGGBB` ou `R,G,B`) |
| `-t, --threshold` | `7` | Tolérance par canal (`0` = exact) |
| `--connectivity` | `4` | Directions du flood (`4` ou `8`) |
| `--crop` | off | Recadrage automatique |
| `--margin` | `0` | Marge de recadrage |
| `--preview` | `0` | Aperçu Nx |
| `--extract` | off | Extraire les sprites d'une planche |
| `--min-size` | `100` | Taille minimum par sprite |

## License

MIT
