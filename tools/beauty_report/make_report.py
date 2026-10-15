"""Generates the beauty report Markdown from the measured data.

Usage:
    python make_report.py [--dir <work folder>] [--out <report.md>]
"""
import argparse, csv, json, collections, statistics as st, os
from pathlib import Path

SELF_DIR = Path(__file__).resolve().parent
REPO_ROOT = SELF_DIR.parents[1]

ap = argparse.ArgumentParser(description="Render the beauty report Markdown.")
ap.add_argument("--dir", default=str(SELF_DIR),
                help="folder holding scores.csv/report_data.json (default: this script's folder)")
ap.add_argument("--out", default=str(REPO_ROOT / "Beauty-Report_test_AX_exact_70x90.md"),
                help="target Markdown file")
args = ap.parse_args()
WORK = Path(args.dir)

D = json.load(open(WORK / 'report_data.json', encoding='utf-8'))
rows = list(csv.DictReader(open(WORK / 'scores.csv', encoding='utf-8')))
def f(r, k, d=0.0):
    try: return float(r[k])
    except Exception: return d

N = D['n']
g = D['grades']
big_cdf = [r for r in rows if f(r, 'n_blocks') >= 10 and r['grade'] in ('C', 'D', 'F')]
def de(x):
    return str(x).replace('.', ',')
def pc(n): return de(f"{100.0*n/N:.1f}") + " %"

L = []
w = L.append

w("# Schönheits-Report: Übungskarten `output/test_AX/exact_70x90`")
w("")
w("Automatische ästhetische Bewertung aller 498 Karten im 70 × 90 mm-Format.")
w("")
w("| | |")
w("|---|---|")
w("| Ordner | `output/test_AX/exact_70x90` |")
w("| Karten | 498 PDF-Dateien |")
w("| Kartenformat | 70,0 × 90,0 mm (198,43 × 255,12 pt) |")
w("| Bewertungsgrundlage | Vektorgeometrie der PDF + Rasterauswertung (150 dpi) |")
w("| Ergebnis | Median 84,6 von 100 Punkten |")
w("")
w("> [!NOTE]")
w("> Bewertet wird ausschließlich das **Layout der fertigen Karte** (Linienführung, Flächennutzung,")
w("> Beschriftung, Aufräumtheit) – nicht die didaktische Qualität oder die Richtigkeit der 4diac-Übung.")
w("> Grundlage sind messbare geometrische Größen, die automatisch aus jedem PDF ermittelt und an")
w("> Kontaktbögen (ca. 100 Karten) visuell gegengeprüft wurden.")
w("")
w("---")
w("")
w("## 1. Bewertungsmaßstab")
w("")
w("Jede Karte wird auf fünf Achsen mit 0–100 Punkten bewertet; die Gesamtnote ist der gewichtete Mittelwert.")
w("")
w("| Achse | Gewicht | Was gemessen wird |")
w("|---|---|---|")
w("| **Linienführung** | 42 % | Kreuzungen echter Leiterbahnen (Segment/Segment-Schnitt), Leitungslänge pro Draht |")
w("| **Ausgewogenheit** | 20 % | genutzte Kartenhöhe, Leerraum oben/unten, mittlerer Freiraum |")
w("| **Dichte** | 18 % | Tintendeckung im Zeichenfeld, größter „Clutter-Hotspot“ (6 × 8 mm), überlappende Bausteine |")
w("| **Beschriftung** | 14 % | Beschreibungszeilen, Text über Text, Text über Baustein, Text bis/über den Kartenrand |")
w("| **Blockverteilung** | 6 % | vertikale Streuung der Bausteine (alles oben gestapelt? gleichmäßig verteilt?) |")
w("")
w("Notenschlüssel: **A+** ≥ 92 · **A** 84–91 · **B** 74–83 · **C** 64–73 · **D** 54–63 · **F** < 54")
w("")
w("---")
w("")
w("## 2. Gesamtergebnis")
w("")
w("| Note | Punkte | Karten | Anteil |")
w("|---|---|---:|---:|")
w(f"| A+ | ≥ 92 | {g['A+']} | {pc(g['A+'])} |")
w(f"| A | 84–91 | {g['A']} | {pc(g['A'])} |")
w(f"| B | 74–83 | {g['B']} | {pc(g['B'])} |")
w(f"| C | 64–73 | {g['C']} | {pc(g['C'])} |")
w(f"| D | 54–63 | {g['D']} | {pc(g['D'])} |")
w(f"| F | < 54 | {g['F']} | {pc(g['F'])} |")
w("")
w(f"**{g['A+'] + g['A']} von {N} Karten ({pc(g['A+'] + g['A'])}) erreichen Note A oder besser.** "
  f"Das Grundlayout (Raster, Klemmen-Badges, TGL-Schrift, Titel-/Beschreibungsblock) ist durchgängig "
  f"hochwertig und einheitlich – die Unterschiede entstehen fast ausschließlich aus der jeweiligen Übungsstruktur.")
