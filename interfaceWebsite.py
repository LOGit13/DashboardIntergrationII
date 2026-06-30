import streamlit as st
import pandas as pd
import os
import json
import math
from PIL import Image
from streamlit_option_menu import option_menu

from Personen import daten_einlesen, klasse_person, klasse_ekgdata
from Personen_Verwaltung import benutzer_verwaltung
from CSV_analyse import power_curve, zonen_einteilung
import data_sortiert


with st.sidebar:
    selected = option_menu(
        menu_title="Menü",
        options=["Startseite", "Personen Verwaltung", "EKG App", "CSV Analyse"],
        icons=["house", "people", "activity", "file-earmark-bar-graph"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#f0f2f6"},
            "icon": {"color": "blue", "font-size": "20px"},
            "nav-link": {"font-size": "18px", "text-align": "left", "margin":"5px"},
            "nav-link-selected": {"background-color": "#4CAF50"},
        }
    )

json_pfad = "data/person_db.json"
personen_data = daten_einlesen.personen_einlesen(json_pfad)

ordner_ekg = "data/ekg_data"
ordner_sortiert = "data/data_sortiert"

abtastrate = 100

if selected == "Startseite":
    st.title("Willkommen zur EKG Analyse App")
    st.subheader("Einführung")
    st.markdown("""
Die Website dient als zentrale Plattform zur Verwaltung von Personen und deren EKG‑Messdaten.

**Funktionen:**
- Personen anlegen und bearbeiten  
- EKG‑Daten hochladen und analysieren  
- Herzratenvariabilität berechnen  
- CSV‑Dateien auswerten
""")
    st.divider()


if selected == "Personen Verwaltung":
    st.title("Personen Verwaltung")
    st.write("Hier können Sie Personen verwalten.")

    option = st.segmented_control("Option wählen:", ["Neue Person anlegen", "Bestehende Nutzer aktualisieren", "Nutzer löschen"])

    if option == "Neue Person anlegen":
        person_id = benutzer_verwaltung.neue_person_id(personen_data)
        vorname = st.text_input("Vorname")
        nachname = st.text_input("Nachname")
        geburtsdatum = st.date_input("Geburtsdatum", min_value=pd.Timestamp('1900-01-01'), max_value=pd.Timestamp.now())

        bild_person = st.file_uploader("Profilbild hochladen", type=["jpg", "jpeg", "png"])
        bildpfad = None
        if bild_person:
            bildname = f"{person_id}_{bild_person.name}"
            bildpfad = f"data/pictures/{bildname}"
            with open(bildpfad, "wb") as f:
                f.write(bild_person.getbuffer())
            st.success(f"Bild {bild_person.name} gespeichert")

        ekg_datei = st.file_uploader("EKG-Datei hochladen", type=["txt"])
        ekg_tests = []
        if ekg_datei:
            ekg_id = benutzer_verwaltung.neue_ekg_id(personen_data)
            ekg_datum = st.text_input("Datum der EKG-Messung")
            ekg_name = f"{person_id}_{ekg_id}_{ekg_datei.name}"
            ekgpfad = f"data/ekg_data/{ekg_name}"
            with open(ekgpfad, "wb") as f:
                f.write(ekg_datei.getbuffer())
            st.success(f"EKG‑Datei {ekg_datei.name} gespeichert")
            ekg_tests.append({"id": ekg_id, "date": ekg_datum, "result_link": ekgpfad})

        person_info = {
            "id": person_id,
            "firstname": vorname,
            "lastname": nachname,
            "date_of_birth": str(geburtsdatum),
            "picture_path": bildpfad,
            "ekg_tests": ekg_tests,
        }

        if st.button("Person speichern"):
            benutzer_verwaltung.benutzer_speichern(json_pfad, person_info)
            st.success("Neue Person hinzugefügt")

    if option == "Bestehende Nutzer aktualisieren":
        auswahl = {f"{p['id']} - {p['firstname']} {p['lastname']}": p['id'] for p in personen_data}
        ausgewaelt = st.selectbox("Person auswählen", list(auswahl.keys()))
        ausgewaelt_id = auswahl[ausgewaelt]

        person_info = next((p for p in personen_data if p["id"] == ausgewaelt_id), None)

        if person_info:
            vorname = st.text_input("Vorname", value=person_info["firstname"])
            nachname = st.text_input("Nachname", value=person_info["lastname"])
            geburtsdatum = st.date_input("Geburtsdatum", value=pd.to_datetime(person_info["date_of_birth"]))

            if st.checkbox("Profilbild ändern"):
                neues_bild = st.file_uploader("Neues Profilbild hochladen", type=["jpg", "jpeg", "png"])
                if neues_bild:
                    bildname = f"{ausgewaelt_id}_{neues_bild.name}"
                    bildpfad = f"data/pictures/{bildname}"
                    with open(bildpfad, "wb") as f:
                        f.write(neues_bild.getbuffer())
                    st.success (f"Bild {neues_bild.name} gespeichert")
                    person_info ["picture_path"] = bildpfad

            if st.checkbox("Neue EKG-Datei hinzufügen"):
                neue_ekg = st.file_uploader("EKG-Datei hochladen", type=["txt"])
                if neue_ekg:
                    ekg_id = benutzer_verwaltung.neue_ekg_id(personen_data)
                    ekg_datum = st.text_input("Datum der neuen EKG-Messung")
                    ekg_name = f"{ausgewaelt_id}_{ekg_id}_{neue_ekg.name}"
                    ekgpfad = f"data/ekg_data/{ekg_name}"
                    with open(ekgpfad, "wb") as f:
                        f.write(neue_ekg.getbuffer())
                    st.success(f"EKG‑Datei {neue_ekg.name} gespeichert")
                    person_info["ekg_tests"].append({"id": ekg_id, "date": ekg_datum, "result_link": ekgpfad})

            person_info["firstname"] = vorname
            person_info["lastname"] = nachname
            person_info["date_of_birth"] = str(geburtsdatum)

            if st.button("Änderungen speichern"):
                benutzer_verwaltung.person_speichern(json_pfad, person_info, update=True)
                st.success("Personendaten aktualisiert")

    if option == "Nutzer löschen":
        auswahl = {f"{p['id']} - {p['firstname']} {p['lastname']}": p["id"] for p in personen_data}
        if len(auswahl) == 0:
            st.info("Es sind keine Personen vorhanden")
        else:
            ausgewaelt = st.selectbox("Person auswählen", list(auswahl.keys()))
            ausgewaelt_id = auswahl[ausgewaelt]

            person_info = next((p for p in personen_data if p["id"] == ausgewaelt_id),None)
            if person_info:
                st.write(f"**Vorname:** {person_info['firstname']}")
                st.write(f"**Nachname:** {person_info['lastname']}")
                st.write(f"**Geburtsdatum:** {person_info['date_of_birth']}")

                bestaetigung = st.checkbox(f"Ich möchte die Person **{person_info['firstname']} {person_info['lastname']}** wirklich löschen.")
                if bestaetigung:
                    if st.button("Person endgültig löschen"):
                        benutzer_verwaltung.person_loeschen(json_pfad, ausgewaelt_id)
                        st.success("Person wurde erfolgreich gelöscht")    

