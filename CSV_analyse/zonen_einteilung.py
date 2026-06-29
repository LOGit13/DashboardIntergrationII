import pandas as pd
import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def aktivitaet_einlesen(dateipfad="data/activity.csv"):
    return pd.read_csv(dateipfad, encoding="utf-8")

def mittelwert_leistung(df):
    return df["PowerOriginal"].mean()

def maximale_leistung(df):
    return df["PowerOriginal"].max()

def maximale_herzfrequenz(df):
    return df["HeartRate"].max()

def zeitachse(dauer_s=1805, punkte=1804):
    return np.linspace(0, dauer_s, punkte)

def zonen_berechnung(max_herzfrequenz):
    return [0.50 * max_herzfrequenz, 0.60 * max_herzfrequenz, 0.70 * max_herzfrequenz, 0.80 * max_herzfrequenz, 0.90 * max_herzfrequenz, 1.00 * max_herzfrequenz]

def ekg_plot(df, max_herzfrequenz):
    zonen = zonen_berechnung(max_herzfrequenz)
    zeit = zeitachse()
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
    fig.update_layout(
        title="EKG und Leistung",
        xaxis_title="Zeit [s]",
        yaxis_title="Herzfrequenz [BPM]",
        yaxis2_title="Leistung [W]",
        legend=dict( x=1.05, y=1, bordercolor="black", borderwidth=1)
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
