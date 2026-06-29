import os
import json
import pandas as pd

def tab_datei(pfad: str, daten: pd.DataFrame) -> None:
    with open(pfad, "w", encoding="utf-8") as f:
        for zeile in daten.itertuples(index=False, name=None):
            wert = [str(w) if pd.notna(w) else "" for w in zeile]
            f.write("\t".join(wert) + "\n")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def ekg_data_sortiert(eingabe: str, ausgabe: str, neu: str, alt: str, json_pfad: str, schritt: int = 5):
    if not os.path.isabs(json_pfad):
        json_pfad = os.path.join(BASE_DIR, json_pfad)
    if not os.path.isabs(eingabe):
        eingabe = os.path.join(BASE_DIR, eingabe)
    if not os.path.isabs(ausgabe):
        ausgabe = os.path.join(BASE_DIR, ausgabe)

    with open(json_pfad, "r", encoding="utf-8") as f:
        personen = json.load(f)

    os.makedirs(ausgabe, exist_ok=True)
    for datei in sorted(os.listdir(eingabe)):
        if datei.endswith(".txt"):
            pfad = os.path.join(eingabe, datei)
            daten = pd.read_csv(pfad, sep=r"\s+", header=None, engine="python")
            daten_res = daten.iloc[::schritt]

            ziel = os.path.join(ausgabe, datei).replace("\\", "/")
            tab_datei(ziel, daten_res)

            alt_link= f"{alt}{datei}"
            neu_link = f"{neu}{datei}"

            for person in personen:
                for test in person["ekg_tests"]:
                    if test["result_link"].replace("\\", "/") == alt_link:
                        test["result_link"] = neu_link

    with open(json_pfad, "w", encoding="utf-8") as f:
        json.dump(personen, f, indent=4)

if __name__== "__main__":
    eingabe = "data/ekg_data"
    ausgabe = "data/data_sortiert"

    neuer_link = "data/data_sortiert/"
    alter_link = "data/ekg_data/"

    ekg_data_sortiert(eingabe, ausgabe, neuer_link, alter_link, "data/person_db.json")
