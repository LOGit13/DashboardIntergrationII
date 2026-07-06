import math
from datetime import datetime


def _parse_datetime(value):
    """Konvertiert verschiedene Datetime-Formate robust in datetime-Objekte."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if hasattr(value, "to_pydatetime"):
        try:
            return value.to_pydatetime()
        except Exception:
            pass
    if hasattr(value, "isoformat"):
        try:
            return datetime.fromisoformat(str(value.isoformat()))
        except Exception:
            pass
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text)
        except ValueError:
            try:
                return datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                return None
    try:
        text = str(value).strip()
        if not text or text.lower() in {"none", "nan", "null"}:
            return None
        return datetime.fromisoformat(text)
    except Exception:
        return None


def _wert(p, name):
    """Extrahiert Werte sicher aus Objekten oder Dictionaries."""
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


def entfernung_berechnen(p1, p2):
    """
    Berechnet die Entfernung zwischen zwei GPS-Punkten in Metern.
    Formel: Haversine
    """
    R = 6371000  # Erdradius in Metern

    lat1 = math.radians(_wert(p1, "breite"))
    lon1 = math.radians(_wert(p1, "laenge"))
    lat2 = math.radians(_wert(p2, "breite"))
    lon2 = math.radians(_wert(p2, "laenge"))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


def gesamt_distanz(streckenpunkte):
    """
    Berechnet die gesamte Distanz einer Aktivität in Kilometern.
    """
    distanz = 0.0
    for i in range(len(streckenpunkte) - 1):
        distanz += entfernung_berechnen(streckenpunkte[i], streckenpunkte[i+1])
    return distanz / 1000  # in km


def gesamt_dauer(streckenpunkte):
    """
    Berechnet die gesamte Dauer einer Aktivität in Sekunden.
    """
    zeiten = [_wert(p, "zeitpunkt") for p in streckenpunkte if _wert(p, "zeitpunkt") is not None]

    if len(zeiten) < 2:
        return None

    start = _parse_datetime(zeiten[0])
    ende = _parse_datetime(zeiten[-1])

    if start is None or ende is None:
        return None

    return (ende - start).total_seconds()


def hoehenmeter(streckenpunkte):
    """
    Berechnet positive und negative Höhenmeter.
    """
    positiv = 0.0
    negativ = 0.0

    for i in range(len(streckenpunkte) - 1):
        h1 = _wert(streckenpunkte[i], "hoehe")
        h2 = _wert(streckenpunkte[i+1], "hoehe")

        if h1 is None or h2 is None:
            continue

        diff = h2 - h1

        if diff > 0:
            positiv += diff
        else:
            negativ += abs(diff)

    return positiv, negativ


def durchschnitt_puls(streckenpunkte):
    """
    Berechnet den durchschnittlichen Puls.
    """
    pulswerte = [_wert(p, "puls") for p in streckenpunkte if _wert(p, "puls") is not None]

    if len(pulswerte) == 0:
        return None

    return sum(pulswerte) / len(pulswerte)


def maximal_puls(streckenpunkte):
    """
    Gibt den maximalen Puls zurück.
    """
    pulswerte = [_wert(p, "puls") for p in streckenpunkte if _wert(p, "puls") is not None]

    if len(pulswerte) == 0:
        return None

    return max(pulswerte)


def durchschnittsgeschwindigkeit(distanz_km, dauer_sek):
    """Berechnet die durchschnittliche Geschwindigkeit in km/h aus Distanz und Dauer."""
    if distanz_km is None or dauer_sek is None:
        return None

    stunden = dauer_sek / 3600
    return distanz_km / stunden


def pace(distanz_km, dauer_sek):
    """Berechnet das Tempo (Pace) in Minuten pro Kilometer aus Distanz und Dauer."""
    if distanz_km is None or dauer_sek is None:
        return None

    minuten = dauer_sek / 60
    return minuten / distanz_km
