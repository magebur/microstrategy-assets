# Wichtelbriefe – Animationskurzfilm (60 s, 4K, komplett in Code)

Kein Filmmaterial, keine Bildgenerierung: Jedes Bild wird mit Python + Cairo als Vektor-Papiercollage
gezeichnet (gerissene Papierkanten, Zweiton-Falzschattierung, Papierfaser-Textur), der Ton wird mit NumPy
synthetisiert (Klavier, Glockenspiel, Streicher, Papierrascheln, Falzen, Federkratzen, Schritte, Kichern).

## Dateien
- `paper.py` – Papier-Primitive (Kanten, Schatten, Falz, Glow, Kritzel-Handschrift, Textur)
- `characters.py` – Wichtel und Kind
- `sets.py` – Haus außen, Zimmer, Fenster mit Schnee, Kalender, Wichteltür
- `inserts.py` – Pop-up-Briefe in Nahaufnahme, Papierstern, Endcard
- `film.py` – Zeitleiste / Einstellungen
- `audio.py` – Soundtrack
- `render.py` – paralleles Rendern + ffmpeg

## Rendern
```bash
pip install pycairo numpy scipy
python3 audio.py out/soundtrack.wav
python3 render.py out/wichtelbriefe_4k.mp4 out/soundtrack.wav   # W=1920 für HD
```
Schrift der Endcard: Fredoka (SIL OFL), liegt in `fonts/` und muss installiert sein (`~/.fonts`).
