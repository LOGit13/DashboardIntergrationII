import os
import json
import pandas as pd

# ---------------------------------------------------------
# Funktion: EKG-Daten aus einem Ordner ausdünnen und Links anpassen
# ---------------------------------------------------------

def sortiere_und_aktualisiere_ekg_daten(
        quellordner,
        zielordner,
        neuer_pfad_prefix,
        alter_pfad_prefix,
        json_datei,
        schrittweite=5):

    # JSON-Daten einlesen
    with open(json_datei, "r") as file:
        personen_liste = json.load(file)

    # Alle Dateien im Quellordner durchgehen
    for dateiname in os.listdir(quellordner):
        if dateiname.endswith(".txt"):

            # Pfad zur Originaldatei
            original_pfad = os.path.join(quellordner, dateiname)

            # Rohdaten laden
            df = pd.read_csv(original_pfad, sep="\t", header=None)

            # Daten ausdünnen (z.B. jeder 5. Wert)
            df_gekuerzt = df.iloc[::schrittweite, :]

            # Zielpfad erzeugen
            neuer_dateipfad = os.path.join(zielordner, dateiname).replace("\\", "/")

            # Neue Datei speichern
            df_gekuerzt.to_csv(neuer_dateipfad, sep="\t", index=False, header=False)

            # Links im JSON anpassen
            alter_link = f"{alter_pfad_prefix}{dateiname}"
            neuer_link = f"{neuer_pfad_prefix}{dateiname}"

            for person in personen_liste:
                for test in person["ekg_tests"]:
                    if test["result_link"].replace("\\", "/") == alter_link:
                        test["result_link"] = neuer_link

    # Aktualisierte JSON-Datei speichern
    with open("data/person_db_aktuell.json", "w") as f:
        json.dump(personen_liste, f, indent=4)


# ---------------------------------------------------------
# Hauptprogramm
# ---------------------------------------------------------
if __name__ == "__main__":

    quellordner = os.path.join("Data", "ekg_data")
    zielordner = os.path.join("Data", "data_sortiert")

    alter_prefix = "data/ekg_data/"
    neuer_prefix = "data/data_sortiert/"

    sortiere_und_aktualisiere_ekg_daten(
        quellordner,
        zielordner,
        neuer_prefix,
        alter_prefix,
        json_datei="data/person_db.json"
    )
