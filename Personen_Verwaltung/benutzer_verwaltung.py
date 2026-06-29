import json

def neue_person_id(personen):
    vorhandene_ids = []
    for person in personen:
        if "id" in person:
            vorhandene_ids.append(int(person["id"]))
    if not vorhandene_ids:
        return 1
    return max(vorhandene_ids) + 1

def neue_ekg_id(personen):
    vorhandene_ids = []
    for person in personen:
        ekg_liste = person.get("ekg_tests", [])
        for eintrag in ekg_liste:
            if "id" in eintrag:
                vorhandene_ids.append(int(eintrag["id"]))
    if not vorhandene_ids:
        return 1
    return max(vorhandene_ids) + 1

def benutzer_speichern(pfad_json, benutzer_info, aktualisieren=False):
    with open(pfad_json, "r" , encoding = "utf-8") as datei:
        personen = json.load(datei)

    if aktualisieren:
        gefunden = False
        for person in personen:
            if person.get("id") == benutzer_info.get("id"):
                person.update(benutzer_info)
                gefunden = True
                break
        if not gefunden:
            raise ValueError("Benutzer wurde nicht gefunden.")
    else:
        benutzer_info["id"] = neue_person_id(personen)
        personen.append(benutzer_info)

    with open(pfad_json, "w", encoding="utf-8") as datei:
        json.dump(personen, datei, indent=4, ensure_ascii=False)

