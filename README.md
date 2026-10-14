# logiBUS® Mini-Trainer – Trainingskarten-Generator

Automatisierte Generierung von Schablonen und Trainingskarten für den **logiBUS® Mini-Trainer** aus Eclipse 4diac™ Subapplication-Dateien (`.SUB`).

Die Karten werden im **Hochformat (7,0 cm × 9,0 cm)** gerendert und passen exakt auf die Hardware-Schablone des Trainers ([layout.png](layout.png)).

---

## 1. Übersicht & Konzept

Für Übungen in der Automatisierungstechnik (IEC 61499) werden Karten auf den Trainer gelegt. Die Signalleitungen führen von den physischen Eingangsklemmen links über die Logikbausteine zu den Ausgangsklemmen rechts.

- **Kartenmaße:** 70 mm Breite × 90 mm Höhe (Hochformat).
- **Eingänge (Links):** $I_1$ bis $I_8$ im 1-cm-Raster von oben (bei 1,0 cm, 2,0 cm, … bis 8,0 cm).
- **Ausgänge (Rechts):** $Q_1$ bis $Q_8$ im 1-cm-Raster von oben (bei 1,0 cm, 2,0 cm, … bis 8,0 cm).
- **Halbkreis-Klemmen am Rand:** Die Ein- und Ausgänge sind als Halbkreise direkt an die Außenkante gesetzt.
- **Dynamische Filterung:** Es werden ausschließlich die Pins dargestellt, die in der jeweiligen Übung auch verschaltet sind (z. B. nur $I_1, I_2$ und $Q_1$).
- **IEC 61499 Baustein-Layout:** Die I/O-Treiberbausteine (`logiBUS_IXA`, `logiBUS_QXA`) werden ausgeblendet; die Kernbausteine (z. B. `AX_AND_2`) werden im Vektor-Layout gerendert.
- **TGL-Normschrift:** Bausteine und Beschriftungen nutzen die originale, schmale Schriftart nach DDR-Norm `TGL 0-17_std` und `TGL 0-16_std`.
- **Textblock unten:** Zentrierter Übungsname und mehrzeilige Aufgabenbeschreibung über die vollen 7 cm Kartenbreite.

---

## 2. Erzeugte Ausgabe-Varianten

Das Skript [`generate_cards.py`](generate_cards.py) erzeugt parallel vier verschiedene PDF-Varianten und eine SVG-Vektorgrafik:

| Variante | Zieldatei | Format / Maße | Einsatzzweck |
|---|---|---|---|
| **1. Einzelkarte** | `logiBUS_single_card.pdf` | DIN-A4 | Schneller Kontrollausdruck (1 Karte mittig mit Schnittmarken und Beschreibung) |
| **2. Sammelbogen** | `logiBUS_multi_cards.pdf` | DIN-A4 | Papiersparender Selbstdruck (6 Karten pro A4-Seite im 2×3-Raster) |
| **3. Offset-Druckerei** | `logiBUS_printshop.pdf` | 82 × 102 mm (Trim: 70×90 mm) | **Auftrags-Druckerei** mit Schnittmarken außerhalb des Papiers und `/TrimBox` |
| **3b. Exaktes Endmaß** | `logiBUS_exact_70x90.pdf` | 70 × 90 mm | Für Online-Druckereien, die Dateien 1:1 auf Endmaß ohne Schnittmarken fordern |
| **Vektorgrafik** | `<Uebung>_card.svg` | 70 × 90 mm | SVG-Grafik mit Base64-eingebetteter TGL-Normschrift |

---

## 3. Voraussetzungen

Für die Ausführung wird Python 3.10 oder neuer benötigt sowie folgende Python-Bibliotheken:

```bash
pip install reportlab svglib
```

Die Schriftarten (`TGL 0-17_std.ttf`, `TGL 0-16_std.ttf`) und der IEC 61499 Renderer liegen im Repository `IEC61499_FunctionBlock_SVG`. Die Typbibliothek liegt in `4diac_training1`.

---

## 4. Bedienung

### Aufruf über die Batch-Datei (Windows)

Am einfachsten ist der Aufruf über die mitgelieferte Batch-Datei [`generate_cards.bat`](generate_cards.bat):

1. **Per Doppelklick:** Startet die Standard-Generierung (`Uebung_002a_AX.SUB`) und hält das Konsolenfenster am Ende offen.
2. **Über die Konsole mit Parametern:**
   ```cmd
   generate_cards.bat --sub "C:\git\ms-docs\4diac_training1\Ventilsteuerung\4diacIDE-workspace\test_AX\Uebungen\Uebung_002a3_AX.SUB"
   ```

### Aufruf über Python

```bash
# 1. Standard-Aufruf (erzeugt alle Varianten fuer Uebung_002a_AX)
python generate_cards.py

# 2. Spezifische Uebungs-Datei uebergeben
python generate_cards.py --sub "C:\git\ms-docs\4diac_training1\Ventilsteuerung\4diacIDE-workspace\test_AX\Uebungen\Uebung_002a5b_AX.SUB"

# 3. Alle Uebungen aus einem Ordner in ein mehrseitiges Druck-PDF generieren
python generate_cards.py --all

# 4. Eigene Ausgabepfade angeben
python generate_cards.py --sub Uebung_002a_AX.SUB --single-out my_single.pdf --printshop-out my_printshop.pdf
```

---

## 5. CLI-Parameter Referenz

| Parameter | Typ | Standardwert | Beschreibung |
|---|---|---|---|
| `--sub` | Pfad | `Uebung_002a_AX.SUB` | Pfad zur 4diac-SubApp-Datei (`.SUB`) |
| `--all` | Flag | `False` | Alle `.SUB`-Dateien im Ordner verarbeiten |
| `--folder` | Pfad | `.../test_AX/Uebungen` | Quellverzeichnis für den `--all`-Modus |
| `--single-out` | Pfad | `logiBUS_single_card.pdf` | Dateiname für Einzelkarte auf DIN-A4 |
| `--multi-out` | Pfad | `logiBUS_multi_cards.pdf` | Dateiname für Sammelbogen auf DIN-A4 |
| `--printshop-out` | Pfad | `logiBUS_printshop.pdf` | Dateiname für Druckerei-PDF (Offset mit TrimBox) |
| `--exact-out` | Pfad | `logiBUS_exact_70x90.pdf` | Dateiname für exaktes 70×90-mm-PDF |

---

## 6. Lizenz & Urheberrecht

Copyright © 2026 Meisterschulen am Ostbahnhof München.  
Lizenziert unter der Eclipse Public License 2.0 (EPL-2.0).
