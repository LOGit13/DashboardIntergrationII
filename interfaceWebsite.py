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
                benutzer_verwaltung.benutzer_speichern(json_pfad, person_info, aktualisieren=True)
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

    personen_namen = {f"{p['firstname']} {p['lastname']}": p["id"] for p in personen_data}
    name = st.selectbox("Person auswählen", list(personen_namen.keys()))
    person_id = personen_namen[name]


    person = daten_einlesen.person_finden_mit_id(person_id, personen_data)
    instanz_person = klasse_person.Person(person)

    tab_person, tab_ekg = st.tabs(["Personendaten", "EKG Analyse"])

    with tab_person:
        fenster1, fenster2 = st.columns(2, gap="large")

        with fenster1:
            st.subheader("Personendaten")
            st.write(f"**Vorname:** {person['firstname']}")
            st.write(f"**Nachname:** {person['lastname']}")
            st.write(f"**Geburtsdatum:** {person['date_of_birth']}")
            st.write(f"**Alter:** {instanz_person.berechne_alter()}")
            st.write(f"**Maximale Herzfrequenz:** {instanz_person.berechne_max_puls()}")

        with fenster2:
            bildpfad = person.get("picture_path") or "data/pictures/none.jpg"
            try:
                st.image(Image.open(bildpfad))
            except:
                st.warning("Kein gültiges Bild gefunden")

    

    with tab_ekg:
        st.subheader("EKG Analyse")
        st.write("Hier können Sie die EKG-Messungen der ausgewählten Person analysieren.")

        ekg_ids = [t["id"] for t in person["ekg_tests"]]
        ekg_id = st.selectbox("EKG-Messung auswählen", ekg_ids)

        ekg_dict = klasse_ekgdata.EKGData.lade_ekg_nach_id(ekg_id, personen_data)
        ekg = klasse_ekgdata.EKGData(ekg_dict)

        if ekg.df.empty:
            st.error("EKG-Datei konnte nicht geladen werden oder ist leer")
            st.stop()
        ekg.zeitbereich(None, None, abtastrate)

        tab_signal, tab_hr, tab_hrv = st.tabs(["Signal", "Herzrate", "HRV"])

        with tab_signal:
            st.subheader("Zeitbereich auswählen")
            max_zeitfenster = min(600, math.ceil(ekg.zeitreihe_dauer()))
            start, ende = st.slider("Zeitfenster", 0, max_zeitfenster, (0, 10))

            ekg.zeitbereich(start, ende, abtastrate)

            st.plotly_chart(ekg.anzeigen_signale())
            st.markdown("<small style='color: gray;'>Hinweis: Durch Anklicken der Legende können Signal und Peaks ein- oder ausgeblendet werden.</small>",unsafe_allow_html=True)
            st.metric("Länge der Zeitreihe [s]", round(ekg.zeitreihe_dauer(), 2))
            st.metric("Testdatum", ekg.test_datum())
            st.metric("Dateipfad", ekg.pfad)
       
        with tab_hr:
            st.subheader("Herzrate [BPM]")
            herzrate_gesamt, herzrate_bereich = ekg.herzrate()

            st.metric("Herzrate gesamt [BPM]", round(herzrate_gesamt, 2))
            st.metric("Herzrate im Bereich [BPM]", round(herzrate_bereich, 2))
            if herzrate_bereich == 0:
                st.warning("Herzrate im Bereich konnte nicht berechnet werden – zu wenige Peaks im ausgewählten Zeitfenster.")
            st.plotly_chart(ekg.plot_herzrate())
    
        with tab_hrv:
            st.subheader("Herzvariabilität [HRV]")

            col_left, col_right = st.columns(2)

            with col_left:
                st.write("**HRV gesamter Bereich:**")

                hrv_gesamt = ekg.herzratenvariabilität()

                if hrv_gesamt is None:
                    st.warning("HRV gesamt konnte nicht berechnet werden – Signal leer oder Abtastrate nicht gesetzt.")
       
                elif hrv_gesamt.get("HRV_MeanNN") is None:
                    st.warning("HRV gesamt konnte nicht berechnet werden – zu wenige Peaks oder schlechte Signalqualität.")
                else:
                    st.metric("HRV MeanNN [s]", round(hrv_gesamt["HRV_MeanNN"] / 1000, 3))
                    st.metric("HRV MinNN [s]", round(hrv_gesamt["HRV_MinNN"] / 1000, 3))
                    st.metric("HRV MaxNN [s]", round(hrv_gesamt["HRV_MaxNN"] / 1000, 3))

            with col_right:
                st.write("**HRV – ausgewählter Bereich:**")

                hrv_bereich = ekg.herzratenvariabilität_bereich()

                if hrv_bereich is None:
                    st.warning("HRV im Bereich konnte nicht berechnet werden – Signal leer oder Abtastrate nicht gesetzt.")
                elif hrv_bereich.get("HRV_MeanNN") is None:
                    st.warning("HRV im Bereich konnte nicht berechnet werden – zu wenige Peaks im Zeitfenster.")
                else:
                    st.metric("HRV MeanNN [s]", round(hrv_bereich["HRV_MeanNN"] / 1000, 3))
                    st.metric("HRV MinNN [s]", round(hrv_bereich["HRV_MinNN"] / 1000, 3))
                    st.metric("HRV MaxNN [s]", round(hrv_bereich["HRV_MaxNN"] / 1000, 3))

            status_gesamt, text_gesamt = ekg.pruefe_hrv(hrv_gesamt)
            status_bereich, text_bereich = ekg.pruefe_hrv(hrv_bereich)

            blink_css = """
            <style>
            @keyframes blink {
            50% { opacity: 0.4; }
            }
            .blink-box {
                animation: blink 1s infinite;
                padding: 15px;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                margin-top: 15px;
            }
            .blink-red {
            background-color: #ff4b4b;
            }
            .blink-green {
                background-color: #4CAF50;
            }
            </style>
            """

            st.markdown(blink_css, unsafe_allow_html=True)

    # Wenn einer der beiden Bereiche gefährlich ist → rot
            if status_gesamt == "danger" or status_bereich == "danger":
                st.markdown(
                    f"<div class='blink-box blink-red'>⚠️ WARNUNG<br>{text_gesamt}</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div class='blink-box blink-green'>✔️ Alles in Ordnung<br>{text_gesamt}</div>",
                    unsafe_allow_html=True
                )

            
            