w("")
w("### Kennzahlen der Stichprobe")
w("")
s = D['stats']
def cnt_of(key):
    return int(s[key].split('(')[1].rstrip(')'))
def pct_of(key):
    return de(s[key].split(' (')[0].replace('%', '').strip()) + " %"
def stat_line(label, key):
    return f"| {label} | {pct_of(key)} ({cnt_of(key)} Karten) |"
w("| Beobachtung | Anteil der Karten |")
w("|---|---|")
w(stat_line("mindestens eine Linienkreuzung", 'crossings_gt0'))
w(stat_line("≥ 5 Kreuzungen", 'crossings_ge5'))
w(stat_line("≥ 20 Kreuzungen", 'crossings_ge20'))
w(stat_line("Text überlappt anderen Text (verstümmelte Beschriftung)", 'text_overlap_gt0'))
w(stat_line("≥ 3 solche Textüberlappungen", 'text_overlap_ge3'))
w(stat_line("Bausteine ragen in das Titel-/Beschreibungsband", 'tbc_gt0'))
w(stat_line("≥ 8 Bausteine im Textband", 'tbc_ge8'))
w(stat_line("Beschreibungstext stößt an den unteren Kartenrand (≤ 1 % Rand)", 'body_bottom_gt099'))
w(stat_line("Text läuft über den unteren Kartenrand hinaus (wird abgeschnitten)", 'body_bottom_gt1'))
w(stat_line("Beschriftung wird am linken Kartenrand abgeschnitten", 'clip_left'))
w(stat_line("mehr als 40 % der Karte unten ungenutzt (top-lastig)", 'bottom_gap_gt40'))
w(stat_line("mehr als 12 Beschreibungszeilen", 'lines_gt12'))
w(stat_line("≥ 10 Bausteine (sehr dichte Netze)", 'blocks_ge10'))
w(stat_line("sehr leer (Tintendeckung < 2,5 %)", 'ink_lt2_5'))
w(stat_line("keine Leiterbahnen (reine Durchschleif-/Leerkarten)", 'nowires'))
w("")
w("---")
w("")
w("## 3. Die 25 schönsten Karten")
w("")
w("| # | Karte | Note | Punkte | Kreuzungen | Bausteine | Beschreibungszeilen |")
w("|---:|---|---|---:|---:|---:|---:|")
for i, r in enumerate(D['best'], 1):
    w(f"| {i} | `{r['ex']}` | {r['g']} | {de(r['t'])} | {r['cr']} | {r['blk']} | {r['lines']} |")
w("")
w("Gemeinsamkeiten: ein bis vier Bausteine, kurze Wege, keine Linienkreuzung, so gut wie keine "
  "überlappenden Beschriftungen und eine kompakte Beschreibung. Typisch sind die einfachen Ein-/Ausgänge der "
  "Familien `Uebung_010`, `Uebung_011`, `Uebung_013`, `Uebung_021`, `Uebung_028`, `Uebung_070`, `Uebung_093b`.")
w("")
w("> [!TIP]")
w("> Ein Teil der Spitzenplätze sind bewusst sehr einfache Karten (`Uebung_003f_AX` besteht z. B. nur aus "
  "vier parallelen Leitungen ohne Baustein). Sie sind aufgeräumt und kreuzungsfrei, aber auch leer – "
  "wer „Schönheit“ mit visueller Fülle gleichsetzt, würde sie niedriger einsortieren. Die Noten unten "
  "belohnen technische Sauberkeit, nicht Fülle (siehe auch Abschnitt 5.6).")
w("")
w("---")
w("")
w("## 4. Die 25 schwächsten Karten")
w("")
w("| # | Karte | Note | Punkte | Kreuzungen | Text über Text | Bausteine im Textband | Zeilen |")
w("|---:|---|---|---:|---:|---:|---:|---:|")
for i, r in enumerate(D['worst'], 1):
    w(f"| {i} | `{r['ex']}` | {r['g']} | {de(r['t'])} | {r['cr']} | {r['tov']} | {r['tbc']} | {r['lines']} |")
