import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def aktivitaet_einlesen(dateipfad="data/activity.csv"):
    return pd.read_csv(dateipfad, encoding="utf-8")

def bestleistung_berechnen(daten: pd.DataFrame, dauer_s: int, frequenz: int = 1) -> float:
    zeitabschnitt = dauer_s  * frequenz
    mittelwert = daten["PowerOriginal"].rolling(window=zeitabschnitt).mean()
    return float(mittelwert.max())

def powercurve_daten(daten: pd.DataFrame, frequenz: int=1)-> pd.DataFrame:
    ergebnis = []
    for dauer in range(1, 1806):
        best = bestleistung_berechnen(daten, dauer, frequenz)
        ergebnis.append([dauer, best])
    return pd.DataFrame(ergebnis, columns=["Zeitfenster [s]", "Leistungsmaximum [W]"])

def plot_powercurve(df: pd.DataFrame, start: int = 1, ende: int = 400, frequenz: int = 1):
    daten = powercurve_daten(df, frequenz)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daten["Zeitfenster [s]"],
        y=daten["Leistungsmaximum [W]"],
        mode="lines",
        name="Powercurve",
        line=dict(color="orange", width=2)
    ))

    zoom = daten[(daten["Zeitfenster [s]"] >= start) & (daten["Zeitfenster [s]"] <= ende)]
    fig.add_trace(go.Scatter(
        x=zoom["Zeitfenster [s]"],
        y=zoom["Leistungsmaximum [W]"],
        mode="lines",
        name="Zoom",
        line=dict(color="red", width=2)
    ))

    fig.update_layout(
        title="Powercurve",
        xaxis_title="Dauer [s]",
        yaxis_title="Leistung [W]"
    )
    return fig

def zoom_powercurve(df: pd.DataFrame, start: int = 1, ende: int = 400, frequenz: int = 1):
    daten = powercurve_daten(df, frequenz)
    zoom = daten[(daten["Zeitfenster [s]"] >= start) & (daten["Zeitfenster [s]"] <= ende)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=zoom["Zeitfenster [s]"],
        y=zoom["Leistungsmaximum [W]"],
        mode="lines",
        name="Zoom",
        line=dict(color="green", width=2)
    ))
    fig.update_layout(
        title="Powercurve (Zoom)",
        xaxis_title="Dauer [s]",
        yaxis_title="Leistung [W]"
    )
    return fig
