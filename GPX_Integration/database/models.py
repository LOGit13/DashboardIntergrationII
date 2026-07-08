class Aktivitaet:
    """
    Repräsentiert eine Trainingsaktivität mit Name, Datum und Sportart
    sowie optionalen Leistungsdaten wie Dauer und Distanz. Wird zur
    Verwaltung und Analyse von aufgezeichneten Trainingseinheiten genutzt.
    """
    def __init__(self, name, datum, sportart, dauer=None, distanz=None):
        """Repräsentiert eine Trainingsaktivität mit Name, Datum, Sportart und optionalen Metriken."""
        self.name = name
        self.datum = datum
        self.sportart = sportart
        self.dauer = dauer
        self.distanz = distanz


class StreckenpunktDB:
    """
    Repräsentiert einen einzelnen GPS‑Trackpunkt mit Koordinaten, Höhe,
    Zeitstempel und optionaler Herzfrequenz. Wird zur Analyse und Darstellung
    von GPX‑basierten Trainingsstrecken verwendet.
    """
    def __init__(self, aktivitaet_id, breite, laenge, hoehe=None, zeitpunkt=None, puls=None):
        """Repräsentiert einen einzelnen Trackpoint einer Aktivität mit GPS- und Vitaldaten."""
        self.aktivitaet_id = aktivitaet_id
        self.breite = breite
        self.laenge = laenge
        self.hoehe = hoehe
        self.zeitpunkt = zeitpunkt
        self.puls = puls
