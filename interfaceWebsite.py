import sys
import os

from pathlib import Path
import math
import importlib
import streamlit as st
import pandas as pd
from PIL import Image
from streamlit_option_menu import option_menu
import base64
import json
def _parse_birth_date_for_input(raw_value):
    """Parst gespeicherte Datumswerte robust fuer st.date_input."""
    if raw_value is None:
        return pd.Timestamp("2000-01-01")

    raw_text = str(raw_value).strip()
    if not raw_text:
        return pd.Timestamp("2000-01-01")

    known_formats = [
        "%Y-%m-%d",
        "%Y-%d-%m",
        "%d.%m.%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d/%m/%Y",
    ]

    for date_format in known_formats:
        parsed = pd.to_datetime(raw_text, format=date_format, errors="coerce")
        if pd.notna(parsed):
            return parsed

    parsed = pd.to_datetime(raw_text, dayfirst=True, errors="coerce")
    if pd.notna(parsed):
        return parsed

    return pd.Timestamp("2000-01-01")

def _apply_theme_css():
    theme = st.session_state.get("theme", "Weiß")
    bg_bytes = st.session_state.get("bg_image_bytes")
    bg_mime = st.session_state.get("bg_mime", "image/png")

    left_color = "transparent"
    right_color = "transparent"
    sidebar_text = "inherit"

    if theme == "Rot":
        left_color = "#7B1E2D"     
        right_color = "#FFEDEE"     
        sidebar_text = "#ffffff"
    elif theme == "Blau":
        left_color = "#1F4E79"      
        right_color = "#EAF3FF"     
        sidebar_text = "#ffffff"

    css = f"""
    <style>
    /* Sidebar background */
    [data-testid="stSidebar"] {{
        background-color: {left_color} !important;
    }}

    /* Main app area background (color) */
    [data-testid="stAppViewContainer"] {{
        background-color: {right_color} !important;
    }}

    /* Ensure good contrast for sidebar text when using dark backgrounds */
    [data-testid="stSidebar"] * {{
        color: {sidebar_text} !important;
    }}

    /* If a background image is set, use it for the app container */
    """

    if bg_bytes:
        try:
            b64 = base64.b64encode(bg_bytes).decode()
            css += f"\n[data-testid=\"stAppViewContainer\"] {{ background-image: url(\"data:{bg_mime};base64,{b64}\") !important; background-size: cover !important; background-position: center !important; }}\n"
            css += "\n[data-testid=\"stAppViewContainer\"]::before { content: \"\"; position: absolute; inset: 0; background: rgba(255,255,255,0.15); pointer-events: none; }\n"
        except Exception:
            pass

    css += "</style>"

    st.markdown(css, unsafe_allow_html=True)

st.session_state.setdefault("theme", "Weiß")
st.session_state.setdefault("bg_image_bytes", None)
st.session_state.setdefault("bg_mime", None)
st.session_state.setdefault("bg_uploader_counter", 0)
st.session_state.setdefault("bg_uploader_key", "bg_uploader_0")

_apply_theme_css()

aktueller_ordner = os.path.dirname(os.path.abspath(__file__))
gpx_ordner = os.path.join(aktueller_ordner, "GPX_Integration")

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

