import streamlit as st
import pandas as pd
import os
import io
import base64
from PIL import Image
from streamlit_option_menu import option_menu

from Personen_Verwaltung import benutzer_verwaltung

THEME_OPTIONS = ["White Theme", "Red Theme", "Blue Theme"]


def get_image_data_uri(image_bytes: bytes, image_format: str = "png") -> str:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/{image_format};base64,{encoded}"


def build_theme_css(theme_choice: str, bg_data_uri: str | None) -> str:
    if theme_choice == "Red Theme":
        background_color = "#FDE8E8"
        text_color = "#7F1D1D"
        overlay_bg = "rgba(253, 232, 232, 0.88)"
        sidebar_bg = "#881B1B"
        sidebar_color = "#FFFFFF"
    elif theme_choice == "Blue Theme":
        background_color = "#EAF2FB"
        text_color = "#0f1f3d"
        overlay_bg = "rgba(255, 255, 255, 0.88)"
        sidebar_bg = "#1E3A8A"
        sidebar_color = "#ffffff"
    else:
        background_color = "#FFFFFF"
        text_color = "#111111"
        overlay_bg = "rgba(255, 255, 255, 0.88)"
        sidebar_bg = "#f0f2f6"
        sidebar_color = "#111111"

    bg_style = f"background-color: {background_color};"
    if bg_data_uri:
        bg_style = (
            f'background-image: url("{bg_data_uri}"); '
            "background-size: cover; background-position: center;"
        )

    return f"""
    <style>
        [data-testid="stAppViewContainer"] {{ {bg_style} }}
        [data-testid="stAppViewContainer"] * {{ color: {text_color} !important; }}
        [data-testid="stAppViewContainer"] {{ background-color: {background_color}; }}
        [data-testid="stAppViewContainer"] div {{ color: {text_color} !important; }}
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; color: {sidebar_color} !important; }}
        [data-testid="stSidebar"] * {{ color: {sidebar_color} !important; }}
        .css-1d391kg {{ background-color: {overlay_bg} !important; color: {text_color} !important; }}
        .css-18e3th9 {{ }}
        .st-bc {{ color: {text_color} !important; }}
        button, input, textarea, select {{ color: {text_color} !important; }}
    </style>
    """

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

if "theme_choice" not in st.session_state:
    st.session_state.theme_choice = "White Theme"
if "show_theme_panel" not in st.session_state:
    st.session_state.show_theme_panel = False
if "uploaded_bg_bytes" not in st.session_state:
    st.session_state.uploaded_bg_bytes = None
if "uploaded_bg_type" not in st.session_state:
    st.session_state.uploaded_bg_type = "png"


def get_active_background_data_uri() -> str | None:
    if st.session_state.uploaded_bg_bytes is not None:
        return get_image_data_uri(st.session_state.uploaded_bg_bytes, st.session_state.uploaded_bg_type)

    return None

roh_daten = os.path.join("data", "ekg_data")
sortierte_daten = os.path.join("data", "data_sortiert")

frequenz_faktor = 100
alter_pfad = "data/ekg_data/"
neuer_pad = "data/data_sortiert/"

#data_resampling.resample_and_changeLink_ekg_data (roh_daten, sortierte_daten, neuer_pad, alter_pfad, json_datei_link)

if selected == "Startseite":
    if st.button("Themes auswählen"):
        st.session_state.show_theme_panel = not st.session_state.show_theme_panel

    st.title("Willkommen zur EKG Analyse App")
    st.subheader("Einführung")
    st.write("Die Website dient als zentrale Plattform zur Verwaltung von Personen und deren EKG‑Messdaten. Sie ermöglicht das Anlegen und Bearbeiten von Nutzern, das Hochladen und Auswerten von EKG‑Aufzeichnungen sowie die visuelle Darstellung der Signale. Zusätzlich bietet sie Funktionen zur Analyse von CSV‑Dateien, sodass verschiedene Datenquellen übersichtlich verarbeitet und interpretiert werden können.")
    st.write("Bitte wählen Sie eine Option aus dem Menü auf der linken Seite aus, oder nutzen Sie unten die Theme- und Hintergrundeinstellungen.")

    if st.session_state.show_theme_panel:
        st.markdown("### Theme und Hintergrund")
        st.session_state.theme_choice = st.selectbox("Theme auswählen:", THEME_OPTIONS, index=THEME_OPTIONS.index(st.session_state.theme_choice) if st.session_state.theme_choice in THEME_OPTIONS else 0)

        st.markdown("#### Eigenes Hintergrundbild hochladen")
        uploaded_bg = st.file_uploader("Hintergrundbild auswählen", type=["jpg", "jpeg", "png"])

        if uploaded_bg is not None:
            st.session_state.uploaded_bg_bytes = uploaded_bg.read()
            st.session_state.uploaded_bg_type = uploaded_bg.type.split("/")[-1]
            st.success("Eigenes Hintergrundbild wurde geladen.")
            st.image(Image.open(io.BytesIO(st.session_state.uploaded_bg_bytes)), caption="Hintergrundbild-Vorschau", use_column_width=True)

        if st.session_state.uploaded_bg_bytes is not None:
            if st.button("Hintergrundbild deaktivieren"):
                st.session_state.uploaded_bg_bytes = None
                st.success("Hintergrundbild wurde deaktiviert.")
        else:
            st.info("Kein benutzerdefiniertes Hintergrundbild aktiv.")

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

css = build_theme_css(st.session_state.theme_choice, get_active_background_data_uri())
st.markdown(css, unsafe_allow_html=True)


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
        

