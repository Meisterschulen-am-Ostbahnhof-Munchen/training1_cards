# TODO: Karten mit zu vielen Bausteinen

Stand: 2026-11-01. **Gelöst** (siehe „Entscheidung" unten) – `generate_cards.py` erkennt jetzt
automatisch, wenn eine Spalte von Bausteinen (oder ein einzelner, sehr großer Baustein wie bei
`Uebung_009a_AX`) nach dem normalen Stapeln immer noch nicht auf die Karte passt, und skaliert
genau diese Bausteine zusätzlich herunter, bis sie ohne Überlappung und ohne über den Kartenrand
bzw. den Übungsnamen hinauszuragen passen (Idee 3 unten, aber nur lokal für die betroffene Spalte
statt global). Die Textgröße schrumpft dabei proportional mit, bleibt aber lesbar genug für die
betroffenen Fälle (`Uebung_028b_AR`, `Uebung_028b2_AR`, `Uebung_028c_AR`, `Uebung_028c2_AR`,
`Uebung_028c3_AR`, `Uebung_009a_AX`). Der folgende Problem-/Ideenteil bleibt als Hintergrund stehen.

Vorheriger Stand: 2026-10-15. Die Layout-Prüfung (`fix-TODO.md`) und die Kartenerzeugung sind für
die meisten Übungen sauber. Bei einigen Übungen passten die Bausteine aber nicht mehr auf die
70 mm × 90 mm große Karte.

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

**2026-11-01 – umgesetzt** (Branch `fix/Todos_scaling_und_platzierung`): Variante 3 (zusätzliches
Herunterskalieren), aber nicht global über `BLOCK_SCALE`, sondern automatisch und nur für die
Bausteine, die nach dem normalen Stapeln noch nicht auf die Karte passen. Dazu gruppiert der
Generator die Bausteine einer Karte nach horizontaler Überlappung („Spalten"), ermittelt pro Spalte
die tatsächlich benötigte Höhe (nur Bausteine, die sich wirklich gegenseitig überlappen, werden
übereinandergestapelt; Bausteine ohne echte Überlappung teilen sich eine Reihe) inklusive
`BLOCK_LABEL_GAP` zwischen den Instanznamen, und schrumpft andernfalls genau diese Spalte (Breite,
Höhe, Schrift, Portabstände einheitlich) um den fehlenden Faktor, bevor sie neu gestapelt wird.
Dadurch bleiben einfache Karten unverändert, während überfüllte Karten (die oben genannten
`028b*`/`028c*`-Übungen sowie `Uebung_009a_AX` mit einem einzelnen, sehr großen Baustein) jetzt
vollständig und überlappungsfrei auf die Karte passen. Idee 1 (echte mehrspaltige Layouts) bleibt
eine mögliche spätere Verbesserung, ist aber durch diesen Fix nicht mehr dringend.

<details>
<summary>Alte Entscheidung (2026-10-15, überholt)</summary>

Vorerst bleibt es bei Variante 5: eine Warnung schadet nicht, und die Karten sind für diese
Übungen ohnehin unübersichtlich. Wir kommen darauf zurück, sobald wir den Generator für
mehrspaltige Karten (Idee 1) erweitern wollen.

</details>
