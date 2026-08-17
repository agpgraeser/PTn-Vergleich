# PTn-Vergleich – Projektnotizen

> **📍 Aktueller Stand: siehe [`STATUS.md`](STATUS.md) – zu Sitzungsbeginn zuerst lesen.**
> **🔄 Am Ende jeder Arbeitssitzung `STATUS.md` aktualisieren** – auch ohne Aufforderung
> (Stichpunkte: was getan, Commit-Hashes, offene Punkte). Grundlage der Tagesdoku.
> Diese Datei = stabile Projektnotizen + Architektur; `STATUS.md` = lebender Stand.

## Projektbeschreibung
Web-App zum **Vergleich mehrerer PTn-Streckenmodelle**. Anwendungsfall im Kurs:
mehrere Teilnehmer haben für dieselbe Strecke je ein PTn-Modell bestimmt; hier
werden ihre Sprungantworten gemeinsam gezeichnet und – wenn eine Referenzmessung
vorliegt – über das Fehlerintegral objektiv verglichen.

Bis zu **vier Systeme**, je mit YA, t₀, UA, DU, KS, n (1…10) und TS.

- **Backend:** Python, FastAPI (`server.py`), Dateiimport in `excel_io.py`.
  Die **Fachlogik liegt im gemeinsamen Paket `agp_control_kern.ptn_vergleich`** –
  nicht in dieser App. Die PTn-Sprungantwort kommt von dort aus `ptn_zpk`,
  also dieselbe Kurve wie in **PTn-ZPK**.
- **Frontend:** `index.html` (eine Seite, vanilla JS), Plotly.js,
  AGP·Control-Design-System (`static/agp-design-system.css` + `static/app.css`).
- **Start:** `start.bat` → http://localhost:8011
- **Tests:** `venv\Scripts\python.exe -m pytest test_server.py`
  (Fachlogik-Tests im Kern: `agp_control_kern/tests/test_ptn_vergleich.py`)

## Herkunft (Stack-Vereinheitlichung 2026-08-17)
Neuaufbau der React/Vite/MUI-App **PTkPTn-Vergleiche** im Stack von
`RegelkreisSimulationen`, nach demselben Muster wie **PTn-ZPK**. Die alte App
bleibt unverändert lauffähig.

Portiert wurde:
- `src/utils/math.ts` → `agp_control_kern/ptn_vergleich.py` (T99-Tabelle,
  Sprungantworten, Fehlerintegral – Rechenweg 1:1)
- `src/utils/excelParser.ts` → `excel_io.py` (openpyxl statt xlsx)
- `src/utils/agpProjekt.ts` (256 Zeilen) **entfällt** – die AGP-Projektdatei
  kommt aus `agp_control_kern.projektdatei`, keine TypeScript-Nachbildung mehr
- `ParameterPanel.tsx` + `ResponseChart.tsx` + `OutputPage.tsx` → `index.html`

## Fachliche Kurzfassung
- Sprungantwort je System: y(t) = YA + KS·DU·y_norm(t; n, TS, t₀)
- Zeitachse ohne Messung: bis das **langsamste** System 99 % erreicht hat
  (T99-Tabelle je Ordnung, im Kern)
- Fehlerintegral je System: Σ (y_mess − y_modell)²·Δt – kleiner ist besser.
  Die Ergebnisseite sortiert danach und vergibt Ränge.

## AGP-Projektdatei
- **📂 je System:** lädt eine Teilnehmer-Projektdatei, nimmt das **erste
  PTn-Modell** aus Blatt `Modelle` (k_M→KS, n→n, T_M→TS), setzt den Namen auf
  den Fallnamen und leitet YA/t₀/UA/DU aus Blatt `Zeitverlaeufe` ab. Enthält die
  Datei keine Zeitverläufe, werden die Signalwerte von einem bereits gefüllten
  System übernommen. **PT1TT-Modelle werden übersprungen** – hier werden
  PTn-Modelle verglichen.
- **„Datei laden"** (Referenzmessung) nimmt **beides** entgegen: eine
  AGP-Projektdatei (Zeitverläufe werden zur Messung) oder eine Rohmessung.
  `/api/datei_laden` entscheidet selbst und meldet die erkannte Art zurück –
  der Anwender muss vorher nicht wissen, welche Datei er hat.

## Wichtige Design-Entscheidungen
- **Unvollständige Systeme werden übersprungen, nicht bemängelt.** Die
  Oberfläche rechnet beim Tippen live mit; ein Fehler bei jedem Zwischenstand
  wäre unbrauchbar. Stattdessen steht unter jeder Systemkarte ein Hinweis,
  *warum* sie noch nicht gezeichnet wird (welches Feld fehlt).
- **Panelbreite fest 400 px** (wie die Vorgänger-App, `App.tsx: '400px 1fr'`).
  Die anteilige Vorgabe des Design-Systems (min. 300 px) sprengt die
  Eingaberaster – das war in PTn-ZPK bereits ein Fehler.
- **Messung hat Vorrang bei der Zeitachse**, damit sie auch dann sichtbar ist,
  wenn noch kein einziges Modell vollständig ist.
- Seite bewusst **hell gepinnt**, weil die Plotly-Charts noch nicht
  dark-mode-fähig gestylt sind (wie die übrigen Apps der Familie).

## Farben
System 1…4 haben feste Farben (blau, rot, grün, orange). Dieselbe Farbe trägt
die Kurve im Diagramm, der Rand der Systemkarte und der Punkt in der
Ergebnistabelle – so ist ohne Legende klar, was zusammengehört.

## Offene Punkte
- Projektdatei **schreiben** ist im Server angelegt (`/api/projekt_xlsx`),
  in der Oberfläche aber noch nicht angebunden.
- Deployment (Render) noch nicht eingerichtet.