if selected == "EKG App":
    st.title("EKG Analyse")

    personen_namen = [f"{p['firstname']} {p['lastname']}" for p in personen_data]
    name = st.selectbox("Person auswählen", personen_namen)

    person = next(p for p in personen_data if f"{p['firstname']} {p['lastname']}" == name)
    instanz_person = klasse_person.Person(person)

    fenster1, fenster2 = st.columns(2, gap="large")

    with fenster1:
        st.subheader("Personendaten")
        st.write(f"**Vorname:** {person['firstname']}")
        st.write(f"**Nachname:** {person['lastname']}")
        st.write(f"**Geburtsdatum:** {person['date_of_birth']}")
        st.write(f"**Alter:** {instanz_person.berechne_alter()}")
        st.write(f"**Maximale Herzfrequenz:** {instanz_person.berechne_max_puls()}")

    with fenster2:
        bildpfad = person.get("picture_path", "data/pictures/none.jpg")
        try:
            st.image(Image.open(bildpfad))
        except:
            st.warning("Kein gültiges Bild gefunden")

    st.divider()
    ekg_ids = [t["id"] for t in person["ekg_tests"]]
    ekg_id = st.selectbox("EKG-Messung auswählen", ekg_ids)

    ekg_dict = klasse_ekgdata.EKGData.lade_ekg_nach_id(ekg_id, personen_data)
    ekg = klasse_ekgdata.EKGData(ekg_dict)

    ekg.zeitbereich(None, None, abtastrate)

    st.subheader("Zeitbereich auswählen")
    start, ende = st.slider("Zeitfenster", 0, math.ceil(ekg.zeitreihe_dauer()), (0, 20))
    ekg.zeitbereich(start, ende, abtastrate)

    st.plotly_chart(ekg.anzeigen_signale())
    st.divider()

    herzrate_gesamt, herzrate_bereich = ekg.herzrate()

    st.metric("Herzrate gesamt [BPM]", round(herzrate_gesamt, 2))
    st.metric("Herzrate im Bereich [BPM]", round(herzrate_bereich, 2))

    st.subheader("Herzvariabilität [HRV]")

    herzvariabilität_gesamt = ekg.herzratenvariabilität()
    herzvariabilität_bereich = ekg.herzratenvariabilität_bereich()

    st.write("**HRV gesamt:**", herzvariabilität_gesamt)
    st.write("**HRV Bereich:**", herzvariabilität_bereich)


