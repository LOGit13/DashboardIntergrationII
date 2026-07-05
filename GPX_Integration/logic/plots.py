import plotly.graph_objects as go
from datetime import datetime
import math


def _wert(p, name):
    if p is None:
        return None
    if hasattr(p, name):
        return getattr(p, name)
    if isinstance(p, dict):
        return p.get(name)
    if hasattr(p, "__getitem__"):
        try:
            return p[name]
        except (KeyError, TypeError, IndexError):
            return None
    return None


def entfernung(p1, p2):
    R = 6371000
    try:
        lat1 = math.radians(float(_wert(p1, "breite")))
        lon1 = math.radians(float(_wert(p1, "laenge")))
        lat2 = math.radians(float(_wert(p2, "breite")))
        lon2 = math.radians(float(_wert(p2, "laenge")))
    except (TypeError, ValueError):
        return 0.0

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def daten_aus_streckenpunkten(streckenpunkte):
    if not streckenpunkte:
        return [], [], [], [], []

    zeit = []
    puls = []
    distanz = []
    geschwindigkeit = []
    pace = []

    gesamt_dist = 0.0

    for i, p in enumerate(streckenpunkte):
        if p is None:
            continue

        zeitpunkt = _wert(p, "zeitpunkt")
        if zeitpunkt is None:
            continue

        try:
            zeit_dt = datetime.fromisoformat(str(zeitpunkt))
        except (TypeError, ValueError):
            continue

        zeit.append(zeit_dt)
        puls.append(_wert(p, "puls"))

        if i > 0:
            d = entfernung(streckenpunkte[i-1], streckenpunkte[i])
            gesamt_dist += d
        distanz.append(gesamt_dist / 1000)

        if i > 0:
            t1_raw = _wert(streckenpunkte[i-1], "zeitpunkt")
            t2_raw = _wert(streckenpunkte[i], "zeitpunkt")
            try:
                t1 = datetime.fromisoformat(str(t1_raw)) if t1_raw is not None else None
                t2 = datetime.fromisoformat(str(t2_raw)) if t2_raw is not None else None
            except (TypeError, ValueError):
                t1 = None
                t2 = None

            if t1 is not None and t2 is not None:
                delta_t = (t2 - t1).total_seconds()
                if delta_t > 0:
                    v = (d/1000) / (delta_t/3600)
                    geschwindigkeit.append(v)
                    pace.append((delta_t/60) / (d/1000) if d > 0 else None)
                else:
                    geschwindigkeit.append(None)
                    pace.append(None)
            else:
                geschwindigkeit.append(None)
                pace.append(None)
        else:
            geschwindigkeit.append(None)
            pace.append(None)

    return zeit, puls, distanz, geschwindigkeit, pace


def grosser_interaktiver_plot(streckenpunkte):
    try:
        zeit, puls, distanz, geschw, pace = daten_aus_streckenpunkten(streckenpunkte)
    except Exception:
        zeit, puls, distanz, geschw, pace = [], [], [], [], []

    fig = go.Figure()
    if not zeit:
        fig.update_layout(title="Interaktiver Trainingsplot", xaxis=dict(title="Zeit"), height=600)
        fig.add_annotation(text="Keine verwertbaren Trackpunkte gefunden.", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
        return fig

    # Puls
    fig.add_trace(go.Scatter(
        x=zeit, y=puls,
        mode="lines",
        name="Puls",
        line=dict(color="red")
    ))

    # Geschwindigkeit
    fig.add_trace(go.Scatter(
        x=zeit, y=geschw,
        mode="lines",
        name="Geschwindigkeit (km/h)",
        line=dict(color="blue"),
        yaxis="y2"
    ))

    # Pace
    fig.add_trace(go.Scatter(
        x=zeit, y=pace,
        mode="lines",
        name="Pace (min/km)",
        line=dict(color="green"),
        yaxis="y3"
    ))

    # Distanz
    fig.add_trace(go.Scatter(
        x=zeit, y=distanz,
        mode="lines",
        name="Distanz (km)",
        line=dict(color="orange"),
        yaxis="y4"
    ))

    # Layout mit mehreren Achsen
    fig.update_layout(
        title="Interaktiver Trainingsplot",
        xaxis=dict(title="Zeit"),
        yaxis=dict(title="Puls"),
        yaxis2=dict(title="Geschwindigkeit (km/h)", overlaying="y", side="right"),
        yaxis3=dict(title="Pace (min/km)", overlaying="y", side="left", position=0.05),
        yaxis4=dict(title="Distanz (km)", overlaying="y", side="right", position=0.95),
        legend=dict(x=0, y=1.1),
        height=600
    )

    return fig
