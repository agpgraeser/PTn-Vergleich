"""Tests der API und des Dateiimports.

Die Fachlogik ist im Kern getestet (agp_control_kern/tests/test_ptn_vergleich.py);
hier geht es um die Anbindung: Routen, Datenformat, Erkennung der Dateiart.
"""

import io

import numpy as np
import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from agp_control_kern import projektdatei, ptn_sprungantwort

import excel_io
from server import app

client = TestClient(app)


def sys_(name="S", y_a=0.0, t0=0.0, u_a=0.0, d_u=1.0, k_s=1.0, n=3, T_s=2.0, aktiv=True):
    return {"name": name, "y_a": y_a, "t0": t0, "u_a": u_a, "d_u": d_u,
            "k_s": k_s, "n": n, "T_s": T_s, "aktiv": aktiv}


def _mappe(zeilen) -> bytes:
    wb = Workbook()
    ws = wb.active
    for z in zeilen:
        ws.append(z)
    puffer = io.BytesIO()
    wb.save(puffer)
    return puffer.getvalue()


def _projektdatei(modelle=None, zeitverlaeufe=None) -> bytes:
    p = projektdatei.neu(fallname="Teilnehmer Test", programm="Test")
    if modelle is not None:
        p["modelle"] = modelle
    if zeitverlaeufe is not None:
        p["zeitverlaeufe"] = zeitverlaeufe
    return projektdatei.schreiben(p, programm="Test", aktion="Test")


# ── Grundfunktionen ─────────────────────────────────────────────────────────

def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_startseite_wird_ausgeliefert():
    r = client.get("/")
    assert r.status_code == 200
    assert "PTn-System-Vergleich" in r.text


# ── Vergleich ───────────────────────────────────────────────────────────────

def test_vergleich_rechnet_aktive_systeme():
    r = client.post("/api/vergleich", json={"systeme": [sys_(name="A"), sys_(name="B")]})
    assert r.status_code == 200
    e = r.json()
    assert [k["name"] for k in e["kurven"]] == ["A", "B"]
    assert len(e["zeit"]) == 1000
    assert len(e["kurven"][0]["daten"]) == len(e["zeit"])


def test_vergleich_ueberspringt_unvollstaendige_systeme():
    r = client.post("/api/vergleich", json={
        "systeme": [sys_(name="gut"), sys_(name="leer", T_s=None), sys_(name="aus", aktiv=False)]})
    e = r.json()
    assert [k["name"] for k in e["kurven"]] == ["gut"]


def test_vergleich_ohne_systeme_liefert_leere_zeitachse():
    e = client.post("/api/vergleich", json={"systeme": []}).json()
    assert e["zeit"] == [] and e["kurven"] == []


def test_vergleich_mit_messung_liefert_fehlerintegral():
    T_s, n, t0 = 2.0, 3, 0.0
    zeit = np.linspace(0, 40, 300)
    mess = ptn_sprungantwort(zeit, T_s, n, t0, 0.0, 1.0, 1.0)
    e = client.post("/api/vergleich", json={
        "systeme": [sys_(name="passt", n=3, T_s=2.0), sys_(name="daneben", n=6, T_s=2.0)],
        "zeit_daten": zeit.tolist(), "mess_daten": mess.tolist(),
    }).json()
    assert e["fehlerintegral"][0] == pytest.approx(0.0, abs=1e-12)
    assert e["fehlerintegral"][1] > e["fehlerintegral"][0]
    # Zeitachse der Messung wird uebernommen
    assert e["zeit"] == pytest.approx(zeit.tolist())


# ── Dateien laden ───────────────────────────────────────────────────────────

def test_datei_laden_erkennt_rohmessung():
    inhalt = _mappe([[0.0, 1.0, 5.0], [1.0, 2.0, 5.0], [2.0, 3.0, 5.0]])
    e = client.post("/api/datei_laden",
                    files={"datei": ("roh.xlsx", inhalt)}).json()
    assert e["art"] == "messung"
    assert e["messung"]["zeit"] == [0.0, 1.0, 2.0]


def test_datei_laden_erkennt_projektdatei_mit_modell():
    inhalt = _projektdatei(modelle=[
        {"Nr": 1, "Typ": "PT1TT", "Methode": "x", "k_M": 9, "n": 1, "T_M": 9},
        {"Nr": 2, "Typ": "PTn", "Methode": "ZPK", "k_M": 1.5, "n": 4, "T_M": 2.5},
    ])
    e = client.post("/api/datei_laden",
                    files={"datei": ("projekt.xlsx", inhalt)}).json()
    assert e["art"] == "projekt"
    assert e["fallname"] == "Teilnehmer Test"
    # PT1TT wird uebersprungen, das PTn-Modell kommt an
    assert e["modell"]["k_s"] == 1.5 and e["modell"]["n"] == 4 and e["modell"]["T_s"] == 2.5


def test_datei_laden_projektdatei_ohne_ptn_modell():
    inhalt = _projektdatei(modelle=[
        {"Nr": 1, "Typ": "PT1TT", "Methode": "x", "k_M": 9, "n": 1, "T_M": 9}])
    e = client.post("/api/datei_laden",
                    files={"datei": ("p.xlsx", inhalt)}).json()
    assert e["art"] == "projekt" and e["modell"] is None


def test_datei_laden_projektdatei_mit_zeitverlaeufen():
    inhalt = _projektdatei(
        modelle=[{"Nr": 1, "Typ": "PTn", "Methode": "ZPK", "k_M": 2, "n": 3, "T_M": 1.5}],
        # daten ist SPALTENweise: [t-Spalte, y-Spalte, u-Spalte]
        zeitverlaeufe={"spalten": ["t", "y", "u"],
                       "daten": [[0, 1, 2, 3], [20, 20, 22, 25], [0, 0, 10, 10]]})
    e = client.post("/api/datei_laden",
                    files={"datei": ("p.xlsx", inhalt)}).json()
    assert e["messung"]["zeit"] == [0, 1, 2, 3]
    assert e["messung"]["y_daten"] == [20, 20, 22, 25]
    assert e["signalwerte"]["y_a"] == 20
    assert e["signalwerte"]["d_u"] == 10


def test_datei_laden_meldet_unbrauchbare_datei():
    r = client.post("/api/datei_laden",
                    files={"datei": ("kaputt.xlsx", b"kein xlsx")})
    assert r.status_code == 400
    assert "detail" in r.json()


def test_zeitverlaeufe_umformung_ohne_stellgroesse():
    m = excel_io.messung_aus_zeitverlaeufen(
        {"spalten": ["t", "y"], "daten": [[0, 1], [5, 6]]}, "x.xlsx")
    assert m["zeit"] == [0, 1] and m["y_daten"] == [5, 6] and m["u_daten"] == []


def test_zeitverlaeufe_umformung_leer():
    assert excel_io.messung_aus_zeitverlaeufen({}, "x") is None
