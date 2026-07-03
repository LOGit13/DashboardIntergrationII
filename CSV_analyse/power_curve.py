import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def aktivitaet_einlesen(dateipfad="data/activity.csv"):
    return pd.read_csv(dateipfad, encoding="utf-8")

def bestleistung_berechnen(daten: pd.DataFrame, dauer_min: int, frequenz: int = 1) -> float:
    zeitabschnitt = int(dauer_min * 60 * frequenz)
    if zeitabschnitt < 1:
        return 0.0
    mittelwert = daten["PowerOriginal"].rolling(window=zeitabschnitt).mean()
    return float(mittelwert.max())

def powercurve_daten(daten: pd.DataFrame, frequenz: int=1)-> pd.DataFrame:
    max_dauer_min = max(1, int(len(daten) / (60 * frequenz)))
    ergebnis = []
    for dauer in range(1, max_dauer_min + 1):
        best = bestleistung_berechnen(daten, dauer, frequenz)
        ergebnis.append([dauer, best])
    return pd.DataFrame(ergebnis, columns=["Zeitfenster [min]", "Leistungsmaximum [W]"])

def plot_powercurve(df: pd.DataFrame, start: int = 1, ende: int = 400, frequenz: int = 1):
    daten = powercurve_daten(df, frequenz)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daten["Zeitfenster [min]"],
        y=daten["Leistungsmaximum [W]"],
        mode="lines",
        name="Powercurve",
        line=dict(color="orange", width=2)
    ))

    zoom = daten[(daten["Zeitfenster [min]"] >= start) & (daten["Zeitfenster [min]"] <= ende)]
    fig.add_trace(go.Scatter(
        x=zoom["Zeitfenster [min]"],
        y=zoom["Leistungsmaximum [W]"],
        mode="lines",
        name="Zoom",
        line=dict(color="red", width=2)
    ))

    fig.update_layout(
        title="Powercurve",
        xaxis_title="Dauer [min]",
        yaxis_title="Leistung [W]"
    )
    return fig

def zoom_powercurve(df: pd.DataFrame, start: int = 1, ende: int = 400, frequenz: int = 1):
    daten = powercurve_daten(df, frequenz)
    zoom = daten[(daten["Zeitfenster [min]"] >= start) & (daten["Zeitfenster [min]"] <= ende)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=zoom["Zeitfenster [min]"],
        y=zoom["Leistungsmaximum [W]"],
        mode="lines",
        name="Zoom",
        line=dict(color="green", width=2)
    ))
    fig.update_layout(
        title="Powercurve (Zoom)",
        xaxis_title="Dauer [min]",
        yaxis_title="Leistung [W]"
    )
    return fig
