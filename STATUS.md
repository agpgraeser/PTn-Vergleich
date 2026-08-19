# STATUS – PTn-Vergleich

Lebendes Logbuch. Neueste Einträge oben.

---

## 2026-08-18 – Spec 39V1: Totzeit, unteres Diagramm, kompaktes Layout

**Was getan** (Commit `f2f0fd9`, Kern `48cb62f`)

- **Totzeit T_T (PTnTT):** Modell jetzt `G(s)=kS/(1+TS·s)^n · e^(−TT·s)`.
  Optionaler Parameter `t_t` im gemeinsamen Kern (`ptn_sprungantwort`,
  `vergleich`, `system_gueltig`, `zeitachse`) – **abwärtskompatibel**
  (t_t=0 = bisheriges PTn, Schwester-Apps unberührt). Neues `TT`-Feld je System.
- **Unteres Diagramm** (fehlte komplett) aus der Referenz `PTkPTn-Vergleiche`
  portiert: Umschalter **Stellgröße · Abweichung · Quadr. Abweichung · Σe²·Δt**.
  Abweichungsmodi = geladene Messung − eingegebene Systeme.
- **Excel-Stellgröße** (3. Spalte `u`) wird im unteren Diagramm (Modus
  Stellgröße) zusammen mit den berechneten Stellverläufen gezeigt.
- **Eingabe-Layout kompakter** (4 Systeme ohne Scrollen): Zeile 1 =
  Klickbox + Status/„unvollständig"-Text + Name (max 10) + 📂; Zeile 4 =
  KS, TS, TT, n in einer Zeile (n schmal).
- **Git gesichert vor Umbau:** Tag `stand-vor-39v1` (beide Repos), zuvor den
  offenen Kern-Bugfix (Zeitverläufe spaltenweise) committet.

**Tests / Doku**

| Suite | Ergebnis |
|---|---|
| `agp_control_kern/tests` | ✅ 92 grün (+4 Totzeit) |
| `PTn-Vergleich/test_server.py` | ✅ 14 grün (+1 API-Totzeit) |
| Grafische Testläufe | `Testlaeufe/` – 4 Spec-Testfälle + Feature-Demo, `README.md` |

Live in-Browser verifiziert (localhost:8011): alle 4 Modi, T_T-Verzögerung,
Abweichung (n=3 gegen PT3-Messung ≈ 0). Push löst Render-Deploy aus.

**Offene Punkte**

- [ ] Nach Render-Deploy: Live-URL `https://ptn-vergleich.onrender.com` prüfen.
- [ ] Fachliche Abnahme durch den Nutzer mit echten Teilnehmerdateien.

---

## 2026-08-17 – Projekt angelegt (Portierung aus React)

**Was getan**

- Neues Projekt `PTn-Vergleich` im Stack von `RegelkreisSimulationen`
  aufgebaut, nach demselben Muster wie `PTn-ZPK`. Die alte React-App
  `PTkPTn-Vergleiche` bleibt unverändert lauffähig.
- **Fachlogik in den gemeinsamen Kern gelegt:** `agp_control_kern/ptn_vergleich.py`
  (portiert aus `math.ts`; T99-Tabelle, Sprungantworten, Fehlerintegral,
  Auswertung der AGP-Projektdatei). Kern-Commit `cb72594`, gepusht.
- Die PTn-Sprungantwort kommt aus `ptn_zpk` – **dieselbe Kurve wie in PTn-ZPK**.
  Genau dafür liegt die Rechnung im Kern.
- `agpProjekt.ts` (256 Zeilen TypeScript-Nachbildung) **entfällt ersatzlos**.
- Oberfläche neu gebaut: vier Systemkarten mit fester Farbzuordnung,
  Ergebnisseite mit Rangliste nach Fehlerintegral.
- `/api/datei_laden` erkennt selbst, ob eine AGP-Projektdatei oder eine
  Rohmessung geladen wurde – ein Knopf für beides.

**Tests**

| Suite | Ergebnis |
|---|---|
| `agp_control_kern/tests/` | ✅ 87 grün – davon 30 neu für ptn_vergleich |
| `PTn-Vergleich/test_server.py` | ✅ grün – API, Dateierkennung, Projektdatei |

**Offene Punkte**

- [x] **Live unter https://ptn-vergleich.onrender.com** (2026-08-17).
      Fachlich geprüft: zwei Modelle gegen eine PT3-Referenzmessung ergeben
      Fehlerintegral 0,000 (passend) und 2,309 (falsche Ordnung), Rangfolge
      korrekt. Erreichbarkeit 15/15. Karte in der HdT-Oberfläche
      freigeschaltet.
- [ ] Projektdatei **schreiben** in der Oberfläche anbinden
      (Server-Route `/api/projekt_xlsx` existiert)
- [ ] Vergleich alte ./. neue App mit echten Teilnehmerdateien durch den Nutzer
- [ ] Karte in der HdT-Oberfläche verlinken, sobald die Render-URL feststeht
