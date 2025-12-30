# AI Bild-Tagger (Lokales CLIP Modell)

Dieses Skript sortiert und verschlagwortet deine Bilder vollautomatisch mit Hilfe von künstlicher Intelligenz (OpenAI CLIP).
Es schreibt die gefundenen Tags (z.B. "Landscape", "Bird", "Street Photography", "Blue Tit") in standardisierte **XMP-Sidecar-Dateien**.

Das bedeutet: **Es funktioniert mit jeder Software**, die XMP lesen kann (Capture One, Adobe Lightroom, Darktable, DigiKam, etc.).

## Features
*   **Lokal**: Alles läuft auf deinem PC. Keine Cloud, kein Upload, keine Kosten.
*   **Smart**: Erkennt Genres (Makro, Street, Portrait) und Inhalte (Vogel, Insekt, Auto, Schnee).
*   **Spezialisiert**: Kennt diverse Vogel- und Insektenarten sowie Street-Photography Elemente.
*   **Sicher**: Verändert niemals deine Originalbilder (nur .xmp Dateien).

## Installation

### 1. Python installieren
Falls noch nicht vorhanden, installiere Python (3.12 oder neuer) von [python.org](https://www.python.org/).
*Wichtig: Beim Installieren "Add Python to PATH" anhaken!*

### 2. Abhängigkeiten installieren
Öffne ein Terminal (PowerShell oder CMD) und führe folgenden Befehl aus:

```powershell
pip install sentence-transformers Pillow
```

*Hinweis: Beim ersten Start wird das KI-Modell (~350 MB) automatisch heruntergeladen.*

## Benutzung

### Einfacher Start
Kopiere das Skript `ai_tagger.py` in deinen Bilder-Ordner und starte es einfach so:

```powershell
python ai_tagger.py
```
Es durchsucht dann den aktuellen Ordner und alle Unterordner.

### Einen bestimmten Ordner scannen
Du kannst dem Skript auch sagen, welchen Ordner es bearbeiten soll:

```powershell
python ai_tagger.py "C:\Pfad\Zu\Deinen\Bildern"
```

## Konfiguration anpassen
Du kannst das Skript einfach mit einem Texteditor (Notepad, VS Code) öffnen, um die Kategorien zu ändern.
Oben im Skript findest du Listen wie:
*   `GENRES`: Die Haupt-Kategorien.
*   `CONTENT_TAGS`: Allgemeine Objekte.
*   `BIRD_SPECIES` / `INSECT_SPECIES`: Speziallisten.

Du kannst dort einfach Wörter hinzufügen oder löschen (auf Englisch funktioniert es am besten, da das Modell englisch trainiert ist).

## Integration in Foto-Software

### Capture One
1.  Gehe zu **Bearbeiten -> Voreinstellungen -> Bild**.
2.  Aktiviere **"Packen vorziehen, wenn möglich"** (optional) und **"Automatische Synchronisierung von Sidecar-XMP"**.
3.  Alternativ: Wähle deine Bilder aus -> Rechtsklick -> **Metadaten laden**.

### Adobe Lightroom
1.  Markiere die Bilder.
2.  Rechtsklick -> **Metadaten** -> **Metadaten aus Datei lesen**.

### Darktable / DigiKam
Diese Programme lesen XMP-Dateien meist automatisch beim Import oder Neustart ein.
