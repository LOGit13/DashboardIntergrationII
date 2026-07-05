from fitparse import FitFile
from datetime import datetime
from GPX_Integration.parsers.gpx_parser import Streckenpunkt

def fit_einlesen(dateipfad):
    """
    Liest eine FIT-Datei ein und gibt eine Liste von Streckenpunkten zurück.
    """

    fitfile = FitFile(dateipfad)
    streckenpunkte = []

    for record in fitfile.get_messages("record"):
        daten = {}

        for field in record:
            daten[field.name] = field.value

        # GPS
        if "position_lat" in daten and "position_long" in daten:
            # FIT nutzt semicircles → umrechnen
            breite = daten["position_lat"] * (180 / 2**31)
            laenge = daten["position_long"] * (180 / 2**31)
        else:
            continue

        # Höhe
        hoehe = daten.get("altitude", None)

        # Zeit
        zeitpunkt = daten.get("timestamp", None)

        # Puls
        puls = daten.get("heart_rate", None)

        punkt = Streckenpunkt(
            breite=breite,
            laenge=laenge,
            hoehe=hoehe,
            zeitpunkt=zeitpunkt,
            puls=puls
        )

        streckenpunkte.append(punkt)

    return streckenpunkte
