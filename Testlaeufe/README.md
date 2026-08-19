# Testläufe – Spec 39V1 (PTn-Vergleich, Totzeit + unteres Diagramm)

Grafische Dokumentation der in Spec 39V1 geforderten Testfälle. Die Kurven
werden mit **demselben Kern wie die App** gerechnet
(`agp_control_kern.ptn_vergleich`), sind also exakt der App-Output.

**Reproduzieren:** `python erzeuge_testlaeufe.py` (erzeugt die PNGs neu; benötigt
`numpy` + `matplotlib` – reines Doku-Werkzeug, nicht Teil der App-Abhängigkeiten).

Alle vier Konfigurationen wurden zusätzlich **live in der laufenden App**
(`localhost:8011`) geprüft: kompaktes 4-System-Layout, T_T-Feld, oberes und
unteres Diagramm mit den vier Modi. Testfall 1 (5 Ordnungen) wird in der App
in zwei Läufen eingegeben (App = 4 Systeme); die Figur unten zeigt der
Vollständigkeit halber alle fünf Ordnungen zusammen.

Gemeinsames Modell: `G(s) = kS / (1 + TS·s)^n · e^(−TT·s)`,
Sprungantwort `Y(s) = G(s)·DU·σ(s)·e^(−t₀·s)`.

## Testfälle

| Nr | YA | t₀ | UA | DU | kS | TS | TT | n | Figur |
|----|----|----|----|----|----|----|----|----|-------|
| 1 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 1, 3, 4, 9, 10 | `Testfall_1.png` |
| 2 | 0 | 0 | 0 | 1 | 1 | 1 | **5** | 3, 4, 10 | `Testfall_2.png` |
| 3 | 0 | **5** | 0 | 1 | 1 | 1 | 0 | 3, 4, 10 | `Testfall_3.png` |
| 4 | 0 | **5** | 0 | **0.5** | **0.5** | 1 | 0 | 3, 4, 10 | `Testfall_4.png` |

## Beobachtungen (aus den berechneten Kurven)

**Testfall 1** – reine PTn-Systeme. Höhere Ordnung ⇒ träger: n=1 läuft praktisch
sofort an (t≈0,02), n=10 erst bei t≈2,97; alle erreichen ~1,0 (Endwert kS·DU=1).

**Testfall 2** – Totzeit TT=5. Die Antwort bleibt bis **t = t₀+TT = 5** exakt 0
und läuft erst dann an (n=3 bei t≈5,21), während die **Stellgröße u(t) schon
bei t=0 springt**. Genau das ist die neue PTnTT-Fähigkeit.

**Testfall 3** – Sprungverschiebung t₀=5 (ohne Totzeit). Hier springen u(t) **und**
Antwort gemeinsam bei t=5. Die Ausgangskurven sind identisch zu Testfall 2 –
der Unterschied steckt allein im unteren Diagramm (u springt bei 0 vs. bei 5).
Das zeigt sauber: Totzeit verzögert nur den Ausgang, t₀ verschiebt das Signal.

**Testfall 4** – t₀=5 mit DU=0,5 und kS=0,5. Endwert = kS·DU = **0,25** (bestätigt),
Anlauf bei t≈5,3.

## Feature-Demo: unteres Diagramm (`Feature_Abweichung.png`)

Da die vier Testfälle keine Referenzmessung enthalten, zeigt eine Zusatzgrafik
das untere Diagramm mit einer **synthetischen PT3-Messung** und den Modellen
n=2/3/4:

- **Abweichung** (Modus 2): Messung − Modell je System.
- **Σe²·Δt** (Modus 4): laufendes Fehlerintegral. Rangfolge (kleiner = besser):

  | System | Σe²·Δt |
  |--------|--------|
  | n=3 | 0,00000 (trifft die PT3-Messung exakt) |
  | n=4 | 0,15625 |
  | n=2 | 0,18750 |

Das demonstriert Punkt „der Unterschied zwischen geladenem Systemverlauf und
den eingegebenen Systemen wird nach Anwahl angezeigt".
