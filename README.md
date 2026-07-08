# 🏃 Dashboard Integration II - Trainings- & EKG-Analyseplattform

Eine umfassende **Streamlit-basierte Webanwendung** zur Verwaltung von Personen, Analyse von EKG-Daten, Trainingsaktivitäten und sportlicher Leistungsbewertung.

## Kurzüberblick

Unsere App bündelt Personenverwaltung, EKG-Analyse und Trainingsauswertung in einer zentralen Oberfläche. 
Sie hilft dabei, Gesundheits- und Leistungsdaten strukturiert zu erfassen, zu speichern und schnell auszuwerten. 
Im EKG-Bereich unterstützt sie bei der Interpretation von Signalverläufen, Herzfrequenz und HRV-Werten. 
Im Trainingsbereich analysiert sie GPX-, TCX- und FIT-Dateien und berechnet daraus verständliche Leistungskennzahlen. 
Die Hauptaufgabe der App ist es, aus rohen Messdaten klare, vergleichbare Informationen für Betreuung, Training und Entscheidung zu machen.

---




## Projektstruktur

```
DashboardIntergrationII/
│
├── interfaceWebsite.py              # Hauptanwendung (Streamlit UI)
├── main.py                          # Streamlit-Wrapper für den Start 
├── requirements.txt                 # Abhängigkeiten
├── pyproject.toml                   # Projektconfig
│
├── Personen/                        # Personalmanagement
│   ├── klasse_person.py            # Person-Dataclass
│   ├── klasse_ekgdata.py           # EKG-Analyselogik
│   └── daten_einlesen.py           # JSON-I/O
│
├── Personen_Verwaltung/            # Admin-Funktionen
│   └── benutzer_verwaltung.py
│
├── CSV_analyse/                    # Sportdaten-Auswertung
│   ├── power_curve.py              # Leistungskurvenberechnung
│   └── zonen_einteilung.py         # Herzfrequenzzone-Analyse
│
├── GPX_Integration/                # Trainings-GPS-Daten
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
└── data/                           # Datenspeicher
    ├── person_db.json              # Personenverwaltung
    ├── activity.csv                # Aktivitätsdaten
    ├── training.db                 # SQLite-Datenbank 
    ├── ekg_data/                   # EKG-Messdateien
    ├── data_sortiert/              # Verarbeitete EKG-Daten
    └── pictures/                   # Benutzerfotos
```

---

## Installation

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
streamlit run main.py
```

Die App öffnet sich unter `http://localhost:8501`

Hinweis: `streamlit run interfaceWebsite.py` funktioniert ebenfalls. `main.py` ist der empfohlene Einstiegspunkt, weil es direkt an die eigentliche App weiterleitet.

---

## Verwendung

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
5. Wenn keine EKG-Daten vorhanden sind, erscheint eine freundliche Info statt einer Fehlermeldung

### Training hochladen
1. Gehe zu **"Training Leistungen"** → **"Neue Aktivität"**
2. Lade eine **GPX/TCX/FIT-Datei** hoch
3. Wähle **Sportart** und **Startzeit**
4. System berechnet automatisch:
   - Strecke auf interaktiver Karte
   - Höhenprofil mit Details
   - 7 Statistiken (Distanz, Dauer, Höhenmeter, Puls, Geschwindigkeit, Pace)
5. Speichern → Daten in SQLite-DB gespeichert

### Aktivitätsverlauf ansehen
1. **"Training Leistungen"** → **"Aktivitätsverlauf"**
2. Filtere nach **Sportart**
3. Die Tabelle wird direkt unter dem Sportarten-Filter angezeigt
4. Klicke auf **"Aktivität löschen"**, wähle eine Aktivität aus und bestätige den Löschvorgang
5. Klicke auf eine Aktivität für Details (Karte + Statistiken)

### Wenn keine EKG-Daten vorhanden sind
- Die EKG App zeigt dann eine Info-Meldung an, dass sich die Analyse für diese Person nicht ausführen lässt
- Es wird kein Fehler ausgelöst und die App bleibt bedienbar

---

## Funktionen

- **Startseite:** Kurzer Überblick über die App und zentrale Einstellungen wie Farbmodus/Hintergrund.
- **Personen Verwaltung:** Personen anlegen, bearbeiten und löschen, inklusive EKG-Dateien zuordnen.
- **EKG App:** EKG-Daten einer Person visualisieren und Herzrate sowie HRV analysieren.
- **CSV Analyse:** CSV-Trainingsdaten auswerten, Zonen prüfen und Anomalien sichtbar machen.
- **Training Leistungen:** GPX/TCX/FIT importieren, Statistiken berechnen, Aktivitäten speichern und Verlauf verwalten.

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
## Eigene Features

### Startseite & Nutzerverwaltung
- **Individueller Farbmodus und frei wählbare Hintergründe** zur persönlichen Anpassung der App.
- **Erweiterte Nutzerverwaltung**: Nutzer löschen.
- **Visuelles Feedbacksystem**.

### EKG-Analyse & Visualisierung
- **Interaktive Plot-Steuerung**: Peaks und Signalanteile können ein- und ausgeschaltet werden.
- **Flexible Zeitfenstersteuerung**: Der betrachtete Zeitraum lässt sich frei in beide Richtungen verschieben.
- **Herzfrequenz-Plot**: Alle HR-Attribute können individuell ein- oder ausgeblendet werden.
- **Verschiebbare Messbereiche**: Beide Begrenzungspunkte ("Köpfe") lassen sich frei und in beide Richtungen verschieben.
- **HRV-Simulation**.

### CSV-Analyse & Anomalieerkennung
- **Anomalienmarkierung im Plot**: Auffälligkeiten werden im EKG- und Leistungsplot durch ein Kreuz hervorgehoben.
- **Detaillierte Anomalieerklärung**: Zu jeder Auffälligkeit gibt es eine präzise Beschreibung mit konkreten Messwerten.
- **Simulation künstlicher Testdaten**.
- **Interaktive Tabellenansicht**: Zoneninformationen lassen sich durch Klick auf Spaltenüberschriften beliebig neu sortieren.

### Training & Leistungsanalyse
- **SQLite-Integration zur lokalen Speicherung aller Trainingsdaten**.
- **Automatischer Analyse-Start**: Sobald eine ausgewählte Datei hochgeladen wurde, beginnt die Trainingsanalyse und alle relevanten Bereiche öffnen sich.
- **Importfunktion für Fitness-Tracking-Dateien** (Strava, Garmin, weitere Apps).
- **Sportart-Auswahl** zur präzisen Kategorisierung der Aktivität.
- **Umfassende Trainingsstatistiken** für jede Aktivität.
- **Dynamisches Höhenprofil**.
- **Aktivitäten speichern & Verlauf anzeigen**.
- **Filterfunktion nach Sportart** für eine schnelle Übersicht.
- **Aktivitäten sicher löschen**: Beim Löschen öffnet sich ein eigenes Dialogfenster, in dem die gewünschte Aktivität ausgewählt wird. Anschließend muss der Löschvorgang über einen zweiten Button bestätigt werden, damit keine Daten versehentlich oder automatisch gelöscht werden können.

---
