"""
server.py – FastAPI-Server des PTn-System-Vergleichs.

Liefert die HTML-Seite und die API aus – ein Server, ein Port, kein CORS.
Die Fachlogik liegt im gemeinsamen Paket `agp_control_kern.ptn_vergleich`,
damit die Programmfamilie dieselbe PTn-Sprungantwort benutzt.

Start: python -m uvicorn server:app --port 8011   (oder start.bat)
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agp_control_kern import projektdatei, ptn_vergleich

import excel_io

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

BASE = Path(__file__).resolve().parent

app = FastAPI(title="AGP-Control - PTn-System-Vergleich", version="1.0")


@app.middleware("http")
async def kein_browser_cache(request, call_next):
    """Browser duerfen HTML/JS/CSS nicht zwischenspeichern – sonst liefert
    Chrome nach einem App-Update tagelang eine alte Kopie aus."""
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# ─── Request-Modelle ─────────────────────────────────────────────────────────

class SystemEingabe(BaseModel):
    """Ein Teilnehmer-Modell. Unvollstaendige Systeme sind erlaubt – sie
    werden beim Rechnen uebersprungen, damit die Oberflaeche waehrend der
    Eingabe weiterzeichnen kann."""
    name: str = ""
    y_a: float | None = None
    t0: float | None = None
    u_a: float | None = None
    d_u: float | None = None
    k_s: float | None = None
    n: float | None = None
    T_s: float | None = None
    aktiv: bool = True


class VergleichRequest(BaseModel):
    systeme: list[SystemEingabe]
    zeit_daten: list[float] | None = None
    mess_daten: list[float] | None = None


class ProjektSpeichernRequest(BaseModel):
    projekt: dict | None = None
    fallname: str = "Vergleich"
    beschreibung: str = ""
    modelle: list | None = None
    programm: str = "PTn-Vergleich"
    aktion: str = "gespeichert"


# ─── API ─────────────────────────────────────────────────────────────────────

@app.post("/api/vergleich")
def vergleich(req: VergleichRequest):
    """Sprungantworten aller aktiven Systeme und – bei vorhandener
    Messung – das Fehlerintegral je System."""
    try:
        return ptn_vergleich.vergleich(
            [s.model_dump() for s in req.systeme],
            zeit_daten=req.zeit_daten, mess_daten=req.mess_daten,
        )
    except Exception as ex:                       # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Interner Fehler: {ex}")


@app.post("/api/messdaten")
async def messdaten(datei: UploadFile):
    """Liest eine Excel-Messdatei (Zeit | y | u)."""
    try:
        return excel_io.messdaten_lesen(await datei.read(), datei.filename or "")
    except excel_io.ExcelError as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@app.post("/api/datei_laden")
async def datei_laden(datei: UploadFile):
    """Nimmt AGP-Projektdatei ODER Rohmessung entgegen und entscheidet selbst.

    Rueckgabe hat immer das Feld `art`:
      "projekt"  – zusaetzlich modell (kann None sein), signalwerte, messung
      "messung"  – nur messung (wie /api/messdaten)

    So braucht die Oberflaeche nur einen Knopf; welche Datei der Anwender
    waehlt, muss er nicht vorher wissen.
    """
    inhalt = await datei.read()
    name = datei.filename or ""

    # Erst als Projektdatei versuchen – die ist am Blatt "Meta" erkennbar.
    try:
        projekt = projektdatei.lesen(inhalt)
    except projektdatei.ProjektdateiError:
        projekt = None

    if projekt is not None:
        messung = None
        zv = projekt.get("zeitverlaeufe")
        if zv and zv.get("daten"):
            messung = excel_io.messung_aus_zeitverlaeufen(zv, name)
        return {
            "art": "projekt",
            "fallname": (projekt.get("meta") or {}).get("fallname", ""),
            "modell": ptn_vergleich.ptn_modell_aus_projekt(projekt),
            "signalwerte": ptn_vergleich.signalwerte_aus_projekt(projekt),
            "messung": messung,
            "dateiname": name,
        }

    # Sonst als gewoehnliche Messdatei lesen
    try:
        return {"art": "messung", "messung": excel_io.messdaten_lesen(inhalt, name),
                "dateiname": name}
    except excel_io.ExcelError as ex:
        raise HTTPException(
            status_code=400,
            detail=f"Weder AGP-Projektdatei noch lesbare Messdatei: {ex}")


@app.post("/api/projekt_xlsx")
def projekt_xlsx(req: ProjektSpeichernRequest):
    """Erzeugt eine Projektdatei mit den verglichenen Modellen."""
    try:
        projekt = req.projekt
        if projekt is None:
            projekt = projektdatei.neu(fallname=req.fallname,
                                       beschreibung=req.beschreibung,
                                       programm="PTn-Vergleich")
        if req.modelle is not None:
            projekt["modelle"] = req.modelle
        if req.fallname:
            projekt.setdefault("meta", {})["fallname"] = req.fallname
        inhalt = projektdatei.schreiben(projekt, programm=req.programm,
                                        aktion=req.aktion)
        return Response(content=inhalt, media_type=XLSX_MIME)
    except projektdatei.ProjektdateiError as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "PTn-Vergleich-Server laeuft"}


# ─── HTML-Seite und statische Dateien ────────────────────────────────────────

@app.get("/")
def seite1():
    return FileResponse(BASE / "index.html")


app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