with st.sidebar:
    selected = option_menu(
        menu_title="Menü",
        options=["Startseite", "Personen Verwaltung", "EKG App", "CSV Analyse", "Trainings Leistungen"],
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

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
JSON_PFAD = DATA_DIR / "person_db.json"
ORDNER_EKG = DATA_DIR / "ekg_data"
ORDNER_SORTIERT = DATA_DIR / "data_sortiert"
BILDER_DIR = DATA_DIR / "pictures"
TEMP_DIR = DATA_DIR / "temp"

for pfad in [DATA_DIR, ORDNER_EKG, ORDNER_SORTIERT, BILDER_DIR, TEMP_DIR]:
    pfad.mkdir(parents=True, exist_ok=True)

UI_SETTINGS_PATH = DATA_DIR / "ui_settings.json"

def load_ui_settings() -> None:
    try:
        if UI_SETTINGS_PATH.exists():
            with open(UI_SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "theme" in data and data["theme"] is not None:
                st.session_state["theme"] = data["theme"]
            if data.get("bg_image_base64"):
                try:
                    st.session_state["bg_image_bytes"] = base64.b64decode(data["bg_image_base64"])
                    st.session_state["bg_mime"] = data.get("bg_mime", "image/png")
                except Exception:
                    st.session_state["bg_image_bytes"] = None
                    st.session_state["bg_mime"] = None
            else:
                st.session_state["bg_image_bytes"] = None
                st.session_state["bg_mime"] = None
    except Exception as e:
        print("Failed to load UI settings:", e)

def save_ui_settings() -> None:
    try:
        payload = {
            "theme": st.session_state.get("theme", "Weiß"),
            "bg_image_base64": None,
            "bg_mime": None,
        }
        bg = st.session_state.get("bg_image_bytes")
        if bg:
            payload["bg_image_base64"] = base64.b64encode(bg).decode()
            payload["bg_mime"] = st.session_state.get("bg_mime", "image/png")

        with open(UI_SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except Exception as e:
        print("Failed to save UI settings:", e)

def _on_theme_change():
    _apply_theme_css()
    save_ui_settings()


def _on_bg_upload(uploaded_obj=None):
    if uploaded_obj is None:
        uploaded_obj = st.session_state.get(st.session_state.get("bg_uploader_key", "bg_uploader_0"))
    try:
        if uploaded_obj:
            st.session_state["bg_image_bytes"] = uploaded_obj.getvalue()
            st.session_state["bg_mime"] = getattr(uploaded_obj, "type", None) or "image/png"
            save_ui_settings()
            _apply_theme_css()
    except Exception as e:
        print("Error handling background upload:", e)


def _remove_background():
    st.session_state["bg_image_bytes"] = None
    st.session_state["bg_mime"] = None

    # FileUploader-Wert wird indirekt geloescht, indem ein neuer Widget-Key verwendet wird.
    next_counter = int(st.session_state.get("bg_uploader_counter", 0)) + 1
    st.session_state["bg_uploader_counter"] = next_counter
    st.session_state["bg_uploader_key"] = f"bg_uploader_{next_counter}"

    save_ui_settings()
    _apply_theme_css()

modules_loaded = True
load_ui_settings()
_apply_theme_css()
try:
    from Personen import daten_einlesen, klasse_person, klasse_ekgdata
    from Personen_Verwaltung import benutzer_verwaltung
    from CSV_analyse import power_curve, zonen_einteilung
    from GPX_Integration.parsers.gpx_parser import gpx_einlesen
    from GPX_Integration.parsers.tcx_parser import tcx_einlesen
    from GPX_Integration.parsers.fit_parser import fit_einlesen
    from GPX_Integration.map.karten_erstellung import karte_erstellen_fuer_streamlit
    import GPX_Integration.logic.statistiken as statistiken_module
    import GPX_Integration.database.training_db as training_db_module
    import GPX_Integration.logic.hoehenprofil_interaktiv as hoehenprofil_interaktiv_module
    from GPX_Integration.logic.statistiken import (
        gesamt_distanz, gesamt_dauer, hoehenmeter, durchschnitt_puls, maximal_puls,
        durchschnittsgeschwindigkeit, pace
    )
    from GPX_Integration.database.training_db import (
        tabellen_erstellen, aktivitaet_speichern_mit_stats, streckenpunkte_speichern_batch,
        alle_aktivitaeten_holen
    )
    from GPX_Integration.logic.hoehenprofil_interaktiv import (
        compute_elevation_profile, get_segment_stats, get_point_details_at_index
    )
    
    try:
        importlib.reload(power_curve)
        importlib.reload(zonen_einteilung)
        importlib.reload(klasse_ekgdata)
        importlib.reload(statistiken_module)
        importlib.reload(training_db_module)
        importlib.reload(hoehenprofil_interaktiv_module)
    except Exception:
        
        pass
except Exception as e:
    modules_loaded = False
    import traceback
    tb = traceback.format_exc()
  
    try:
        st.error("Fehler beim Laden von lokalen Modulen. Siehe Logs für Details.")
        st.text(tb)
        st.stop()
    except Exception:
        
        print("Fehler beim Laden von lokalen Modulen:")
        print(tb)
        raise

personen_data = daten_einlesen.personen_einlesen(str(JSON_PFAD))

abtastrate = 100

if selected == "Startseite":
    st.title("Willkommen zur EKG Analyse App")
    st.subheader("Einführung")
    st.markdown("""
Die Website dient als zentrale Plattform zur Verwaltung von Personen und deren EKG‑Messdaten. 
Des weiteren können Trainingsergebnisse aus GPX, TCX und FIT Dateien analysiert und gespeichert werden.

**Funktionen:**
- Personen anlegen und bearbeiten  
- EKG‑Daten hochladen und analysieren  
- Herzratenvariabilität berechnen  
- CSV‑Dateien auswerten
- Trainingseinheiten 
""")
    st.divider()
    
    with st.container():
        st.subheader("Farbmodus & Hintergrund")

        _theme_options = ["Weiß", "Rot", "Blau"]
        _current_theme = st.session_state.get("theme", "Weiß")
        try:
            _idx = _theme_options.index(_current_theme)
        except ValueError:
            _idx = 0

        st.selectbox(
            "Farbmodus auswählen",
            _theme_options,
            index=_idx,
            key="theme",
            on_change=_on_theme_change,
        )

        uploaded_bg = st.file_uploader(
            "Hintergrundbild hochladen",
            type=["png", "jpg", "jpeg"],
            key=st.session_state.get("bg_uploader_key", "bg_uploader_0"),
            on_change=_on_bg_upload,
        )

        # Direkte Verarbeitung sorgt dafuer, dass das Bild auch ohne Callback-Probleme gesetzt wird.
        if uploaded_bg is not None:
            _on_bg_upload(uploaded_bg)

        if st.button("Hintergrund entfernen"):
            _remove_background()
            st.success("Hintergrund entfernt")

        _apply_theme_css()

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
            bildpfad = str(BILDER_DIR / bildname)
            with open(bildpfad, "wb") as f:
                f.write(bild_person.getbuffer())
            st.success(f"Bild {bild_person.name} gespeichert")

        ekg_datei = st.file_uploader("EKG-Datei hochladen", type=["txt"])
        ekg_tests = []
        if ekg_datei:
            ekg_id = benutzer_verwaltung.neue_ekg_id(personen_data)
            ekg_datum = st.text_input("Datum der EKG-Messung")
            ekg_name = f"{person_id}_{ekg_id}_{ekg_datei.name}"
            ekgpfad = str(ORDNER_EKG / ekg_name)
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
            benutzer_verwaltung.benutzer_speichern(str(JSON_PFAD), person_info)
            st.success("Neue Person hinzugefügt")

    if option == "Bestehende Nutzer aktualisieren":
        auswahl = {f"{p['id']} - {p['firstname']} {p['lastname']}": p['id'] for p in personen_data}
        ausgewaelt = st.selectbox("Person auswählen", list(auswahl.keys()))
        ausgewaelt_id = auswahl[ausgewaelt]

        person_info = next((p for p in personen_data if p["id"] == ausgewaelt_id), None)

        if person_info:
            vorname = st.text_input("Vorname", value=person_info["firstname"])
            nachname = st.text_input("Nachname", value=person_info["lastname"])
            geburtsdatum = st.date_input(
                "Geburtsdatum",
                value=_parse_birth_date_for_input(person_info.get("date_of_birth")),
            )

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
                benutzer_verwaltung.benutzer_speichern(str(JSON_PFAD), person_info, aktualisieren=True)
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
                        benutzer_verwaltung.person_loeschen(str(JSON_PFAD), ausgewaelt_id)
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
            except Exception:
                st.warning("Kein gültiges Bild gefunden")

    

    with tab_ekg:
        st.subheader("EKG Analyse")
        st.write("Hier können Sie die EKG-Messungen der ausgewählten Person analysieren.")

        ekg_ids = [t["id"] for t in person["ekg_tests"]]
        if not ekg_ids:
            st.info(
                "EKG App lässt sich für diese Person nicht ausführen, weil keine EKG-Daten vorhanden sind. "
                "Bitte zuerst eine EKG-Messung unter 'Personen Verwaltung' oder über den Upload anlegen."
            )
            st.stop()

        ekg_id = st.selectbox("EKG-Messung auswählen", ekg_ids)

        ekg_dict = klasse_ekgdata.EKGData.lade_ekg_nach_id(ekg_id, personen_data)
        if ekg_dict is None:
            st.info(
                "EKG App lässt sich für diese Person nicht ausführen, weil die ausgewählte EKG-Messung nicht gefunden wurde."
            )
            st.stop()

        ekg = klasse_ekgdata.EKGData(ekg_dict)

        if ekg.df.empty:
            st.info(
                "EKG App lässt sich für diese Person nicht ausführen, weil die EKG-Datei leer ist oder nicht geladen werden konnte."
            )
            st.stop()
        ekg.zeitbereich(None, None, abtastrate)

        tab_signal, tab_hr, tab_hrv = st.tabs(["Signal", "Herzrate", "HRV"])

        with tab_signal:
            st.subheader("Zeitbereich auswählen")
            gesamtdauer = ekg.zeitreihe_dauer()
            max_zeitfenster = math.ceil(gesamtdauer)
            start, ende = st.slider("Signal-Zeitraum [s]", 0.0, float(max_zeitfenster), (0.0, min(10.0, float(max_zeitfenster))), step=0.1)

            ekg.zeitbereich(start, ende, abtastrate)

            st.plotly_chart(ekg.anzeigen_signale())
            st.markdown("<small style='color: gray;'>Hinweis: Durch Anklicken der Legende können Signal und Peaks ein- oder ausgeblendet werden.</small>", unsafe_allow_html=True)
            st.metric("Länge der Zeitreihe [min]", round(gesamtdauer / 60, 2))
            st.metric("Testdatum", ekg.test_datum())
            st.metric("Dateipfad", ekg.pfad)
       
        with tab_hr:
            st.subheader("Herzrate [BPM]")
            st.write("Wählen Sie den Zeitbereich für die Herzratenberechnung.")
            hr_range_start, hr_range_end = st.slider(
                "Herzrate-Bereich [s]",
                0.0,
                float(max_zeitfenster),
                (0.0, min(10.0, float(max_zeitfenster))),
                step=0.1,
            )

            herzrate_gesamt = ekg.herzrate()
            herzrate_bereich = ekg.herzrate_bereich(hr_range_start, hr_range_end)

            st.metric("Herzrate gesamt [BPM]", round(herzrate_gesamt, 2) if herzrate_gesamt > 0 else "n/a")
            st.metric("Herzrate im Bereich [BPM]", round(herzrate_bereich, 2) if herzrate_bereich > 0 else "n/a")

            if herzrate_gesamt == 0:
                st.warning("Herzrate gesamt konnte nicht berechnet werden – zu wenige Peaks im Signal.")
            if herzrate_bereich == 0:
                st.warning("Herzrate im Bereich konnte nicht berechnet werden – zu wenige Peaks im gewählten Bereich.")

            st.plotly_chart(ekg.plot_herzrate(start=hr_range_start, ende=hr_range_end))
    
        with tab_hrv:
            st.subheader("Herzvariabilität [HRV]")

            simulate = st.checkbox("Simuliere kritische HRV-Werte")
            if simulate:
                st.info("Kritische HRV-Simulation aktiv: Werte und Plot werden temporär aggressiv angezeigt.")

            col_left, col_right = st.columns(2)

            with col_left:
                st.write("**HRV gesamter Bereich:**")

                hrv_gesamt = ekg.herzratenvariabilität()

                if simulate:
                    hrv_gesamt = {"HRV_MeanNN": 150.0, "HRV_MinNN": 100.0, "HRV_MaxNN": 2000.0}
                    st.warning("Kritische HRV-Werte simuliert (gesamter Bereich)")

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

                hrv_bereich = ekg.herzratenvariabilität_bereich(hr_range_start, hr_range_end)

                if simulate:
                    hrv_bereich = {"HRV_MeanNN": 150.0, "HRV_MinNN": 100.0, "HRV_MaxNN": 2000.0}
                    st.warning("Kritische HRV-Werte simuliert (ausgewählter Bereich)")

                if hrv_bereich is None:
                    st.warning("HRV im Bereich konnte nicht berechnet werden – Signal leer oder Abtastrate nicht gesetzt.")
                elif hrv_bereich.get("HRV_MeanNN") is None:
                    st.warning("HRV im Bereich konnte nicht berechnet werden – zu wenige Peaks im Zeitfenster.")
                else:
                    st.metric("HRV MeanNN [s]", round(hrv_bereich["HRV_MeanNN"] / 1000, 3))
                    st.metric("HRV MinNN [s]", round(hrv_bereich["HRV_MinNN"] / 1000, 3))
                    st.metric("HRV MaxNN [s]", round(hrv_bereich["HRV_MaxNN"] / 1000, 3))

            st.plotly_chart(ekg.plot_hrv(start=hr_range_start, ende=hr_range_end, simulate=simulate))

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
        st.info("Aktuelle CSV-Daten werden für die Analyse verwendet.")

        test_anomalien = st.checkbox("Testdaten mit künstlichen Anomalien erzeugen")
        if test_anomalien:
            df = zonen_einteilung.inject_test_anomalies(df)
            st.success("Testanomalien wurden erfolgreich eingebracht. Die Auswirkungen sind im Diagramm sichtbar.")

        anomalien = zonen_einteilung.erkenne_anomalien(df)
        fig = zonen_einteilung.ekg_plot(df, max_hf, anomalien)
        st.plotly_chart(fig)
        st.caption("Hinweis: Durch Anklicken der Legende können Herzfrequenz oder Leistung ein- bzw. ausgeblendet werden.")

        st.metric("CSV-Dauer [min]", round(zonen_einteilung.gesamtdauer_min(df), 2))

        if len(anomalien) == 0:
            st.success("Keine Anomalie gefunden. Partien ist gesund.")
        else:
            with st.expander(f"{len(anomalien)} gefundene Anomalie(n) anzeigen"):
                df_anom = pd.DataFrame(anomalien)
                df_anom["x"] = df_anom["x"].apply(lambda v: f"{v:.2f}")
                df_anom["y"] = df_anom["y"].apply(lambda v: f"{v:.2f}")
                df_anom["Achse"] = df_anom["secondary_y"].apply(lambda v: "Leistung (rechte Achse)" if v else "Herzfrequenz (linke Achse)")
                df_anom = df_anom.drop(columns=["secondary_y"])
                df_anom = df_anom.rename(columns={
                    "typ": "Anomalie-Typ",
                    "x": "Zeitpunkt [min]",
                    "y": "Messwert",
                    "beschreibung": "Beschreibung"})
                df_anom = df_anom[["Anomalie-Typ", "Zeitpunkt [min]", "Messwert", "Achse", "Beschreibung"]]
                st.table(df_anom)

        fenster_leistung, fenster_zoneninfo = st.tabs(["Leistungswerte", "Zoneninformationen"])

        with fenster_leistung:
            st.metric ("Ø Leistung [W]", round(zonen_einteilung.mittelwert_leistung(df), 2))
            st.metric ("Max Leistung [W]", zonen_einteilung.maximale_leistung(df))
        with fenster_zoneninfo:
            daten = zonen_einteilung.leistung_zeit_in_zonen(df, max_hf)
            df_zonen = pd.DataFrame(daten).set_index("Trainingsbereich")
            st.dataframe(df_zonen)
            st.caption("Hinweis: Die Tabelle kann durch Anklicken der Spaltenüberschriften sortiert werden.")

    with fenster_power:
        df_power = power_curve.aktivitaet_einlesen()
        freq = st.number_input("Frequenz:", min_value=1, max_value=20, value=1)

        x_min = st.number_input("X-Min (Minuten):", min_value=0, max_value=180, value=0)
        x_max_raw = st.number_input("X-Max (Minuten):", min_value=0, max_value=180, value=5)
        x_max = x_max_raw + 1

        st.plotly_chart(power_curve.plot_powercurve(df_power, x_min, x_max, freq))
        st.plotly_chart(power_curve.zoom_powercurve(df_power, x_min, x_max, freq))


if selected == "Trainings Leistungen":
    st.title("Trainings Leistungen")
    
    tabellen_erstellen()
    
    # Tabs für Upload und Verwaltung
    tab_upload, tab_history = st.tabs(["Neue Aktivität", "Aktivitätsverlauf"])

    @st.dialog("Trainingsdetails")
    def _zeige_aktivitaet_details_dialog(aktivitaet):
        st.subheader(aktivitaet.get("name", "Aktivität"))

        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1:
            st.metric("Sportart", aktivitaet.get("sportart") or "N/A")
        with info_col2:
            st.metric("Datum", aktivitaet.get("datum") or "N/A")
        with info_col3:
            st.metric("Aktivität-ID", str(aktivitaet.get("id", "N/A")))

        punkte = training_db_module.streckenpunkte_holen(aktivitaet.get("id"))
        if not punkte:
            st.info("Für diese Aktivität sind keine Streckenpunkte gespeichert.")
            return

        st.subheader("Trainingsroute")
        try:
            karte = karte_erstellen_fuer_streamlit(punkte)
            st.components.v1.html(karte.get_root().render(), height=450)
        except Exception as e:
            st.warning(f"Karte konnte nicht erstellt werden: {e}")

        st.subheader("Trainingsstatistiken")
        col1, col2, col3, col4 = st.columns(4)

        dauer_sek = aktivitaet.get("dauer_sek")
        distanz_km = aktivitaet.get("distanz_km")
        hm_pos = aktivitaet.get("hoehenmeter_positiv")
        hm_neg = aktivitaet.get("hoehenmeter_negativ")
        geschw = aktivitaet.get("geschwindigkeit_kmh")
        puls_avg = aktivitaet.get("puls_durchschnitt")
        puls_max = aktivitaet.get("puls_max")

        with col1:
            st.metric("Distanz", f"{distanz_km:.2f} km" if distanz_km else "N/A")
        with col2:
            st.metric(
                "Dauer",
                f"{int(dauer_sek // 3600):02d}:{int((dauer_sek % 3600) // 60):02d}:{int(dauer_sek % 60):02d}"
                if dauer_sek else "N/A"
            )
        with col3:
            st.metric("Höhenmeter (↑)", f"{hm_pos:.0f} m" if hm_pos else "N/A")
        with col4:
            st.metric("Höhenmeter (↓)", f"{hm_neg:.0f} m" if hm_neg else "N/A")

        col5, col6, col7 = st.columns(3)
        with col5:
            st.metric("Ø-Geschwindigkeit", f"{geschw:.2f} km/h" if geschw else "N/A")
        with col6:
            st.metric("Ø-Puls", f"{puls_avg:.0f} BPM" if puls_avg else "N/A")
        with col7:
            st.metric("Max-Puls", f"{puls_max} BPM" if puls_max else "N/A")

        st.subheader("Höhenprofil")
        try:
            profile = compute_elevation_profile(punkte)
            stats = get_segment_stats(punkte)

            if profile and len(profile) > 0:
                slider_key = f"history_profile_idx_{aktivitaet.get('id')}"
                selected_index = st.slider(
                    "Punkt im Profil auswählen:",
                    0,
                    len(profile) - 1,
                    0,
                    key=slider_key,
                )

                point_details = get_point_details_at_index(profile, selected_index)
                if point_details:
                    pcol1, pcol2, pcol3 = st.columns(3)
                    with pcol1:
                        st.metric("Kilometer", f"{point_details['km']:.2f}")
                    with pcol2:
                        st.metric("Höhe", f"{point_details['hoehe']:.0f} m")
                    with pcol3:
                        if point_details['anstieg_prozent'] > 0:
                            st.metric("Anstieg", f"{point_details['anstieg_prozent']:.1f}%")
                        else:
                            st.metric("Gefälle", f"{point_details['gefaelle_prozent']:.1f}%")

                import plotly.graph_objects as go
                fig_profile = go.Figure()
                kms = [p['km'] for p in profile]
                hoehen = [p['hoehe'] for p in profile]

                fig_profile.add_trace(go.Scatter(
                    x=kms,
                    y=hoehen,
                    mode='lines',
                    fill='tozeroy',
                    line=dict(color='#1f77b4', width=3),
                    name='Höhe'
                ))

                if 0 <= selected_index < len(profile):
                    fig_profile.add_trace(go.Scatter(
                        x=[profile[selected_index]['km']],
                        y=[profile[selected_index]['hoehe']],
                        mode='markers',
                        marker=dict(size=12, color='red'),
                        name='Aktueller Punkt'
                    ))

                fig_profile.update_layout(
                    title="Höhenverlauf",
                    xaxis_title="Distanz (km)",
                    yaxis_title="Höhe (m)",
                    hovermode='x unified',
                    height=380
                )

                st.plotly_chart(fig_profile, use_container_width=True)
                st.caption(
                    f"Min: {stats['min_hoehe']:.0f}m | Max: {stats['max_hoehe']:.0f}m | "
                    f"Total ↑: {stats['total_stieg']:.0f}m | Total ↓: {stats['total_fall']:.0f}m"
                )
            else:
                st.warning("Keine Höhendaten vorhanden")
        except Exception as e:
            st.warning(f"Höhenprofil konnte nicht erstellt werden: {e}")
    
    with tab_upload:
        st.subheader("GPX/TCX/FIT-Datei hochladen")
        uploaded_file = st.file_uploader(
            "Wähle eine Datei (GPX, TCX oder FIT)", 
            type=["gpx", "tcx", "fit"]
        )
        
        if uploaded_file:
            temp_path = str(TEMP_DIR / uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ Datei '{uploaded_file.name}' hochgeladen")
            
            # Datei einlesen
            try:
                if uploaded_file.name.endswith(".gpx"):
                    punkte = gpx_einlesen(temp_path)
                elif uploaded_file.name.endswith(".tcx"):
                    punkte = tcx_einlesen(temp_path)
                else:
                    punkte = fit_einlesen(temp_path)
                
                if not punkte or len(punkte) == 0:
                    st.error("❌ Fehler: Keine gültigen Streckenpunkte in der Datei gefunden")
                    st.stop()
                
                st.info(f"📍 {len(punkte)} Streckenpunkte geladen")
                
                # Sportart-Auswahl
                st.subheader("Trainingsart")
                sportarten = ["🏃 Laufen", "🚴 Radfahren", "🥾 Wandern", "🏊 Schwimmen"]
                sportart_selected = st.radio("Wähle deine Trainingsart:", sportarten)
                sportart_key = sportart_selected.split()[-1]  # "Laufen", "Radfahren", etc.
                
                # Aktivitätsname
                default_name = f"{sportart_key} - {pd.Timestamp.now().strftime('%d.%m.%Y %H:%M')}"
                aktivitaet_name = st.text_input("Name der Aktivität:", value=default_name)
                
                # Statistiken berechnen
                try:
                    distanz_km = gesamt_distanz(punkte)
                    dauer_sek = gesamt_dauer(punkte)
                    hm_pos, hm_neg = hoehenmeter(punkte)
                    puls_avg = durchschnitt_puls(punkte)
                    puls_max = maximal_puls(punkte)
                    geschw = durchschnittsgeschwindigkeit(distanz_km, dauer_sek)
                    pace_min_km = pace(distanz_km, dauer_sek)
                    
                    st.subheader("Trainingsroute")
                    try:
                        karte = karte_erstellen_fuer_streamlit(punkte)
                        st.components.v1.html(karte.get_root().render(), height=500)
                    except Exception as e:
                        st.warning(f"⚠️ Karte konnte nicht erstellt werden: {e}")
                    
                    st.subheader("Trainingsstatistiken")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Distanz", f"{distanz_km:.2f} km" if distanz_km else "N/A")
                    with col2:
                        st.metric("Dauer", 
                                  f"{int(dauer_sek // 3600):02d}:{int((dauer_sek % 3600) // 60):02d}:{int(dauer_sek % 60):02d}" 
                                  if dauer_sek else "N/A")
                    with col3:
                        st.metric("Höhenmeter (↑)", f"{hm_pos:.0f} m" if hm_pos else "N/A")
                    with col4:
                        st.metric("Höhenmeter (↓)", f"{hm_neg:.0f} m" if hm_neg else "N/A")
                    
                    col5, col6, col7 = st.columns(3)
                    
                    with col5:
                        st.metric("Ø-Geschwindigkeit", f"{geschw:.2f} km/h" if geschw else "N/A")
                    with col6:
                        st.metric("Ø-Puls", f"{puls_avg:.0f} BPM" if puls_avg else "N/A")
                    with col7:
                        st.metric("Max-Puls", f"{puls_max} BPM" if puls_max else "N/A")
                    
                    st.subheader("Höhenprofil (Interaktiv)")
                    
                    try:
                        profile = compute_elevation_profile(punkte)
                        stats = get_segment_stats(punkte)
                        
                        if profile and len(profile) > 0:
                            # Schieberegler für Punkt-Details
                            selected_index = st.slider(
                                "Klicke auf einen Punkt im Profil:",
                                0, 
                                len(profile) - 1,
                                0
                            )
                            
                            point_details = get_point_details_at_index(profile, selected_index)
                            
                            if point_details:
                                info_col1, info_col2, info_col3 = st.columns(3)
                                with info_col1:
                                    st.metric("Kilometer", f"{point_details['km']:.2f}")
                                with info_col2:
                                    st.metric("Höhe", f"{point_details['hoehe']:.0f} m")
                                with info_col3:
                                    if point_details['anstieg_prozent'] > 0:
                                        st.metric("Anstieg", f"{point_details['anstieg_prozent']:.1f}%")
                                    else:
                                        st.metric("Gefälle", f"{point_details['gefaelle_prozent']:.1f}%")
                            
                            import plotly.graph_objects as go
                            fig_profile = go.Figure()
                            
                            kms = [p['km'] for p in profile]
                            hoehen = [p['hoehe'] for p in profile]
                            
                            fig_profile.add_trace(go.Scatter(
                                x=kms, 
                                y=hoehen,
                                mode='lines',
                                fill='tozeroy',
                                line=dict(color='#1f77b4', width=3),
                                name='Höhe'
                            ))
                            
                            if 0 <= selected_index < len(profile):
                                fig_profile.add_trace(go.Scatter(
                                    x=[profile[selected_index]['km']],
                                    y=[profile[selected_index]['hoehe']],
                                    mode='markers',
                                    marker=dict(size=12, color='red'),
                                    name='Aktueller Punkt'
                                ))
                            
                            fig_profile.update_layout(
                                title="Höhenverlauf",
                                xaxis_title="Distanz (km)",
                                yaxis_title="Höhe (m)",
                                hovermode='x unified',
                                height=400
                            )
                            
                            st.plotly_chart(fig_profile, use_container_width=True)
                            
                            st.caption(f"Min: {stats['min_hoehe']:.0f}m | Max: {stats['max_hoehe']:.0f}m | "
                                     f"Total ↑: {stats['total_stieg']:.0f}m | Total ↓: {stats['total_fall']:.0f}m")
                        else:
                            st.warning("Keine Höhendaten vorhanden")
                    
                    except Exception as e:
                        st.warning(f"Höhenprofil konnte nicht erstellt werden: {e}")
                    
                    if st.button("Aktivität speichern", type="primary"):
                        try:
                            aktivitaet_id = aktivitaet_speichern_mit_stats(
                                name=aktivitaet_name,
                                datum=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                                sportart=sportart_key,
                                dauer_sek=dauer_sek,
                                distanz_km=distanz_km,
                                hoehenmeter_positiv=hm_pos,
                                hoehenmeter_negativ=hm_neg,
                                puls_durchschnitt=puls_avg,
                                puls_max=puls_max,
                                geschwindigkeit_kmh=geschw,
                                pace_min_km=pace_min_km
                            )
                            
                            streckenpunkte_speichern_batch(aktivitaet_id, punkte)
                            
                            st.success(f"Aktivität '{aktivitaet_name}' wurde erfolgreich gespeichert!")
                            st.balloons()
                        
                        except Exception as e:
                            st.error(f"Fehler beim Speichern: {e}")
                
                except Exception as e:
                    st.error(f"Fehler bei der Statistik-Berechnung: {e}")
            
            except Exception as e:
                st.error(f"Fehler beim Einlesen der Datei: {e}")
    
    with tab_history:
        st.subheader("Deine Aktivitäten")
        
        try:
            aktivitaeten = alle_aktivitaeten_holen()
            
            if not aktivitaeten or len(aktivitaeten) == 0:
                st.info("📌 Noch keine Aktivitäten gespeichert. Lade eine Datei hoch!")
            else:
                sportarten_liste = list(set([a['sportart'] for a in aktivitaeten]))
                selected_sportart = st.multiselect("Nach Sportart filtern:", sportarten_liste, default=sportarten_liste)
                
                filtered = [a for a in aktivitaeten if a['sportart'] in selected_sportart]
                
                display_data = []
                for a in filtered:
                    display_data.append({
                        "Datum": a['datum'],
                        "Name": a['name'],
                        "Sportart": a['sportart'],
                        "Distanz (km)": f"{a['distanz_km']:.2f}" if a['distanz_km'] else "N/A",
                        "Dauer": f"{int(a['dauer_sek'] // 3600):02d}:{int((a['dauer_sek'] % 3600) // 60):02d}:{int(a['dauer_sek'] % 60):02d}" if a['dauer_sek'] else "N/A",
                        "Ø Speed (km/h)": f"{a['geschwindigkeit_kmh']:.2f}" if a['geschwindigkeit_kmh'] else "N/A",
                        "Höhenmeter (↑)": f"{a['hoehenmeter_positiv']:.0f}" if a['hoehenmeter_positiv'] else "N/A"
                    })

                df_display = pd.DataFrame(display_data)
                st.caption("Klicke auf eine Zeile, um die Aktivität im Detailfenster zu öffnen.")
                selected_rows = []
                try:
                    table_event = st.dataframe(
                        df_display,
                        use_container_width=True,
                        on_select="rerun",
                        selection_mode="single-row",
                    )
                    selected_rows = list(table_event.selection.rows)
                except TypeError:
                    # Fallback für Streamlit-Versionen ohne Zeilen-Selektion in st.dataframe
                    st.dataframe(df_display, use_container_width=True)

                if selected_rows:
                    selected_idx = selected_rows[0]
                    if 0 <= selected_idx < len(filtered):
                        _zeige_aktivitaet_details_dialog(filtered[selected_idx])

                st.caption(f"Insgesamt {len(filtered)} Aktivitäten angezeigt")

                aktivitaet_lookup = {
                    f"{a['datum']} | {a['name']} | {a['sportart']} | ID {a['id']}": a
                    for a in filtered
                }

                if "show_delete_activity_panel" not in st.session_state:
                    st.session_state["show_delete_activity_panel"] = False

                st.divider()
                if st.button("Aktivität löschen"):
                    st.session_state["show_delete_activity_panel"] = True

                if st.session_state["show_delete_activity_panel"]:
                    if aktivitaet_lookup:
                        st.subheader("Aktivität löschen")
                        zu_loeschen_label = st.selectbox(
                            "Zu löschende Aktivität auswählen:",
                            list(aktivitaet_lookup.keys())
                        )
                        zu_loeschen = aktivitaet_lookup[zu_loeschen_label]

                        st.warning(
                            f"Bitte bestätige das Löschen von **{zu_loeschen['name']}** vom **{zu_loeschen['datum']}**. "
                            "Diese Aktion kann nicht rückgängig gemacht werden."
                        )
                        bestaetigung = st.checkbox("Ja, ich möchte diese Aktivität endgültig löschen.")
                        loeschen_clicked = st.button("Aktivität endgültig löschen", type="primary")

                        if loeschen_clicked:
                            if not bestaetigung:
                                st.warning("Bitte bestätige das Löschen zuerst mit dem Kontrollkästchen.")
                            else:
                                try:
                                    geloescht = training_db_module.aktivitaet_loeschen(zu_loeschen["id"])
                                    if geloescht:
                                        st.success(f"Aktivität '{zu_loeschen['name']}' wurde gelöscht.")
                                        st.session_state["show_delete_activity_panel"] = False
                                        st.rerun()
                                    else:
                                        st.info("Die Aktivität konnte nicht gefunden oder nicht gelöscht werden.")
                                except Exception as e:
                                    st.error(f"Fehler beim Löschen der Aktivität: {e}")
                    else:
                        st.info("Für die aktuell gefilterte Ansicht gibt es keine Aktivitäten zum Löschen.")
        
        except Exception as e:
            st.error(f"Fehler beim Laden der Aktivitäten: {e}")







