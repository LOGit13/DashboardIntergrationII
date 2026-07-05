from GPX_Integration.parsers.gpx_parser import gpx_einlesen
from GPX_Integration.database.models import Aktivitaet, StreckenpunktDB
from GPX_Integration.database.training_db import aktivitaet_speichern, streckenpunkt_speichern

def gpx_in_datenbank_speichern(dateipfad, name_der_aktivitaet, sportart="Laufen"):
    """
    Liest eine GPX-Datei ein und speichert die Aktivität + alle Streckenpunkte in der Datenbank.
    Gibt die ID der gespeicherten Aktivität zurück.
    """

    # GPX-Datei einlesen
    punkte = gpx_einlesen(dateipfad)

    # Aktivität anlegen (Datum könnte man später aus GPX lesen)
    aktivitaet = Aktivitaet(
        name=name_der_aktivitaet,
        datum="unbekannt",   # später automatisch aus GPX-Zeit ableitbar
        sportart=sportart,
        dauer=None,
        distanz=None
    )

    aktivitaet_id = aktivitaet_speichern(aktivitaet)

    # Streckenpunkte speichern
    for p in punkte:
        punkt_db = StreckenpunktDB(
            aktivitaet_id=aktivitaet_id,
            breite=p.breite,
            laenge=p.laenge,
            hoehe=p.hoehe,
            zeitpunkt=str(p.zeitpunkt) if p.zeitpunkt else None,
            puls=p.puls
        )
        streckenpunkt_speichern(punkt_db)

    return aktivitaet_id
