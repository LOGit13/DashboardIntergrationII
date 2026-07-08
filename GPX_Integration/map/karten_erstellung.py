import folium


def _get_wert(p, name):
    """Hilfsfunction um Werte aus Objekten oder Dicts zu lesen"""
    if p is None:
        return None
    if hasattr(p, name):
        return getattr(p, name)
    if isinstance(p, dict):
        return p.get(name)
    return None


def karte_erstellen_fuer_streamlit(streckenpunkte):
    """
    Erstellt eine Folium-Karte mit rot gezeichneter Route.
    Die Karte ist zoombar und verschiebbar.
    """
    if not streckenpunkte or len(streckenpunkte) == 0:
        return folium.Map(location=[51.5, 10.0], zoom_start=5)

    start_breite = _get_wert(streckenpunkte[0], "breite")
    start_laenge = _get_wert(streckenpunkte[0], "laenge")

    if start_breite is None or start_laenge is None:
        return folium.Map(location=[51.5, 10.0], zoom_start=5)

    karte = folium.Map(
        location=[start_breite, start_laenge],
        zoom_start=14,
        tiles="OpenStreetMap"  # Standard Basemap
    )

    punkte_liste = []
    for p in streckenpunkte:
        breite = _get_wert(p, "breite")
        laenge = _get_wert(p, "laenge")
        
        if breite is not None and laenge is not None:
            punkte_liste.append([breite, laenge])

    if len(punkte_liste) > 1:
        folium.PolyLine(
            punkte_liste,
            color="red",
            weight=4,
            opacity=0.8
        ).add_to(karte)

        folium.CircleMarker(
            location=punkte_liste[0],
            radius=8,
            popup="Start",
            color="green",
            fill=True,
            fillColor="green"
        ).add_to(karte)

        folium.CircleMarker(
            location=punkte_liste[-1],
            radius=8,
            popup="Ende",
            color="red",
            fill=True,
            fillColor="red"
        ).add_to(karte)

    return karte
