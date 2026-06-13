# 🌊 PixelFlood

[English](README.md) · [中文](README_zh.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Français](README_fr.md) · [Español](README_es.md)

Transparence par flood-fill de bord + extraction d'éléments pour le pixel art.

---

## Problème

Les outils classiques de "suppression du fond blanc" rendent transparents **tous** les pixels blancs. Les détails blancs de l'élément sont détruits.

<p align="center"><img src="docs/comparison.png" width="780" alt="Comparaison"></p>

PixelFlood ne remplit qu'à partir des **bords**. Le contour protège le blanc intérieur.

---

## Algorithme

<p align="center"><img src="docs/algorithm.png" alt="Principe"></p>

| Étape | Description |
|-------|-------------|
| Graines aux bords | Scan des 4 bords pour trouver les pixels de fond |
| Flood-fill | BFS 4 directions, bloqué par le contour |
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

# Extraction + nettoyage du blanc piégé
pixelflood spritesheet.png --extract --smart -o out/
```

<p align="center"><img src="docs/extract.png" width="780" alt="Extraction"></p>

```python
from PIL import Image
from pixelflood import flood, extract

# Élément unique : supprimer le fond
result = flood(Image.open("sprite.png"))

# Planche d'éléments : extraire + nettoyage
sprites = extract(Image.open("spritesheet.png"), min_size=500,
                  smart=True, smart_bg_threshold=0.5)
for i, sprite in enumerate(sprites):
    sprite.save(f"sprite-{i+1}.png")
```

## Options

| Option | Défaut | Description |
|--------|--------|-------------|
| `-c, --color` | `#FFFFFF` | Couleur de fond |
| `-t, --threshold` | `7` | Tolérance par canal |
| `--crop` | off | Recadrage automatique |
| `--preview` | `0` | Aperçu Nx |
| `--extract` | off | Extraire les éléments d'une planche |
| `--min-size` | `100` | Taille minimum par élément |
| `--smart` | off | Supprimer le blanc piégé |
| `--smart-aggressiveness` | `0.5` | Force du filtre (0=doux, 1=agressif) |

## License

MIT