if selected == "CSV Analyse":
    st.title("CSV Analyse")

    fenster_zonen, fenster_power = st.tabs(["Zonenanalyse", "Power Curve"])

    with fenster_zonen:
        max_hf = st.number_input("Maximale Herzfrequenz:", min_value=120, max_value=250, value=190)
        st.write(f"Max HF: {max_hf}")

        df = zonen_einteilung.aktivitaet_einlesen()
        fig = zonen_einteilung.ekg_plot(df, max_hf)
        st.plotly_chart(fig)

        fenster_leistung, fenster_zoneninfo = st.tabs(["Leistung", "Zoneninfo"])

        with fenster_leistung:
            st.metric ("Ø Leistung [W]", round(zonen_einteilung.mittelwert_leistung(df), 2))
            st.metric ("Max Leistung [W]", zonen_einteilung.maximale_leistung(df))
        with fenster_zoneninfo:
            daten = zonen_einteilung.leistung_zeit_in_zonen(df, max_hf)
            df_zonen = pd.DataFrame(daten).set_index("Trainingsbereich")
            st.dataframe(df_zonen)

    with fenster_power:
        df_power = power_curve.aktivitaet_einlesen()
        freq = st.number_input("Frequenz:", min_value=1, max_value=20, value=1)

        x_min = st.number_input("X-Min (Sekunden):", min_value=0, max_value=1800, value=0)
        x_max_raw = st.number_input("X-Max (Sekunden):", min_value=0, max_value=1800, value=300)
        x_max = x_max_raw + 5

        st.plotly_chart(power_curve.plot_powercurve(df_power, x_min, x_max, freq))
        st.plotly_chart(power_curve.zoom_powercurve(df_power, x_min, x_max, freq))
