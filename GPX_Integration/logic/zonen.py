from datetime import datetime


def _parse_datetime(value):
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


def zonen_berechnen(streckenpunkte, hf_max):
    """
    Berechnet die Zeit in jeder Herzfrequenzzone.
    Gibt ein Dictionary zurück:
    {
        "Z1": Sekunden,
        "Z2": Sekunden,
        "Z3": Sekunden,
        "Z4": Sekunden,
        "Z5": Sekunden
    }
    """

    # Zonenbereiche
    z1_min, z1_max = hf_max * 0.50, hf_max * 0.60
    z2_min, z2_max = hf_max * 0.60, hf_max * 0.70
    z3_min, z3_max = hf_max * 0.70, hf_max * 0.80
    z4_min, z4_max = hf_max * 0.80, hf_max * 0.90
    z5_min, _ = hf_max * 0.90, hf_max * 1.00

    # Zeit in jeder Zone
    zonen = {
        "Z1": 0,
        "Z2": 0,
        "Z3": 0,
        "Z4": 0,
        "Z5": 0
    }

    # Wir gehen Punkt für Punkt durch
    for i in range(len(streckenpunkte) - 1):
        p1 = streckenpunkte[i]
        p2 = streckenpunkte[i + 1]

        if _wert(p1, "zeitpunkt") is None or _wert(p2, "zeitpunkt") is None:
            continue

        # Zeit zwischen zwei Punkten
        t1 = _parse_datetime(_wert(p1, "zeitpunkt"))
        t2 = _parse_datetime(_wert(p2, "zeitpunkt"))

        if t1 is None or t2 is None:
            continue

        delta = (t2 - t1).total_seconds()

        puls = _wert(p1, "puls")
        if puls is None:
            continue

        # Zone bestimmen
        if z1_min <= puls < z1_max:
            zonen["Z1"] += delta
        elif z2_min <= puls < z2_max:
            zonen["Z2"] += delta
        elif z3_min <= puls < z3_max:
            zonen["Z3"] += delta
        elif z4_min <= puls < z4_max:
            zonen["Z4"] += delta
        elif puls >= z5_min:
            zonen["Z5"] += delta

    return zonen


def zonen_prozent(zonen_dict):
    """
    Berechnet den Prozentanteil jeder Zone.
    """
    gesamt = sum(zonen_dict.values())
    if gesamt == 0:
        return {z: 0 for z in zonen_dict}

    return {zone: (sek / gesamt) * 100 for zone, sek in zonen_dict.items()}
