# AI Bild-Tagger (Lokales CLIP Modell)

Dieses Skript sortiert und verschlagwortet deine Bilder vollautomatisch mit Hilfe von künstlicher Intelligenz (OpenAI CLIP).
Es schreibt die gefundenen Tags (z.B. "Landscape", "Bird", "Street Photography", "Blue Tit") in standardisierte **XMP-Sidecar-Dateien**.

## Features
*   **Lokal**: Alles läuft auf deinem PC. Keine Cloud, kein Upload.
*   **Smart**: Erkennt Genres (Makro, Street, Portrait) und Inhalte (Vogel, Insekt, Auto, Schnee).
*   **Spezialisiert**: Kennt diverse Vogel- und Insektenarten sowie Street-Photography Elemente.
*   **Performance**: Überspringt automatisch bereits getaggte Bilder.
*   **Live-Überwachung**: Kann Ordner überwachen und neue Bilder sofort taggen.

## Installation

### 1. Python & Abhängigkeiten
```powershell
pip install sentence-transformers Pillow watchdog
```

## Benutzung

### Standard (Alles scannen)
```powershell
python ai_tagger.py "C:\Mein\Bilder\Ordner"
```
*   Das Skript scant den Ordner.
*   Bilder, die **schon Tags haben**, werden **übersprungen** (spart Zeit!).

### Alles neu taggen (Erzwingen)
Wenn du neue Kategorien hinzugefügt hast oder einfach alles neu berechnen willst:
```powershell
python ai_tagger.py "C:\Mein\Bilder\Ordner" --force
```

### Automatische Überwachung (Watch Mode)
Lässt das Skript im Hintergrund laufen. Wenn du neue Bilder in den Ordner kopierst, werden sie sofort erkannt:
```powershell
python ai_tagger.py "C:\Mein\Bilder\Ordner" --watch
```
*(Beenden mit STRG + C)*
