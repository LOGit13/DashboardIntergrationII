import streamlit as st
import pandas as pd
import math
import os
import json
from PIL import Image
from streamlit_option_menu import option_menu

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
        #unser_id = funktion_verwaltung.get_next_user_id(data_jsonperson_db))
        vorname = st.text_input("Vorname")
        nachname = st.text_input("Nachname")
        geburtsdatum = st.date_input("Geburtsdatum", min_value=pd.Timestamp('1900-01-01'), max_value=pd.Timestamp.now())
        
