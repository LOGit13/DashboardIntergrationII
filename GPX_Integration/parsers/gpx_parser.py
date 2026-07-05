import xml.etree.ElementTree as ET
from datetime import datetime


class Streckenpunkt:
    def __init__(self, breite, laenge, hoehe=None, zeitpunkt=None, puls=None):
        self.breite = breite      # Breitengrad
        self.laenge = laenge      # Längengrad
        self.hoehe = hoehe        # Höhe in Metern (optional)
        self.zeitpunkt = zeitpunkt  # Zeitpunkt (optional)
        self.puls = puls          # Herzfrequenz (optional)

    def __repr__(self):
        return f"Streckenpunkt({self.breite}, {self.laenge}, hoehe={self.hoehe}, zeit={self.zeitpunkt}, puls={self.puls})"


def gpx_einlesen(dateipfad):
    """
    Liest eine GPX-Datei ein und gibt eine Liste von Streckenpunkten zurück.
    """
    baum = ET.parse(dateipfad)
    wurzel = baum.getroot()

    # Namespace aus dem Root-Tag holen (GPX benutzt meistens Namespaces)
    namespace = wurzel.tag.split("}")[0].strip("{")
    ns = {"ns": namespace}

    streckenpunkte = []

    # Alle Trackpunkte (trkpt) finden
    for trkpt in wurzel.findall(".//ns:trkpt", ns):
        breite = float(trkpt.attrib.get("lat"))
        laenge = float(trkpt.attrib.get("lon"))

        # Höhe (ele) auslesen, falls vorhanden
        ele_tag = trkpt.find("ns:ele", ns)
        if ele_tag is not None:
            hoehe = float(ele_tag.text)
        else:
            hoehe = None

        # Zeit (time) auslesen, falls vorhanden
        time_tag = trkpt.find("ns:time", ns)
        if time_tag is not None:
            # GPX-Zeit ist meistens im ISO-Format mit Z am Ende
            text = time_tag.text.replace("Z", "+00:00")
            try:
                zeitpunkt = datetime.fromisoformat(text)
            except ValueError:
                zeitpunkt = None
        else:
            zeitpunkt = None

        # Puls (hr) auslesen, falls vorhanden (oft in Erweiterungen)
        hr_tag = trkpt.find(".//ns:hr", ns)
        if hr_tag is not None:
            try:
                puls = int(hr_tag.text)
            except ValueError:
                puls = None
        else:
            puls = None

        punkt = Streckenpunkt(
            breite=breite,
            laenge=laenge,
            hoehe=hoehe,
            zeitpunkt=zeitpunkt,
            puls=puls
        )
        streckenpunkte.append(punkt)

    return streckenpunkte




