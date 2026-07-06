class Aktivitaet:
    def __init__(self, name, datum, sportart, dauer=None, distanz=None):
        """Repräsentiert eine Trainingsaktivität mit Name, Datum, Sportart und optionalen Metriken.""" = name
        self.datum = datum
        self.sportart = sportart
        self.dauer = dauer
        self.distanz = distanz


class StreckenpunktDB:
    def __init__(self, aktivitaet_id, breite, laenge, hoehe=None, zeitpunkt=None, puls=None):
        """Repräsentiert einen einzelnen Trackpoint einer Aktivität mit GPS- und Vitaldaten.""" = aktivitaet_id
        self.breite = breite
        self.laenge = laenge
        self.hoehe = hoehe
        self.zeitpunkt = zeitpunkt
        self.puls = puls
