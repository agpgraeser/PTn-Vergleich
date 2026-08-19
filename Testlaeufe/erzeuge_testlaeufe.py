"""erzeuge_testlaeufe.py – Grafische Dokumentation der Testfaelle aus Spec 39V1.

Rechnet jede Konfiguration mit DEMSELBEN Kern wie die App
(agp_control_kern.ptn_vergleich) und legt PNG-Figuren im selben Ordner ab.
So ist die Dokumentation reproduzierbar und exakt der App-Output.

Aufruf:  python erzeuge_testlaeufe.py
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from agp_control_kern import ptn_vergleich
from agp_control_kern.ptn_zpk import ptn_sprungantwort, abweichung

HIER = Path(__file__).resolve().parent
FARBEN = ["#1976d2", "#e53935", "#43a047", "#fb8c00", "#8e24aa"]


def sys(name, n, y_a=0.0, t0=0.0, u_a=0.0, d_u=1.0, k_s=1.0, T_s=1.0, T_t=0.0):
    return dict(name=name, y_a=y_a, t0=t0, u_a=u_a, d_u=d_u,
                k_s=k_s, n=n, T_s=T_s, T_t=T_t, aktiv=True)


def anlaufzeit(t, y, schwelle=1e-3):
    """Erster Zeitpunkt, an dem die Antwort merklich anlaeuft."""
    idx = np.argmax(np.abs(y) > schwelle)
    return float(t[idx]) if np.any(np.abs(y) > schwelle) else None


def plot_fall(datei, titel, systeme, untertitel=""):
    erg = ptn_vergleich.vergleich(systeme)
    t = np.asarray(erg["zeit"])

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(9, 7), sharex=True, gridspec_kw={"height_ratios": [2, 1]})

    zeilen = []
    for k in erg["kurven"]:
        i = k["index"]
        daten = np.asarray(k["daten"])
        ax1.plot(t, daten, color=FARBEN[i % len(FARBEN)], lw=2, label=k["name"])
        zeilen.append((k["name"], anlaufzeit(t, daten), float(daten[-1])))

    ax1.set_title(titel + ("\n" + untertitel if untertitel else ""), fontsize=11)
    ax1.set_ylabel("Ausgangsgröße  y(t)")
    ax1.grid(alpha=0.3)
    ax1.legend(loc="lower right", fontsize=8, ncol=2)

    # Stellgröße (in jedem Testfall fuer alle Systeme gleich -> eine Linie)
    s0 = systeme[0]
    u = np.where(t <= s0["t0"], s0["u_a"], s0["u_a"] + s0["d_u"])
    ax2.plot(t, u, color="#555", lw=1.8, label="u(t)")
    ax2.set_ylabel("Stellgröße  u(t)")
    ax2.set_xlabel("Zeit")
    ax2.grid(alpha=0.3)
    ax2.legend(loc="lower right", fontsize=8)

    fig.tight_layout()
    fig.savefig(HIER / datei, dpi=110)
    plt.close(fig)
    return zeilen


def plot_abweichung(datei):
    """Feature-Demo: synthetische PT3-Messung, drei Modelle, Abweichung und
    laufendes Fehlerintegral – zeigt das untere Diagramm (Modi 2 und 4)."""
    tm = np.linspace(0, 18, 300)
    mess = ptn_sprungantwort(tm, 1.0, 3, 0.0, 0.0, 1.0, 1.0)   # PT3 als "Messung"
    systeme = [sys("n=2", 2), sys("n=3", 3), sys("n=4", 4)]
    erg = ptn_vergleich.vergleich(systeme, zeit_daten=tm.tolist(),
                                  mess_daten=mess.tolist())

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 9), sharex=True)
    ax1.plot(tm, mess, color="#555", lw=3, label="Messung (PT3)")
    for k in erg["kurven"]:
        i = k["index"]
        ax1.plot(tm, k["daten"], color=FARBEN[i], lw=2, ls="--", label=k["name"])
    ax1.set_title("Feature-Demo: Abweichung Messung ./. Modelle (unteres Diagramm)", fontsize=11)
    ax1.set_ylabel("y(t)"); ax1.grid(alpha=0.3); ax1.legend(fontsize=8)

    ranking = []
    for k in erg["kurven"]:
        i = k["index"]
        abw = abweichung(tm.tolist(), mess.tolist(), k["daten"])
        ax2.plot(tm, abw["diffs"], color=FARBEN[i], lw=2, label=k["name"])
        ax3.plot(tm, abw["kum_summe"], color=FARBEN[i], lw=2, label=k["name"])
        ranking.append((k["name"], abw["kum_summe_gesamt"]))
    ax2.set_ylabel("Abweichung"); ax2.grid(alpha=0.3); ax2.legend(fontsize=8)
    ax2.axhline(0, color="#999", lw=0.8)
    ax3.set_ylabel("Σ e²·Δt"); ax3.set_xlabel("Zeit"); ax3.grid(alpha=0.3); ax3.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(HIER / datei, dpi=110)
    plt.close(fig)
    return ranking


def main():
    print("Erzeuge Figuren in", HIER)

    z1 = plot_fall("Testfall_1.png",
                   "Testfall 1: PTn ohne Totzeit (YA=0, t₀=0, UA=0, DU=1, kS=1, TS=1, TT=0)",
                   [sys(f"n={n}", n) for n in (1, 3, 4, 9, 10)],
                   "Ordnungen n = 1, 3, 4, 9, 10 – hoehere Ordnung = traeger")

    z2 = plot_fall("Testfall_2.png",
                   "Testfall 2: PTnTT mit Totzeit TT=5 (t₀=0, DU=1, kS=1, TS=1)",
                   [sys(f"n={n}", n, T_t=5.0) for n in (3, 4, 10)],
                   "Antwort beginnt erst bei t = t₀+TT = 5; u(t) springt bereits bei t=0")

    z3 = plot_fall("Testfall_3.png",
                   "Testfall 3: Sprungverschiebung t₀=5 (DU=1, kS=1, TS=1, TT=0)",
                   [sys(f"n={n}", n, t0=5.0) for n in (3, 4, 10)],
                   "u(t) und Antwort beginnen bei t₀=5")

    z4 = plot_fall("Testfall_4.png",
                   "Testfall 4: t₀=5, DU=0.5, kS=0.5 (TS=1, TT=0)",
                   [sys(f"n={n}", n, t0=5.0, d_u=0.5, k_s=0.5) for n in (3, 4, 10)],
                   "Endwert = kS·DU = 0.25")

    rank = plot_abweichung("Feature_Abweichung.png")

    # Kurzzahlen fuer den Bericht ausgeben
    def zeig(name, zeilen):
        print(f"\n{name}:")
        for nm, anlauf, endw in zeilen:
            a = f"{anlauf:.2f}" if anlauf is not None else "-"
            print(f"   {nm:6s} Anlauf t={a:>6s}  Endwert={endw:.4f}")

    zeig("Testfall 1", z1)
    zeig("Testfall 2 (TT=5)", z2)
    zeig("Testfall 3 (t0=5)", z3)
    zeig("Testfall 4", z4)
    print("\nFeature Abweichung – Fehlerintegral (kleiner = besser):")
    for nm, fi in sorted(rank, key=lambda x: x[1]):
        print(f"   {nm:6s} Σe²·Δt = {fi:.5f}")
    print("\nFertig.")


if __name__ == "__main__":
    main()
