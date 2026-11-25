# Wichtelbriefe – Die Mission (60 s, 4K, komplett in Code)

Papercraft-Kurzfilm ohne Filmmaterial und ohne Bildgenerierung: Python + Cairo zeichnen jede Papierschicht,
`engine.py` setzt sie wie in einem Schattenkasten mit weichen, geblurrten Schlagschatten, Papierfaser-/Knittertextur
und Parallax zusammen. Der Ton (Klavier, Glockenspiel, Pizzicato via Karplus-Strong, Wind, Schnurren, Fauchen,
Papiergeräusche) wird in `audio2.py` synthetisiert.

- `engine.py` – Ebenen-Compositing, Schatten, Textur, Form-Helfer (Prägung, gestanzte Schneeflocken)
- `chars2.py` – Wichtel (Krepppapier-Mütze, Faserbart, Knopfaugen), Katze (Akkordeon-Segmente), Brief, Papierflieger
- `sets2.py` – Wohnzimmer, Kamin, Sofa, Baum, Fenster im Sturm, Türen, Kalender, Wichtelstube
- `overlays.py` – aufklappende Textstreifen, URL-Anhänger
- `film2.py` – Zeitleiste und Einstellungen
- `render.py` – paralleles Rendern + ffmpeg

```bash
python3 audio2.py out/soundtrack.wav
python3 render.py out/wichtelbriefe_mission_4k.mp4 out/soundtrack.wav   # W=1920 für HD
```
Schriften (SIL OFL): Kurale (Texte, Anhänger), liegt in `fonts/`, muss in `~/.fonts` installiert sein.
