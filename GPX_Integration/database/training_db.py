import os
import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = DB_DIR / "training.db"


def verbindung_herstellen():
    """
    Stellt eine Verbindung zur SQLite-Datenbank her.
    Falls die Datei nicht existiert, wird sie automatisch angelegt.
    """
    return sqlite3.connect(DB_PATH)


def tabellen_erstellen():
    """
    Legt die Tabellen für Aktivitäten und Streckenpunkte an.
    Diese Funktion sollte einmal beim Start der Anwendung ausgeführt werden.
    """

    con = verbindung_herstellen()
    cur = con.cursor()

    # Tabelle für Aktivitäten
    cur.execute("""
        CREATE TABLE IF NOT EXISTS aktivitaeten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            datum TEXT,
            sportart TEXT,
            dauer_sek REAL,
            distanz_km REAL,
            hoehenmeter_positiv REAL DEFAULT 0,
            hoehenmeter_negativ REAL DEFAULT 0,
            puls_durchschnitt REAL,
            puls_max INTEGER,
            geschwindigkeit_kmh REAL,
            pace_min_km REAL,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabelle für Streckenpunkte
    cur.execute("""
        CREATE TABLE IF NOT EXISTS streckenpunkte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aktivitaet_id INTEGER NOT NULL,
            breite REAL,
            laenge REAL,
            hoehe REAL,
            zeitpunkt TEXT,
            puls INTEGER,
            reihenfolge INTEGER,
            FOREIGN KEY (aktivitaet_id) REFERENCES aktivitaeten(id) ON DELETE CASCADE
        )
    """)

    con.commit()
    con.close()


def aktivitaet_speichern_mit_stats(name, datum, sportart, dauer_sek, distanz_km, 
                                   hoehenmeter_positiv, hoehenmeter_negativ,
                                   puls_durchschnitt, puls_max, geschwindigkeit_kmh, pace_min_km):
    """
    Speichert eine komplette Aktivität mit allen Statistiken und gibt die ID zurück.
    """
    tabellen_erstellen()
    con = verbindung_herstellen()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO aktivitaeten 
        (name, datum, sportart, dauer_sek, distanz_km, hoehenmeter_positiv, hoehenmeter_negativ,
         puls_durchschnitt, puls_max, geschwindigkeit_kmh, pace_min_km)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, datum, sportart, dauer_sek, distanz_km, hoehenmeter_positiv, hoehenmeter_negativ,
          puls_durchschnitt, puls_max, geschwindigkeit_kmh, pace_min_km))

    con.commit()
    aktivitaet_id = cur.lastrowid
    con.close()

    return aktivitaet_id


def streckenpunkte_speichern_batch(aktivitaet_id, punkte):
    """
    Speichert mehrere Streckenpunkte auf einmal (batch insert).
    """
    tabellen_erstellen()
    con = verbindung_herstellen()
    cur = con.cursor()

    for i, p in enumerate(punkte):
        breite = getattr(p, 'breite', None) or (p.get('breite') if isinstance(p, dict) else None)
        laenge = getattr(p, 'laenge', None) or (p.get('laenge') if isinstance(p, dict) else None)
        hoehe = getattr(p, 'hoehe', None) or (p.get('hoehe') if isinstance(p, dict) else None)
        zeitpunkt = getattr(p, 'zeitpunkt', None) or (p.get('zeitpunkt') if isinstance(p, dict) else None)
        puls = getattr(p, 'puls', None) or (p.get('puls') if isinstance(p, dict) else None)

        cur.execute("""
            INSERT INTO streckenpunkte (aktivitaet_id, breite, laenge, hoehe, zeitpunkt, puls, reihenfolge)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (aktivitaet_id, breite, laenge, hoehe, zeitpunkt, puls, i))

    con.commit()
    con.close()


def alle_aktivitaeten_holen():
    """
    Holt alle gespeicherten Aktivitäten aus der Datenbank.
    Gibt eine Liste von Dictionaries zurück.
    """
    tabellen_erstellen()
    con = verbindung_herstellen()
    cur = con.cursor()

    cur.execute("""
        SELECT id, name, datum, sportart, dauer_sek, distanz_km, hoehenmeter_positiv, 
               hoehenmeter_negativ, puls_durchschnitt, puls_max, geschwindigkeit_kmh, pace_min_km
        FROM aktivitaeten
        ORDER BY erstellt_am DESC
    """)
    daten = cur.fetchall()

    con.close()

    aktivitaeten = []
    for a in daten:
        aktivitaeten.append({
            "id": a[0],
            "name": a[1],
            "datum": a[2],
            "sportart": a[3],
            "dauer_sek": a[4],
            "distanz_km": a[5],
            "hoehenmeter_positiv": a[6],
            "hoehenmeter_negativ": a[7],
            "puls_durchschnitt": a[8],
            "puls_max": a[9],
            "geschwindigkeit_kmh": a[10],
            "pace_min_km": a[11]
        })

    return aktivitaeten


def streckenpunkte_holen(aktivitaet_id):
    """
    Holt alle Streckenpunkte einer bestimmten Aktivität.
    Gibt eine Liste von Dictionaries zurück.
    """
    tabellen_erstellen()
    con = verbindung_herstellen()
    cur = con.cursor()

    cur.execute("""
        SELECT breite, laenge, hoehe, zeitpunkt, puls
        FROM streckenpunkte
        WHERE aktivitaet_id = ?
        ORDER BY reihenfolge
    """, (aktivitaet_id,))

    daten = cur.fetchall()
    con.close()

    punkte = []
    for p in daten:
        punkte.append({
            "breite": p[0],
            "laenge": p[1],
            "hoehe": p[2],
            "zeitpunkt": p[3],
            "puls": p[4]
        })

    return punkte


def aktivitaet_holen(aktivitaet_id):
    """
    Holt eine einzelne Aktivität anhand ihrer ID.
    Gibt ein Dictionary zurück.
    """
    tabellen_erstellen()
    con = verbindung_herstellen()
    cur = con.cursor()

    cur.execute("""
        SELECT id, name, datum, sportart, dauer_sek, distanz_km, hoehenmeter_positiv, 
               hoehenmeter_negativ, puls_durchschnitt, puls_max, geschwindigkeit_kmh, pace_min_km
        FROM aktivitaeten
        WHERE id = ?
    """, (aktivitaet_id,))

    a = cur.fetchone()
    con.close()

    if a is None:
        return None

    return {
        "id": a[0],
        "name": a[1],
        "datum": a[2],
        "sportart": a[3],
        "dauer_sek": a[4],
        "distanz_km": a[5],
        "hoehenmeter_positiv": a[6],
        "hoehenmeter_negativ": a[7],
        "puls_durchschnitt": a[8],
        "puls_max": a[9],
        "geschwindigkeit_kmh": a[10],
        "pace_min_km": a[11]
    }

