import pandas as pd
import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

SEKUNDEN_PRO_MINUTE = 60

def aktivitaet_einlesen(dateipfad="data/activity.csv"):
    return pd.read_csv(dateipfad, encoding="utf-8")

def mittelwert_leistung(df):
    return df["PowerOriginal"].mean()

def maximale_leistung(df):
    return df["PowerOriginal"].max()

def maximale_herzfrequenz(df):
    return df["HeartRate"].max()

def zeitachse(punkte=1804, dauer_min=None):
    if punkte <= 1:
        return np.array([0.0])
    if dauer_min is None:
        return np.arange(punkte, dtype=float) / SEKUNDEN_PRO_MINUTE
    return np.linspace(0.0, float(dauer_min), punkte)

def gesamtdauer_min(df):
    return len(df) / SEKUNDEN_PRO_MINUTE

def zonen_berechnung(max_herzfrequenz):
    return [0.50 * max_herzfrequenz, 0.60 * max_herzfrequenz, 0.70 * max_herzfrequenz, 0.80 * max_herzfrequenz, 0.90 * max_herzfrequenz, 1.00 * max_herzfrequenz]

def inject_test_anomalies(df):
    df = df.copy()
    if len(df) < 10:
        return df

    n = len(df)
    mid = n // 2
    df.loc[mid, "HeartRate"] = df["HeartRate"].iloc[mid - 1] + 45

    dropout_start = max(1, n // 4)
    df.loc[dropout_start:dropout_start + 2, "PowerOriginal"] = 0

    delay_start = max(1, n // 3)
    df.loc[delay_start, "PowerOriginal"] = max(df["PowerOriginal"].iloc[delay_start - 1] + 40, df["PowerOriginal"].iloc[delay_start])
    if delay_start + 5 < n:
        df.loc[delay_start + 1:delay_start + 5, "HeartRate"] = df["HeartRate"].iloc[delay_start]

    unplausibel_idx = min(n - 2, n * 3 // 4)
    df.loc[unplausibel_idx, "HeartRate"] = max(df["HeartRate"].mean() + 90, 220)

    return df

def ekg_plot(df, max_herzfrequenz, anomalien=None):
    zonen = zonen_berechnung(max_herzfrequenz)
    zeit = zeitachse(len(df))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=zeit, y=df["HeartRate"], name="Herzfrequenz", line=dict(color="red")), secondary_y=False)
    fig.add_trace(go.Scatter(x=zeit, y=df["PowerOriginal"], name="Leistung", line=dict(color="yellow")), secondary_y=True)

    farben = ["#CCE5FF", "#99CCFF", "#66B2FF", "#3385FF", "#0052CC"]
    for i in range(5):
        fig.add_shape(
            type="rect",
            x0=0, x1=zeit[-1],
            y0=zonen[i], y1=zonen[i+1],
            xref="x", yref="y",
            fillcolor=farben[i],
            opacity=0.3,
            layer="below"
        )

    if anomalien is None:
        anomalien = erkenne_anomalien(df, zeit)

    for a in anomalien:
        fig.add_trace(go.Scatter(
            x=[a["x"]],
            y=[a["y"]],
            mode="markers",
            marker=dict(size=10, color="orange", symbol="x"),
            name=a["typ"],
            hovertext=a["beschreibung"],
            showlegend=False
        ), secondary_y=a.get("secondary_y", False))

    fig.update_layout(
        title="EKG und Leistung",
        xaxis_title="Zeit [min]",
        yaxis_title="Herzfrequenz [BPM]",
        yaxis2_title="Leistung [W]",
        legend=dict(x=1.05, y=1, bordercolor="black", borderwidth=1)
    )

    return fig

def leistung_zeit_in_zonen(df, max_herzfrequenz):
    herz = df["HeartRate"]
    power = df["PowerOriginal"]
    zonen = zonen_berechnung(max_herzfrequenz)

    zeit = [0]*5
    leistung =[[] for _ in range(5)]
    for herzfrequenz, p in zip(herz, power):
        for i in range(5):
            if zonen[i] <= herzfrequenz < zonen[i+1]:
                zeit[i] +=1
                leistung[i].append(p)
                break
    durchschnitt = [round(sum(w)/len(w),2) if w else 0 for w in leistung]
    zeit_min = [round(z/60,2) for z in zeit]

    return {
        "Trainingsbereich": ["Bereich 1","Bereich 2","Bereich 3","Bereich 4","Bereich 5"],
        "Zeit[min]": zeit_min,
        "Durchschnittsleistung [W]": durchschnitt
    }

def erkenne_anomalien(df, zeit=None):
    if zeit is None:
        zeit = zeitachse(len(df))

    anomalien = []
    herz = df["HeartRate"].to_numpy()
    leistung = df["PowerOriginal"].to_numpy()

    if len(herz) < 2:
        return anomalien

    herz_diff = np.diff(herz)
    leistung_diff = np.diff(leistung)

    for i in range(1, len(herz)):
        if herz_diff[i - 1] > 20 and abs(leistung[i] - leistung[i - 1]) < 10:
            anomalien.append({
                "typ": "HF-Spike",
                "x": zeit[i],
                "y": herz[i],
                "secondary_y": False,
                "beschreibung": "Plötzlicher HF-Anstieg ohne passende Leistungsänderung."})

    for i in range(len(leistung)):
        if leistung[i] < 10 and herz[i] > 80 and (i == 0 or leistung[i - 1] > 20):
            anomalien.append({
                "typ": "Leistungs-Dropout",
                "x": zeit[i],
                "y": leistung[i],
                "secondary_y": True,
                "beschreibung": "Leistung fällt kurzzeitig stark ab, obwohl die HF hoch bleibt."})

    fenster = min(SEKUNDEN_PRO_MINUTE, len(herz) // 4)
    if len(herz) >= fenster * 2:
        herz_start = np.mean(herz[:fenster])
        herz_ende = np.mean(herz[-fenster:])
        leistung_mittel = np.mean(leistung)
        if leistung_mittel > 30 and (herz_ende - herz_start) > 10:
            anomalien.append({
                "typ": "HF-Drift",
                "x": zeit[len(zeit) // 2],
                "y": herz[len(zeit) // 2],
                "secondary_y": False,
                "beschreibung": "Langsamer Anstieg der Herzfrequenz bei relativ konstanter Leistung."})

    for i in range(1, len(leistung)):
        if leistung_diff[i - 1] > 30:
            j_max = min(i + 10, len(herz) - 1)
            if herz[j_max] - herz[i] < 5:
                anomalien.append({
                    "typ": "Verzögerte HF-Reaktion",
                    "x": zeit[i],
                    "y": leistung[i],
                    "secondary_y": True,
                    "beschreibung": "Leistung steigt schnell an, die HF folgt aber nur verzögert."})

    for i in range(1, len(herz)):
        if abs(herz_diff[i - 1]) > 40 or herz[i] < 30 or herz[i] > 220:
            beschreibung = "Sprunghafte HF-Änderung oder unplausibler Wert."
            if herz[i] < 30 or herz[i] > 220:
                beschreibung = "Herzfrequenz liegt außerhalb typischer physiologischer Grenzen."
            anomalien.append({
                "typ": "Unplausibler HF-Wert",
                "x": zeit[i],
                "y": herz[i],
                "secondary_y": False,
                "beschreibung": beschreibung})

    return anomalien
   