w("")
w("Zwei deutlich unterschiedliche Problemgruppen:")
w("")
w("1. **Überfüllte Großnetzwerke** (`Uebung_122`, `Uebung_122b`, `Uebung_056`, `Uebung_025`, `Uebung_080f`, "
  "`Uebung_060`): 13–67 Bausteine auf 7 × 9 cm. Die Karte ist vollständig gefüllt, Leitungen kreuzen sich "
  "hundert- bis tausendfach, Beschriftungen liegen übereinander. Diese Übungen sind für das Kartenformat "
  "schlicht zu groß.")
w("2. **Karten mit dickem Beschreibungsband** (`Uebung_120`–`Uebung_135`, `Uebung_006c`, `Uebung_011b4`–"
  "`011b7`, `Uebung_006_SAFE_AX`): 12–22 Beschreibungszeilen füllen das untere Drittel; das Titelband "
  "wird außerdem von tief liegenden Bausteinen überlagert und der Text läuft unten über den Kartenrand hinaus.")
w("")
w("---")
w("")
w("## 5. Wiederkehrende Mängel (Befundklassen)")
w("")
w("### 5.1 Linienkreuzungen")
w("")
w(f"{pct_of('crossings_gt0')} ({cnt_of('crossings_gt0')} Karten) weisen mindestens eine echte "
  f"Kreuzung zweier Leitungen auf, {pct_of('crossings_ge20')} ({cnt_of('crossings_ge20')} Karten) sogar mehr als 20. "
  "Spitzenreiter sind `Uebung_122b_AX` (6575 erkannte "
  "Schnittpunkte) und `Uebung_122_AX` (3590). Bereits ab etwa 5 Kreuzungen wird der Signalfluss "
  "schwer nachvollziehbar; die Kreuzungen stammen überwiegend aus invertierten Pin-Zuordnungen "
  "(siehe [`fix-TODO.md`](fix-TODO.md)) und aus der schieren Netzdichte.")
w("")
w("Betroffen sind auch alle in `fix-TODO.md` markierten Fälle – der Messwert bestätigt sie, z. B. "
  "`Uebung_019b_AX` (9), `Uebung_019c_AX` (11), `Uebung_039a_AX` (7), `Uebung_040_AX` (120), `Uebung_087a1_AX` (20).")
w("")
w("### 5.2 Text über Text (verstümmelte Beschriftungen)")
w("")
w("Wenn Bausteine vertikal gestapelt werden, schiebt sich der Instanzname des unteren Bausteins in den "
  "Baustein darüber, oder Portbeschriftungen benachbarter Blöcke überlagern sich zu unlesbaren "
  "Zeichenketten. Beim einfachen Netz (`Uebung_011f_AX`, `Uebung_010a_AX`) tritt das nicht auf, in den "
  "mittleren und unteren Noten gehäuft.")
w("")
w("Beispiele: `Uebung_026_AX` (6 Textüberlappungen), `Uebung_023b_AX2`, `Uebung_024_AX`, "
  "`Uebung_103c2`, `Uebung_094c2_AX`, `Uebung_122_AX`, `Uebung_028a_AR`.")
w("")
w("### 5.3 Bausteine ragen in das Titel-/Beschreibungsband")
w("")
w(f"{pct_of('tbc_gt0')} ({cnt_of('tbc_gt0')} Karten) haben Bausteine, die in die untere "
  "Textzone hineinreichen; die Karte wirkt dadurch unten 'zugebaut'. Zusätzlich weisen "
  f"{pct_of('lines_gt12')} ({cnt_of('lines_gt12')} Karten) mehr als zwölf Beschreibungszeilen, wodurch "
  "das untere Drittel fast vollständig vom Text belegt wird (`Uebung_006c_AX` mit 22 Zeilen am stärksten).")
w("")
w("### 5.4 Text läuft über den Kartenrand")
w("")
w(f"Konkret messbar: {pct_of('clip_left')} ({cnt_of('clip_left')} Karten) haben Beschriftungen, die am "
  "**linken Rand** "
  "angeschnitten werden (u. a. `Uebung_150_AX`, `Uebung_151_AX`, `Uebung_073d_AUI`, `Uebung_121_AX`, "
  f"`Uebung_011b1_AX`), und {pct_of('clip_bottom')} ({cnt_of('clip_bottom')} Karten) haben Text, der über "
  "den **unteren Rand** hinausragt "
  "(`Uebung_020e2_AX`, `Uebung_020f2_AX`, `Uebung_094b_AX`, `Uebung_103c2`, `Uebung_160b_AX`, "
  "`Uebung_248_AX` – bis zu 5,8 pt ≈ 2 mm abgeschnitten; das ist echte, im Druck sichtbare Kürzung).")
