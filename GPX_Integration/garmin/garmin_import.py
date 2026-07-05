import os
from garminconnect import Garmin

def garmin_aktivitaeten_holen(client, limit=10):
    """
    Holt die letzten Aktivitäten von Garmin Connect.
    """
    try:
        aktivitaeten = client.get_activities(0, limit)
        return aktivitaeten
    except Exception as e:
        print("Fehler beim Abrufen der Garmin-Aktivitäten:", e)
        return []


def garmin_datei_download(client, activity_id, zielordner="garmin_downloads"):
    """
    Lädt GPX/TCX/FIT einer Garmin-Aktivität herunter.
    """

    if not os.path.exists(zielordner):
        os.makedirs(zielordner)

    dateien = {}

    # GPX
    try:
        gpx = client.download_activity(activity_id, "gpx")
        gpx_path = os.path.join(zielordner, f"{activity_id}.gpx")
        with open(gpx_path, "wb") as f:
            f.write(gpx)
        dateien["gpx"] = gpx_path
    except:
        pass

    # TCX
    try:
        tcx = client.download_activity(activity_id, "tcx")
        tcx_path = os.path.join(zielordner, f"{activity_id}.tcx")
        with open(tcx_path, "wb") as f:
            f.write(tcx)
        dateien["tcx"] = tcx_path
    except:
        pass

    # FIT
    try:
        fit = client.download_activity(activity_id, "fit")
        fit_path = os.path.join(zielordner, f"{activity_id}.fit")
        with open(fit_path, "wb") as f:
            f.write(fit)
        dateien["fit"] = fit_path
    except:
        pass

    return dateien
