from GPX_Integration.logic.statistiken import (
    gesamt_distanz,
    gesamt_dauer,
    hoehenmeter,
    durchschnitt_puls,
    maximal_puls,
    durchschnittsgeschwindigkeit,
    pace
)

from GPX_Integration.logic.zonen import zonen_berechnen, zonen_prozent
from GPX_Integration.database.training_db import aktivitaet_holen


def statistik_zusammenfassung(aktivitaet_id, streckenpunkte, hf_max=190):
    """
    Erstellt eine komplette Zusammenfassung aller Statistiken einer Aktivität.
    Gibt ein Dictionary zurück.
    """

    # Basisdaten aus der Aktivität
    aktivitaet = aktivitaet_holen(aktivitaet_id)

    # Statistiken berechnen
    distanz_km = gesamt_distanz(streckenpunkte)
    dauer_sek = gesamt_dauer(streckenpunkte)
    hm_pos, hm_neg = hoehenmeter(streckenpunkte)
    puls_avg = durchschnitt_puls(streckenpunkte)
    puls_max = maximal_puls(streckenpunkte)
    geschw = durchschnittsgeschwindigkeit(distanz_km, dauer_sek)
    pace_min_km = pace(distanz_km, dauer_sek)

    # Zonen
    zonen = zonen_berechnen(streckenpunkte, hf_max)
    zonen_pct = zonen_prozent(zonen)

    aktivitaet_name = aktivitaet["name"] if aktivitaet else None
    aktivitaet_datum = aktivitaet["datum"] if aktivitaet else None
    aktivitaet_sportart = aktivitaet["sportart"] if aktivitaet else None

    return {
        "aktivitaet_id": aktivitaet_id,
        "name": aktivitaet_name,
        "datum": aktivitaet_datum,
        "sportart": aktivitaet_sportart,

        "distanz_km": distanz_km,
        "dauer_sek": dauer_sek,
        "hoehenmeter_positiv": hm_pos,
        "hoehenmeter_negativ": hm_neg,

        "puls_avg": puls_avg,
        "puls_max": puls_max,

        "geschwindigkeit_kmh": geschw,
        "pace_min_km": pace_min_km,

        "zonen_sekunden": zonen,
        "zonen_prozent": zonen_pct
    }