w("")
w("### 5.5 Top-lastige Karten / ungenutzte Kartenfläche")
w("")
w(f"{pct_of('bottom_gap_gt40')} ({cnt_of('bottom_gap_gt40')} Karten) lassen mehr als 40 % der Kartenhöhe "
  "unterhalb des Netzwerks leer, "
  "weil der Baustein auf die mittlere Höhe der genutzten Eingänge zentriert wird und niedrige Klemmen "
  "(I1, I2 …) physikalisch weit oben liegen. Das ist funktional richtig, wirkt aber leer und "
  "unausgewogen – Beispiele `Uebung_001_AX` (83 % Leerraum unten), `Uebung_001c_AX`, "
  "`Uebung_004a_AX`, `Uebung_001e_AX`, `Uebung_004b6_AX`, `Uebung_005_AX`.")
w("")
w("Umgekehrt gibt es nur 5 Karten mit großem Freiraum oben (`Uebung_034_AX` mit 61 %), weil dort nur "
  "hohe Klemmen genutzt werden.")
w("")
w("### 5.6 Zu leere und zu volle Karten")
w("")
w(f"- {pct_of('ink_lt2_5')} ({cnt_of('ink_lt2_5')} Karten) sind sehr leer (Tintendeckung < 2,5 %), teils "
  "reine Durchschleifkarten ohne Baustein (`Uebung_001_AX`, `Uebung_001c_AX`, `Uebung_003_AX`, "
  "`Uebung_003f_AX`) – technisch sauber, optisch aber dünn.")
w(f"- {pct_of('blocks_ge10')} ({cnt_of('blocks_ge10')} Karten) enthalten 10 und mehr Bausteine; "
  f"{len(big_cdf)} dieser Karten landen in den Noten C bis F.")
w("")
w("### 5.7 Kartenfamilien")
w("")
w("| Schlechteste Familien (Ø Punkte) | Beste Familien (Ø Punkte) |")
w("|---|---|")
fam_w = D['weak_families']; fam_s = D['strong_families']
for i in range(max(len(fam_w), len(fam_s))):
    a = f"`Uebung_{fam_w[i][0]}*` ({fam_w[i][2]} Karten) – {str(fam_w[i][1]).replace('.', ',')}" if i < len(fam_w) else ""
    b = f"`Uebung_{fam_s[i][0]}*` ({fam_s[i][2]} Karten) – {str(fam_s[i][1]).replace('.', ',')}" if i < len(fam_s) else ""
    w(f"| {a} | {b} |")
w("")
w("Die Ethernet-/NetCat-Kette `Uebung_120`–`Uebung_135` ist die auffälligste Problemgruppe (dichte "
  "Netzwerke **und** lange Beschreibungen gleichzeitig).")
w("")
w("---")
w("")
w("## 6. Was durchgängig gut ist")
w("")
w("- Einheitliches Grundraster (1-cm-Klemmenraster, Halbkreis-Badges links/rechts) über alle 498 Karten.")
w("- Konsequente TGL-Normschrift, klare Titel-/Beschreibungstypografie im unteren Band.")
w(f"- {pc(N - int(s['crossings_gt0'].split('(')[1].rstrip(')')))} aller Karten kommen **ohne jede Kreuzung** aus.")
w("- Keine einzige überlappende Bausteinfläche wurde gefunden (`n_block_overlaps` = 0 auf allen 498 Karten).")
w("- Gute Ergebnisqualität bei den Standard-Ein-/Ausgangsübungen (`Uebung_011*`, `Uebung_070*`, "
  "`Uebung_010*`, `Uebung_012*`, `Uebung_201*`).")
w("")
w("---")
w("")
w("## 7. Empfehlungen")
w("")
w("1. **Beschreibungsband begrenzen.** Ab ca. 8 Zeilen sollte die Schrift im unteren Band kleiner "
  "skaliert oder die Beschreibung gekürzt werden; aktuell läuft der Text auf 13,9 % der Karten unten "
  "über den Rand. Der Textblock sollte außerdem eine harte Untergrenze (Sicherheitsabstand zum "
  "Kartenrand) erhalten.")
