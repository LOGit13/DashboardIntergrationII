import math
from datetime import datetime


def _parse_datetime(value):
    """Parst Datetime-Werte robust"""
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
    """Hilfsfunction um Werte aus Objekten oder Dicts zu lesen"""
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


def haversine_distance(lat1, lon1, lat2, lon2):
    """Berechnet die Entfernung zwischen zwei GPS-Punkten in Metern"""
    R = 6371000  # Erdradius in Metern
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def compute_elevation_profile(streckenpunkte):
    """
    Berechnet ein detailliertes Höhenprofil mit:
    - Distanz (km) für jeden Punkt
    - Höhe (m) für jeden Punkt
    - Anstieg (%) für jeden Punkt
    - Gefälle (%) für jeden Punkt
    
    Gibt eine Liste von Dicts zurück: [{km, hoehe, anstieg_prozent, gefaelle_prozent}, ...]
    """
    if not streckenpunkte or len(streckenpunkte) == 0:
        return []

    profile = []
    cumulative_distance = 0.0
    
    for i in range(len(streckenpunkte)):
        hoehe = _wert(streckenpunkte[i], "hoehe")
        
        # Distanz für diesen Punkt
        if i == 0:
            cumulative_distance = 0.0
        else:
            lat1 = _wert(streckenpunkte[i-1], "breite")
            lon1 = _wert(streckenpunkte[i-1], "laenge")
            lat2 = _wert(streckenpunkte[i], "breite")
            lon2 = _wert(streckenpunkte[i], "laenge")
            
            if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
                dist_m = haversine_distance(lat1, lon1, lat2, lon2)
                cumulative_distance += dist_m
        
        # Anstieg/Gefälle für diesen Punkt
        anstieg_prozent = 0.0
        gefaelle_prozent = 0.0
        
        if i > 0:
            hoehe_prev = _wert(streckenpunkte[i-1], "hoehe")
            if hoehe is not None and hoehe_prev is not None and cumulative_distance > 0:
                height_diff = hoehe - hoehe_prev
                # Strecke seit letztem Punkt in km
                if i > 0:
                    lat1 = _wert(streckenpunkte[i-1], "breite")
                    lon1 = _wert(streckenpunkte[i-1], "laenge")
                    lat2 = _wert(streckenpunkte[i], "breite")
                    lon2 = _wert(streckenpunkte[i], "laenge")
                    if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
                        dist_segment_m = haversine_distance(lat1, lon1, lat2, lon2)
                        if dist_segment_m > 0:
                            gradient = (height_diff / dist_segment_m) * 100
                            if gradient > 0:
                                anstieg_prozent = gradient
                            else:
                                gefaelle_prozent = abs(gradient)
        
        if hoehe is not None:
            profile.append({
                "km": cumulative_distance / 1000,
                "hoehe": hoehe,
                "anstieg_prozent": round(anstieg_prozent, 2),
                "gefaelle_prozent": round(gefaelle_prozent, 2),
                "index": i
            })
    
    return profile


def get_point_details_at_index(profile, index):
    """
    Gibt die Details für einen bestimmten Punkt im Profil zurück.
    """
    if not profile or index < 0 or index >= len(profile):
        return None
    
    return profile[index]


def get_segment_stats(streckenpunkte):
    """
    Berechnet Statistiken für das Höhenprofil.
    """
    if not streckenpunkte:
        return {
            "max_hoehe": None,
            "min_hoehe": None,
            "total_stieg": 0.0,
            "total_fall": 0.0
        }
    
    hoehen = [_wert(p, "hoehe") for p in streckenpunkte if _wert(p, "hoehe") is not None]
    
    if not hoehen:
        return {
            "max_hoehe": None,
            "min_hoehe": None,
            "total_stieg": 0.0,
            "total_fall": 0.0
        }
    
    max_hoehe = max(hoehen)
    min_hoehe = min(hoehen)
    
    total_stieg = 0.0
    total_fall = 0.0
    
    for i in range(1, len(streckenpunkte)):
        h1 = _wert(streckenpunkte[i-1], "hoehe")
        h2 = _wert(streckenpunkte[i], "hoehe")
        
        if h1 is not None and h2 is not None:
            diff = h2 - h1
            if diff > 0:
                total_stieg += diff
            else:
                total_fall += abs(diff)
    
    return {
        "max_hoehe": max_hoehe,
        "min_hoehe": min_hoehe,
        "total_stieg": round(total_stieg, 1),
        "total_fall": round(total_fall, 1)
    }
