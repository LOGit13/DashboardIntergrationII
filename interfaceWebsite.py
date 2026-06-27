import streamlit as st
import pandas as pd
import math
import os
import json
from PIL import Image
from streamlit_option_menu import option_menu

from DashboardIntergrationII.Personen_Verwaltung import benutzer_verwaltung

#import data_resampling
#from Benutzer_Verwaltung import funktion_verwaltung
#from Personen import read_data, Klasse_ekgdata, Klasse_person
#from CSV_analyse import Einteilung_Zonen, Power_Curve

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

json_datei_link = 'DashboardIntergrationII/Personen_Verwaltung/data/person_db_test.json'
#json_datei_einlesen = read_data.(json_datei_link)

roh_daten = os.path.join("data", "ekg_data")
sortierte_daten = os.path.join("data", "data_sortiert")

frequenz_faktor = 100
alter_pfad = "data/ekg_data/"
neuer_pad = "data/data_sortiert/"

#data_resampling.resample_and_changeLink_ekg_data (roh_daten, sortierte_daten, neuer_pad, alter_pfad, json_datei_link)

if selected == "Startseite":
    st.title("Willkommen zur EKG Analyse App")
    st.subheader("Einführung")
    st.write("Die Website dient als zentrale Plattform zur Verwaltung von Personen und deren EKG‑Messdaten. Sie ermöglicht das Anlegen und Bearbeiten von Nutzern, das Hochladen und Auswerten von EKG‑Aufzeichnungen sowie die visuelle Darstellung der Signale. Zusätzlich bietet sie Funktionen zur Analyse von CSV‑Dateien, sodass verschiedene Datenquellen übersichtlich verarbeitet und interpretiert werden können.")
    st.write("Bitte wählen Sie eine Option aus dem Menü auf der linken Seite aus, um fortzufahren.")
    st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        right: 10px;
        bottom: 10px;
        color: grey;
        font-size: 14px;
        z-index: 100;
        text-align: right;
    }
    </style>
    <div class="footer">
        Autor: Noah Reinermann<br>
        Autor: Lenn Oßwald
    </div>
    """,
    unsafe_allow_html=True
)


if selected == "Personen Verwaltung":
    st.title("Personen Verwaltung")
    st.write("Hier können Sie Personen verwalten.")

    option = st.segmented_control("Option wählen:", ["Neue Person anlegen", "Bestehende Nutzer aktualisieren", "Nutzer löschen"])

    if option == "Neue Person anlegen":
        #unser_id = benutzer_verwaltung.naechste_user_id(data_json)
        vorname = st.text_input("Vorname")
        nachname = st.text_input("Nachname")
        geburtsdatum = st.date_input("Geburtsdatum", min_value=pd.Timestamp('1900-01-01'), max_value=pd.Timestamp.now())

        bild_person = st.file_uploader("Profilbild hochladen", type=["jpg", "jpeg", "png"])
        bild_speichern = None
        #speichern des Bildes, wenn es hochgeladen wurde
        #if bild_person is not None:
         #   bild_ordner = f" hier fehlt noch andere Datein
        