w("2. **Linksüberlauf der Portbeschriftungen.** 30,9 % der Karten schneiden Portnamen am linken Rand ab. "
  "Der Generator sollte Beschriftungen, die links aus dem Kartenformat ragen, nach rechts einrücken "
  "oder kürzen.")
w("3. **Titelband freihalten.** 40,2 % der Karten haben Bausteine, die bis in die Titel-/Beschreibungszone "
  "reichen. Die untere Grenze der Zeichenfläche sollte hart auf den Beginn des Titelbandes begrenzt und "
  "das Netzwerk bei Bedarf etwas kleiner skaliert werden.")
w("4. **Vertikale Zentrierung des Netzwerks.** Statt auf die mittlere Klemmhöhe zu zentrieren, könnte die "
  "gesamte Zeichnung (Blöcke + Leitungen) vertikal mittig zwischen oberem Rand und Textband ausgerichtet "
  "werden – das entfernt den großen Leerraum auf 27,5 % der Karten.")
w("5. **Instanznamen kollisionsfrei setzen.** Bei gestapelten Blöcken sollte der Name des unteren "
  "Bausteins in die Lücke (oder oberhalb des oberen Bausteins) ausweichen; heute entstehen auf 40 % "
  "der Karten überlappende Beschriftungen.")
w("6. **Großnetzwerke aufteilen.** Karten mit ≥ 10 Bausteinen (`Uebung_122`, `Uebung_122b`, `Uebung_056`, "
  "`Uebung_025`, `Uebung_080f` u. a.) auf mehrere Karten oder ein größeres Format verteilen – im "
  "7 × 9 cm-Format sind sie nicht mehr lesbar.")
w("7. **Pin-Inversionen weiter abbauen.** Die in `fix-TODO.md` gelisteten Fälle erklären einen großen Teil "
  "der Kreuzungen; jede dort erledigte Übung verbessert die Karte messbar.")
w("")
w("---")
w("")
w("## 8. Anhang: Gesamtranking aller 498 Karten")
w("")
w("Sortiert nach Gesamtpunktzahl (absteigend). Kreuz. = erkannte Linienkreuzungen, "
  "Textü. = Text-über-Text-Überlappungen, Leer unten = ungenutzte Kartenhöhe unterhalb des Netzwerks, "
  "Z. = Beschreibungszeilen.")
w("")
w("| Karte | Note | Punkte | Kreuz. | Textü. | Leer unten | Z. |")
w("|---|---|---:|---:|---:|---:|---:|")
for ex, grade, tot, cr, tov, gap, lines in D['all']:
    try:
        gapv = f"{float(gap):.0f} %"
    except Exception:
        gapv = "100 %"
    w(f"| `{ex}` | {grade} | {de(tot)} | {cr} | {tov} | {gapv} | {lines} |")
w("")
w("---")
w("")
w("## 9. Reproduzierbarkeit")
w("")
w("Die Auswertung ist vollständig automatisiert und wiederholbar:")
w("")
w("1. Jede Karte wird mit PyMuPDF geöffnet.")
w("2. Aus den Vektorzeichnungen werden alle Leiterbahnen (nach Renderer-Farbe) extrahiert und paarweise "
  "auf echte Schnittpunkte geprüft.")
w("3. Aus einer 150-dpi-Rasterisierung werden Tintendeckung, Clutter-Hotspot, Freiräume und "
  "Schwerpunktverschiebung bestimmt.")
w("4. Textzeilen (Bounding-Boxen) liefern Zeilenzahl, Überlappungen und Randüberstände.")
w("5. Gewichtung nach Abschnitt 1 → Gesamtpunktzahl → Note.")
w("")
w("> [!IMPORTANT]")
w("> Die Bewertung ist ein **heuristisches Modell**, keine objektive Wahrheit. Es priorisiert technische")
w("> Sauberkeit (Kreuzungsfreiheit, Lesbarkeit) stärker als künstlerische Gestaltung. Die visuelle")
w("> Gegenprüfung an Kontaktbögen bestätigt die Rangfolge an den Rändern (beste und schwächste Karten);")
w("> im Mittelfeld sind Verschiebungen um ±½ Note möglich.")
w("")

out = args.out
open(out, 'w', encoding='utf-8', newline='\n').write("\n".join(L))
print('wrote', out, len(L), 'lines')
