import xml.etree.ElementTree as ET
from datetime import datetime
from GPX_Integration.parsers.gpx_parser import Streckenpunkt

def tcx_einlesen(dateipfad):
    """
    Liest eine TCX-Datei ein und gibt eine Liste von Streckenpunkten zurück.
    """

    baum = ET.parse(dateipfad)
    wurzel = baum.getroot()

    # TCX hat oft Namespaces
    namespace = wurzel.tag.split("}")[0].strip("{")
    ns = {"ns": namespace}

    streckenpunkte = []

    # Trackpoints finden
    for trkpt in wurzel.findall(".//ns:Trackpoint", ns):

        # Zeit
        time_tag = trkpt.find("ns:Time", ns)
        if time_tag is not None:
            zeit = time_tag.text.replace("Z", "+00:00")
            try:
                zeitpunkt = datetime.fromisoformat(zeit)
            except Exception:
                zeitpunkt = None
        else:
            zeitpunkt = None

        # Position
        pos = trkpt.find("ns:Position", ns)
        if pos is not None:
            lat_tag = pos.find("ns:LatitudeDegrees", ns)
            lon_tag = pos.find("ns:LongitudeDegrees", ns)

            if lat_tag is not None and lon_tag is not None:
                breite = float(lat_tag.text)
                laenge = float(lon_tag.text)
            else:
                continue
        else:
            continue

        # Höhe
        alt_tag = trkpt.find("ns:AltitudeMeters", ns)
        hoehe = float(alt_tag.text) if alt_tag is not None else None

        # Puls
        hr_tag = trkpt.find(".//ns:HeartRateBpm/ns:Value", ns)
        puls = int(hr_tag.text) if hr_tag is not None else None

        punkt = Streckenpunkt(
            breite=breite,
            laenge=laenge,
            hoehe=hoehe,
            zeitpunkt=zeitpunkt,
            puls=puls
        )

        streckenpunkte.append(punkt)

    return streckenpunkte
