# Dashboard Integration II - Trainings- & EKG-Analyseplattform

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
├── interfaceWebsite.py             # Hauptanwendung (Streamlit UI)
├── main.py                         # Streamlit-Wrapper für den Start 
├── requirements.txt                # Abhängigkeiten
├── pyproject.toml                  # Projektconfig
│
├── Personen/                       # Personalmanagement
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

## Installation mit PIP

### Voraussetzungen
- **Python 3.12 oder neuer**
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
pip install -r requirements.txt
```

### Schritt 4: Anwendung starten
```bash
streamlit run main.py
```

## Installation mit PDM

### Schritt 1: PDM installieren
Falls PDM noch nicht installiert ist:
```bash
pip install pdm
```

### Schritt 2: Projektabhängigkeiten installieren
```bash
pdm install
```

### Schritt 3: Anwendung starten
```bash
pdm run streamlit run main.py
```


Hinweis: `streamlit run interfaceWebsite.py` funktioniert ebenfalls. `main.py` ist der empfohlene Einstiegspunkt, weil es direkt an die eigentliche App weiterleitet.

---

## Verwendung

### Personen verwalten
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

### CSV-Analyse
1. Gehe zu **"CSV Analyse"**
2. Analysiere Trainings- und Leistungsdaten in den Zonen- und Power-Ansichten
3. Erkenne dabei Auffälligkeiten und prüfe die Verteilung der Werte

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

## Datenspeicherung

### SQLite Datenbank (`training.db`) 
Zentrale **Speicherung aller Trainingsaktivitäten** mit zwei Tabellen:

#### Tabelle: `aktivitaeten`
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

#### Tabelle: `streckenpunkte`
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

## Basis-Aufgaben und Freie Aufgaben

### Basis-Aufgaben
- Alle genannten Basis-Aufgaben wurden in die App eingebaut und umgesetzt.


### Freie Aufgaben
- Auch alle genannten freien Aufgaben wurden in die App integriert.

---
## Eigene Features

### Startseite & Nutzerverwaltung
- Individueller Farbmodus und frei wählbare Hintergründe zur persönlichen Anpassung der App.
- Erweiterte Nutzerverwaltung: Nutzer löschen.
- Visuelles Feedbacksystem.
    - Nach jeder Aktion erscheint eine grüne Bestätigungsmeldung.
    - Beim Löschen erfolgt zusätzlich eine zweite Sicherheitsabfrage, um Fehlbedienungen zu vermeiden.

### EKG-Analyse & Visualisierung
- Interaktive Plot-Steuerung: Peaks und Signalanteile können ein- und ausgeschaltet werden.
- Flexible Zeitfenstersteuerung: Der betrachtete Zeitraum lässt sich frei in beide Richtungen verschieben.
- Herzfrequenz-Plot: Alle HR-Attribute können individuell ein- oder ausgeblendet werden.
- Verschiebbare Messbereiche: Beide Begrenzungspunkte („Knöpfe“) lassen sich frei und in beide Richtungen verschieben.
- HRV-Simulation.
    - Kritische HRV-Werte lösen ein rotes Warnsignal aus.
    - Sichere Werte erzeugen ein grünes „Alles in Ordnung“-Signal.

### CSV-Analyse & Anomalieerkennung
- Anomalienmarkierung im Plot: Auffälligkeiten werden im EKG- und Leistungsplot durch ein Kreuz hervorgehoben.
- Detaillierte Anomalieerklärung: Zu jeder Auffälligkeit gibt es eine präzise Beschreibung mit konkreten Messwerten.
- Simulation künstlicher Testdaten.
    - Zur Veranschaulichung von Anomalien passt sich der Plot dynamisch an.
    - Die Anomalietabelle aktualisiert sich entsprechend.
    - Künstliche Anomalien können ein- und ausgeschaltet werden.
- Interaktive Tabellenansicht: Zoneninformationen lassen sich durch Klick auf Spaltenüberschriften beliebig neu sortieren.

### Training & Leistungsanalyse
- SQLite-Integration zur lokalen Speicherung aller Trainingsdaten.
- Automatischer Analyse-Start: Sobald eine ausgewählte Datei hochgeladen wurde, beginnt die Trainingsanalyse und alle relevanten Bereiche öffnen sich.
- Importfunktion für Fitness-Tracking-Dateien (Strava, Garmin, weitere Apps).
- Sportart-Auswahl zur präzisen Kategorisierung der Aktivität.
- Umfassende Trainingsstatistiken für jede Aktivität.
- Dynamisches Höhenprofil.
    - Das Profil lässt sich über die gesamte Distanz verschieben.
    - Zu jedem Punkt werden Höhe, Steigung und exakte Kilometer angezeigt.
    - Beim Bewegen der Maus entlang der Kurve werden alle Werte live eingeblendet.
- Aktivitäten speichern & Verlauf anzeigen.
    - Aktivitäten können dauerhaft gespeichert werden.
    - Im Aktivitätsverlauf lassen sich die wichtigsten Werte vergleichen.
- Filterfunktion nach Sportart für eine schnelle Übersicht.
- Detailansicht für ausgewählte Trainings: Beliebig ausgewählte Trainings lassen sich im Aktivitätsverlauf anklicken und in einem separaten Fenster öffnen. Dort erhält man erneut einen kompakten Überblick über alle wichtigen Informationen der jeweiligen Aktivität.
- Aktivitäten sicher löschen: Beim Löschen öffnet sich ein eigenes Dialogfenster, in dem die gewünschte Aktivität ausgewählt wird. Anschließend muss der Löschvorgang über einen zweiten Button bestätigt werden, damit keine Daten versehentlich gelöscht werden können.

---
### Autoren
---
- Lenn Oßwald
- Noah Reinermann
