# TODO: Karten mit zu vielen Bausteinen

Stand: 2026-10-15. Die Layout-Prüfung (`fix-TODO.md`) und die Kartenerzeugung sind für die meisten
Übungen sauber. Bei einigen Übungen passen die Bausteine aber nicht mehr auf die 70 mm × 90 mm
große Karte. Dort müssen wir noch etwas tun.

## Problem

Der Generator skaliert die x-Positionen der Bausteine auf den Bereich 48 bis 285 der Karte und die
y-Positionen auf den freien Platz zwischen den Pins. Liegen viele Bausteine in 4diac weit
auseinander, aber nur wenige in einer Spalte, landen sie auf der Karte übereinander. Bei
fünf oder mehr Bausteinen in einer Spalte reicht die Kartenhöhe nicht:

- die untersten Bausteine stoßen an den Übungsnamen am unteren Rand oder ragen darüber hinaus
- der Mindestabstand für den Instanznamen (`BLOCK_LABEL_GAP`) lässt sich nicht mehr einhalten

Beispiel: `Uebung_028b_AR` mit `THRESHOLD`, `HYSTERESIS`, `AD_TO_AR_NUM`, `AX_SPLIT_2` und
`CALIBRATE` in einer Spalte (`CALIBRATE` liegt unter dem Übungsnamen).

## Betroffene Übungen (bisher bekannt)

- `Uebung_028b_AR`, `Uebung_028b2_AR`
- `Uebung_028c_AR`, `Uebung_028c2_AR`, `Uebung_028c3_AR`
- vermutlich weitere Übungen mit fünf oder mehr Bausteinen in einer Spalte (noch nicht systematisch erfasst)

## Was wir ausprobiert haben

- `CALIBRATE` in 4diac unter `AX_SPLIT_2` verschieben (y=3500): die Layout-Warnung verschwindet, die
  Karte wird aber nicht besser. **Verworfen**, keine Änderung an `4diac_training1`.
- `AD_TO_AR_NUM` und `AX_SPLIT_2` nach oben, `CALIBRATE` bei y=1500 lassen: die Karte bleibt genauso
  voll. Das Problem ist die Anzahl der Bausteine, nicht ihre Reihenfolge.

## Ideen für eine Lösung

1. **Zweite Spalte im Generator:** Bausteine, die in 4diac nebeneinander liegen, auch auf der Karte
   nebeneinander setzen (x-Skalierung nicht auf 48 bis 285 stauchen, sondern Spalten erhalten).
2. **Karte automatisch in zwei Karten teilen**, wenn mehr als vier Bausteine in einer Spalte liegen
   (z. B. Eingangsseite und Ausgangsseite).
3. **Bausteine noch kleiner skalieren** (aktuell `BLOCK_SCALE = 0.96`): hilft nur begrenzt, weil die
   Schrift lesbar bleiben muss.
4. **Übungen vereinfachen:** `THRESHOLD`/`HYSTERESIS` in ein SubApp zusammenfassen, damit weniger
   Bausteine auf der Karte stehen.
5. **Warnung bewusst stehen lassen:** `fix-TODO.md` meldet die Karte weiter als
   „Baustein unglücklich platziert“. Das ist akzeptabel, solange wir die Karte nicht ändern.

## Entscheidung

Vorerst bleibt es bei Variante 5: eine Warnung schadet nicht, und die Karten sind für diese
Übungen ohnehin unübersichtlich. Wir kommen darauf zurück, sobald wir den Generator für
mehrspaltige Karten (Idee 1) erweitern wollen.
