import json
import pandas as pd
import os

def personen_einlesen(pfad):
    """
    JSON Datei wird eingelesen und gibt alle gespeicherten Personenifos zurück
    Die Datei wird geöffnet, ausgelesen und als Python-Datenstruktur zurückgegeben.
    """
    with open(pfad, "r", encoding="utf-8") as ordner:
        daten = json.load(ordner)
    return daten

def extrahiere_name(personen):
    """
    sortierte Liste der Namen wird erstellt. Personen lassen sich später so in Dropdowns anzeigen.
    """
    namen = []
    for person in personen:
        name = "{}, {}".format(person["lastname"], person["firstname"])
        namen.append(name)
    return sorted(namen)

def person_finden_mit_name(name, daten):
    """
    in der Personenliste wird nach einer Person mit 'Nachname, Vorname' gesucht.
    es wird ein Personen-Dictionary zurückgegeben, wenn die Person gefunden wurde, ansonsten ein leeres Dictionary.
    """
    if name is None or name == "None":
        return {}
    
    teile = name.split(", ")
    if len(teile) != 2:
        return {}   
    
    nachname, vorname = teile

    return next((person for person in daten if person["lastname"] == nachname and person["firstname"] == vorname), {})

def person_finden_mit_id(id_wert, daten):
    """
    Person wird mithilfe der ID in Personliste gesucht. 
    Personen-Dictionary wird zurückgegeben, wenn die Person gefunden wurde, ansonsten ein leeres Dictionary.
    """
    if id_wert is None:
        return {}
    for person in daten:
        if str(person.get("id")) == str(id_wert):
            return person
    return {}

def txt_zu_df(pfad):
    """
    es wird geprüft, ob die Datei existiert, und sie wird dann als Tabelle (DataFrame) eingelesen.
    Wenn die Datei fehlt, kommt es zu einer Meldung und ein leerer DataFrame wird zurückgegeben
    """ 
    if os.path.exists(pfad):
        return pd.read_csv(pfad, encoding="utf-8")
    else:
        print("Datei wurde nicht gefunden:", pfad)
        return pd.DataFrame()

