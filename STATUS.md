# STATUS – PTn-Vergleich

Lebendes Logbuch. Neueste Einträge oben.

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

- [ ] Render-Deployment einrichten (`render.yaml` liegt bereit)
- [ ] Projektdatei **schreiben** in der Oberfläche anbinden
      (Server-Route `/api/projekt_xlsx` existiert)
- [ ] Vergleich alte ./. neue App mit echten Teilnehmerdateien durch den Nutzer
- [ ] Karte in der HdT-Oberfläche verlinken, sobald die Render-URL feststeht
