# 🏃 Dashboard Integration II - Trainings- & EKG-Analyseplattform

Eine umfassende **Streamlit-basierte Webanwendung** zur Verwaltung von Personen, Analyse von EKG-Daten, Trainingsaktivitäten und sportlicher Leistungsbewertung.

---

## 📋 Inhaltsverzeichnis

- [Features](#-features)
- [Systemarchitektur](#-systemarchitektur)
- [Installation](#-installation)
- [Verwendung](#-verwendung)
- [Projektstruktur](#-projektstruktur)
- [Technologie-Stack](#-technologie-stack)
- [Datenspeicherung](#-datenspeicherung)
- [Module im Detail](#-module-im-detail)

---

## ✨ Features

### 🏠 Startseite
- Übersicht und Einführung in die Anwendung
- Schneller Zugriff auf alle Funktionen

### 👥 Personen Verwaltung
- **Neue Personen anlegen** mit Foto-Upload
- **Bestehende Nutzer bearbeiten** (Persönliche Daten, Fotos)
- **Nutzer löschen** mit Bestätigung
- JSON-basierte Persistierung (person_db.json)

### 💓 EKG Analyse
- EKG-Daten pro Person hochladen und speichern
- **R-Peak-Erkennung** zur automatischen Herzrate-Berechnung
- **Herzratenvariabilität (HRV)** analysieren
- Signalvisualisierung (EKG-Signal, Herzrate-Trend, HRV)
- Vergleich zwischen Ruhe- und Belastungszuständen

### 📊 CSV Analyse
- Power-Curve-Berechnung für Leistungsdaten
- Zoneneinteilung nach Herzfrequenztrainingszone
- Interaktive Plotly-Visualisierungen
- Datenimport aus CSV-Aktivitätsdateien

### 🗺️ Training Leistungen (Hauptfeature)
#### 📤 Neue Aktivität hochladen:
- **Multi-Format-Unterstützung:** GPX, TCX, FIT (Garmin)
- **Sportart-Auswahl:** Laufen, Radfahren, Wandern, Schwimmen
- Automatische Statistik-Berechnung:
  - Distanz, Dauer, Höhenmeter
  - Durchschnitt/Max Pulsfrequenz
  - Geschwindigkeit, Pace
- **Interaktive Kartenvisualisierung** (Folium)
- **Höhenprofil mit Schieberegler** zur Detailansicht

#### 📊 Aktivitätsverlauf:
- Alle Trainingseinheiten chronologisch anzeigen
- 7-Metrik-Statistiken pro Aktivität
- Filterung nach Sportart
- Datumsbereiche auswählen

---

## 🏗️ Systemarchitektur

```
DashboardIntergrationII/
│
├── interfaceWebsite.py              # 🎯 Hauptanwendung (Streamlit UI)
├── requirements.txt                 # 📦 Abhängigkeiten
├── pyproject.toml                   # ⚙️ Projektconfig
│
├── Personen/                        # 👥 Personalmanagement
│   ├── klasse_person.py            # Person-Dataclass
│   ├── klasse_ekgdata.py           # EKG-Analyselogik
│   └── daten_einlesen.py           # JSON-I/O
│
├── Personen_Verwaltung/            # 🎛️ Admin-Funktionen
│   └── benutzer_verwaltung.py
│
├── CSV_analyse/                    # 📊 Sportdaten-Auswertung
│   ├── power_curve.py              # Leistungskurvenberechnung
│   └── zonen_einteilung.py         # Herzfrequenzzone-Analyse
│
├── GPX_Integration/                # 🗺️ Trainings-GPS-Daten
│   ├── database/
│   │   └── training_db.py          # SQLite Persistierung
│   ├── parsers/
│   │   ├── gpx_parser.py           # GPX-Format
│   │   ├── tcx_parser.py           # TCX-Format (Garmin)
│   │   └── fit_parser.py           # FIT-Format (Garmin)
│   ├── logic/
│   │   ├── statistiken.py          # Berechnungen (Distanz, Tempo, etc.)
│   │   ├── hoehenprofil_interaktiv.py  # Elevation-Profile
│   │   ├── zonen.py                # Trainingszone-Verteilung
│   │   └── plots.py                # Visualisierungen
│   └── map/
│       └── karten_erstellung.py    # Folium-Kartenrenderer
│
└── data/                           # 📁 Datenspeicher
    ├── person_db.json              # Personenverwaltung
    ├── activity.csv                # Aktivitätsdaten
    ├── training.db                 # SQLite-Datenbank ⭐
    ├── ekg_data/                   # EKG-Messdateien
    ├── data_sortiert/              # Verarbeitete EKG-Daten
    └── pictures/                   # Benutzerfotos
```

---

## 🚀 Installation

### Voraussetzungen
- **Python 3.12+**
- **Git**
- **Windows/Linux/macOS**

### Schritt 1: Repository klonen
```bash
git clone <repository-url>
cd DashboardIntergrationII
```

### Schritt 2: Virtuelle Umgebung erstellen
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### Schritt 3: Abhängigkeiten installieren
```bash
pip install -r DashboardIntergrationII/requirements.txt
```

### Schritt 4: Anwendung starten
```bash
cd DashboardIntergrationII
streamlit run interfaceWebsite.py
```

Die App öffnet sich unter `http://localhost:8501`

---

## 💻 Verwendung

### Personen verwaltenn
1. Navigiere zu **"Personen Verwaltung"** im Menü
2. Wähle **"Neue Person anlegen"**
3. Gib Namen, Geburtsdatum und Foto ein
4. Speichern → Daten in `person_db.json` gespeichert

### EKG analysieren
1. Gehe zu **"EKG App"**
2. Wähle eine Person aus
3. Lade eine EKG-Datei hoch
4. Analysiere: Herzrate, HRV, Signalpeaks werden automatisch berechnet

### Training hochladen
1. Gehe zu **"Training Leistungen"** → **"📤 Neue Aktivität"**
2. Lade eine **GPX/TCX/FIT-Datei** hoch
3. Wähle **Sportart** und **Startzeit**
4. System berechnet automatisch:
   - Strecke auf interaktiver Karte
   - Höhenprofil mit Details
   - 7 Statistiken (Distanz, Dauer, Höhenmeter, Puls, Geschwindigkeit, Pace)
5. Speichern → Daten in SQLite-DB gespeichert

### Aktivitätsverlauf ansehen
1. **"Training Leistungen"** → **"📊 Aktivitätsverlauf"**
2. Filtere nach **Sportart** oder **Zeitraum**
3. Klicke auf Aktivität für Details (Karte + Statistiken)

---

## 📦 Technologie-Stack

### Core Framework
| Technologie | Version | Zweck |
|---|---|---|
| **Streamlit** | 1.58.0 | Web-UI Framework |
| **streamlit-option-menu** | 0.4.0 | Navigationsmenü |

### Datenverarbeitung & Visualisierung
| Technologie | Version | Zweck |
|---|---|---|
| **pandas** | 2.3.3 | Datenmanipulation |
| **numpy** | ≥1.24.0 | Numerische Berechnungen |
| **plotly** | 6.8.0 | Interaktive Diagramme |
| **folium** | 0.20.0 | Karten-Rendering |
| **pillow** | ≥10.0.0 | Bildverarbeitung |

### Signal- & Wissenschaft
| Technologie | Version | Zweck |
|---|---|---|
| **scipy** | 1.18.0 | Signalverarbeitung (Peak-Detection) |
| **neurokit2** | 0.2.13 | Biomedizinische Signal-Analyse |

### Dateiformate & Datenbank
| Technologie | Version | Zweck |
|---|---|---|
| **fitparse** | 1.2.0 | Garmin FIT-Format-Parser |
| **sqlite3** | Built-in | Aktivitäts-Persistierung |
| **json** | Built-in | Personen-Speicherung |

---

## 📊 Datenspeicherung

### SQLite Datenbank (`training.db`) ⭐
Zentrale **Speicherung aller Trainingsaktivitäten** mit zwei Tabellen:

#### 1️⃣ Tabelle: `aktivitaeten`
Speichert Metadaten jeder Trainingseinheit:
```sql
CREATE TABLE aktivitaeten (
    id INTEGER PRIMARY KEY,
    name TEXT,
    datum TEXT,
    sportart TEXT,              -- Laufen/Radfahren/Wandern/Schwimmen
    dauer_sek REAL,            -- Sekunden
    distanz_km REAL,           -- Kilometer
    hoehenmeter_positiv REAL,  -- Aufstieg (m)
    hoehenmeter_negativ REAL,  -- Abstieg (m)
    puls_durchschnitt REAL,    -- BPM
    puls_max INTEGER,          -- BPM
    geschwindigkeit_kmh REAL,  -- km/h
    pace_min_km REAL,          -- min/km
    erstellt_am TIMESTAMP
)
```

#### 2️⃣ Tabelle: `streckenpunkte`
GPS-Trackpoints jeder Aktivität:
```sql
CREATE TABLE streckenpunkte (
    id INTEGER PRIMARY KEY,
    aktivitaet_id INTEGER,     -- Fremdschlüssel
    breite REAL,               -- Latitude
    laenge REAL,               -- Longitude
    hoehe REAL,                -- Meter
    zeitpunkt TEXT,            -- ISO-Format
    puls INTEGER,              -- BPM
    reihenfolge INTEGER        -- Position in Track
)
```

### Verwendung in der App
- ✅ **Speichern:** Neue Aktivität nach Upload → `aktivitaet_speichern_mit_stats()`
- ✅ **Abrufen:** Aktivitätsverlauf → `alle_aktivitaeten_holen()`
- ✅ **Batch-Insert:** GPS-Punkte → `streckenpunkte_speichern_batch()`

### Personen-Verwaltung (`person_db.json`)
JSON-Datei mit Personeninformationen (Name, Geburt, Fotopfad).

---

## 🔧 Module im Detail

### 📍 **GPX_Integration/database/training_db.py**
**Zweck:** SQLite Datenbankabstraktion

**Hauptfunktionen:**
- `verbindung_herstellen()` - DB-Verbindung
- `tabellen_erstellen()` - Initialisierung beim Start
- `aktivitaet_speichern_mit_stats(...)` - Speichert komplette Aktivität
- `streckenpunkte_speichern_batch(...)` - Batch-Insert von GPS-Punkten
- `alle_aktivitaeten_holen()` - Lädt alle Aktivitäten für Dashboard

---

### 🔍 **GPX_Integration/parsers/**

#### `gpx_parser.py`
- Parst **GPX-Dateien** (GPS Exchange Format)
- Extrahiert: Koordinaten, Höhe, Zeitstempel
- Rückgabe: Liste von `Streckenpunkt`-Objekten

#### `tcx_parser.py`
- Parst **TCX-Dateien** (Training Center XML, Garmin)
- Extrahiert: Koordinaten, Höhe, Zeitstempel, Puls
- Robust gegen Fehler mit `except Exception`-Handling

#### `fit_parser.py`
- Parst **FIT-Dateien** (Garmin binary format)
- Nutzt `fitparse`-Bibliothek
- Extrahiert: Position, Höhe, Herzfrequenz, Cadence

---

### 📈 **GPX_Integration/logic/statistiken.py**

Berechnet 7 Kern-Metriken aus Trackpoints:

| Funktion | Berechnung |
|---|---|
| `gesamt_distanz()` | Haversine-Distanz zwischen allen Points |
| `gesamt_dauer()` | Zeitspanne Start→Ende |
| `hoehenmeter()` | Positive/Negative Elevation-Änderung |
| `durchschnitt_puls()` | Mittelwert aller Pulswerte |
| `maximal_puls()` | Max Herzfrequenz |
| `durchschnittsgeschwindigkeit()` | distanz_km / dauer_h |
| `pace()` | dauer_min / distanz_km |

Alle Funktionen mit robustem **Datetime-Parsing** via `_parse_datetime()`.

---

### 📊 **GPX_Integration/logic/hoehenprofil_interaktiv.py**

Interaktive Elevation-Profil-Berechnung:

| Funktion | Zweck |
|---|---|
| `compute_elevation_profile()` | Bereitet Höhendaten für Visualisierung auf |
| `get_segment_stats()` | Statistiken (Steigung, Distanz) pro Segment |
| `get_point_details_at_index()` | Detail-Info bei Höhenschieberegler |
| `haversine_distance()` | GPS-Distanz zwischen zwei Punkten |

**UI-Integration:** Schieberegler aktualisiert Karte + Statistiken in Echtzeit.

---

### 💚 **Personen/klasse_ekgdata.py**

EKG-Signalanalyse mit scipy Peak-Detection:

| Methode | Zweck |
|---|---|
| `lade_ekg_nach_id()` | EKG-Datei für Person laden |
| `peaks()` | R-Peak-Erkennung (Herzschläge) |
| `herzrate()` | Herzrate aus Peaks berechnen |
| `herzratenvariabilität()` | HRV (Varianz der RR-Intervalle) |
| `plot_herzrate()` | Zeitreihen-Plot |
| `plot_hrv()` | HRV-Spektralanalyse |

---

### 📊 **CSV_analyse/**

#### `power_curve.py`
- Berechnet beste durchschnittliche **Leistung pro Zeitfenster**
- Rolling-Window-Mechanismus
- Nutzt `PowerOriginal`-Spalte aus CSV

#### `zonen_einteilung.py`
- Teilt Trainingseinheiten in **Herzfrequenzzonen** (Z1-Z5)
- Berechnung basierend auf HRMax
- Prozentuale Verteilung pro Zone

---

## 🎯 Workflow: GPX-Upload bis Speicherung

```
1. Benutzer lädt GPX/TCX/FIT-Datei
                    ↓
2. Entsprechender Parser lädt Trackpoints
                    ↓
3. statistiken.py berechnet 7 Metriken
                    ↓
4. hoehenprofil_interaktiv.py erstellt Höhendaten
                    ↓
5. karten_erstellung.py rendert Folium-Karte
                    ↓
6. Streamlit zeigt Karte + Höhenprofil + Statistiken
                    ↓
7. Benutzer klickt "Speichern"
                    ↓
8. aktivitaet_speichern_mit_stats() speichert in training.db
   └─ aktivitaet_speichern_batch() speichert alle GPS-Punkte
                    ↓
9. Daten erscheinen im "Aktivitätsverlauf"-Tab
```

---

## 📝 Docstring-Standard

Alle Funktionen haben **1-2 Sätze Dokumentation**:

```python
def berechne_distanz(koordinaten: list) -> float:
    """Berechnet die Gesamtstrecke zwischen GPS-Punkten mittels Haversine-Formel."""
    ...
```

---

## ⚙️ Konfiguration

### Abtastrate
```python
abtastrate = 100  # Hz, in interfaceWebsite.py
```

### Datenverzeichnisse
```python
DATA_DIR = BASE_DIR / "data"
ORDNER_EKG = DATA_DIR / "ekg_data"
ORDNER_SORTIERT = DATA_DIR / "data_sortiert"
BILDER_DIR = DATA_DIR / "pictures"
```

Alle Verzeichnisse werden beim Start automatisch erstellt.

---

## 🐛 Fehlerbehandlung

- ✅ **Bare except → except Exception** (PEP 8 konform)
- ✅ **Robustes Datetime-Parsing** mit Fallback-Logik
- ✅ **Dateiformat-Fehler** werden abgefangen
- ✅ **SQLite-Verbindungsfehler** mit `con.close()`-Cleanup

---

## 📜 Lizenz

Projekt für Ausbildung/Evaluation

---

## 👨‍💻 Entwicklung

### Abhängigkeiten aktualisieren
```bash
pip install -r DashboardIntergrationII/requirements.txt --upgrade
```

### Tests ausführen (optional)
```bash
pytest  # Wenn Test-Framework hinzugefügt
```

### Git-Workflow
```bash
git add .
git commit -m "Feature: XYZ"
git push origin main
```

---

## 📞 Support

Bei Fragen oder Fehlern:
1. Überprüfe `requirements.txt` auf passende Versionen
2. Stelle sicher, dass `.venv` aktiviert ist
3. Überprüfe Dateirechte für `data/`-Verzeichnis
4. Konsultiere Fehlerausgabe in Streamlit-Terminal

---

**Viel Spaß mit der App! 🚀💓🏃**
