from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import neurokit2 as nk
from scipy.signal import find_peaks

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "person_db.json"

class EKGData:
    def __init__(self, ekg_info):
        self.id = ekg_info.get("id")
        self.datum = ekg_info.get("date")
        self.pfad = ekg_info.get("result_link")

        try:
            self.df = pd.read_csv(self.pfad, sep="\t", header=None, names=["Messwert", "Zeit"])
        except:
            print("Fehler beim Laden der Datei:", self.pfad)
            self.df = pd.DataFrame(columns=["Messwert", "Zeit"])

        self.start = None
        self.ende = None
        self.rate = None

    @staticmethod
    def lade_ekg_nach_id(ekg_id, personen_liste):
        for person in personen_liste:
            for ekg in person.get("ekg_tests", []):
                if ekg.get("id") == ekg_id:
                    return ekg
        return None

    def zeitbereich(self, start, ende, rate):
        df = self.df_plot()
        if start is None:
            self.start = df["Zeit"].min()
        else:
            self.start = float(start)
        if ende is None:
            self.ende = df["Zeit"].max()
        else:
            self.ende = float(ende)

        self.rate = float(rate)

    def plot_basis(self):
        fig = px.line(self.df, x="Zeit", y="Messwert")
        return fig
    
    def df_plot(self):
        if self.df.empty:
            return self.df
        df = self.df.copy()
        df["Zeit"] = (df["Zeit"] - df["Zeit"].iloc[0]) / 1000
        return df

    def df_bereich(self):
        if self.start is None or self.ende is None:
            return self.df
        df = self.df_plot()
        return df[(df["Zeit"] >= self.start) & (df["Zeit"] <= self.ende)].reset_index(drop=True)
    
    def peaks(self):
        df = self.df_plot()
        werte = df["Messwert"].to_numpy()
        zeit = df["Zeit"].to_numpy()

        if len(zeit) < 2:
            self.peaks_alle = []
            self.peaks_teil = []
            return

        sekunden_pro_sample = np.mean(np.diff(zeit))
        min_distance_samples = int(0.3 / sekunden_pro_sample) if sekunden_pro_sample > 0 else 1
        schwelle = np.mean(werte) + np.std(werte)

        peaks, _ = find_peaks(werte, height=schwelle, distance=min_distance_samples)
        self.peaks_alle = list(peaks)

        if self.start is not None and self.ende is not None:
            self.peaks_teil = [
                p for p in self.peaks_alle
                if self.start <= df["Zeit"].iloc[p] <= self.ende
            ]
        else:
            self.peaks_teil = self.peaks_alle
        
    def anzeigen_signale(self):
        df = self.df_plot()
        self.peaks()
        fig = go.Figure()
        fig.add_scatter(x=df["Zeit"], y=df["Messwert"], mode="lines", name="Signal")
        if len(self.peaks_alle) > 0:
            fig.add_scatter(x=df["Zeit"].iloc[self.peaks_alle], y=df["Messwert"].iloc[self.peaks_alle], mode="markers", marker=dict(color="red", size=10), name="Peaks")
        fig.update_xaxes(range=[self.start, self.ende])
        return fig

    def peak_times(self):
        self.peaks()
        if not self.peaks_alle:
            return np.array([])
        return self.df_plot()["Zeit"].iloc[self.peaks_alle].to_numpy()

    def herzrate(self):
        peak_times = self.peak_times()
        if len(peak_times) < 2:
            return 0.0

        intervals = np.diff(peak_times)
        if np.any(intervals <= 0):
            intervals = intervals[intervals > 0]
        if len(intervals) == 0:
            return 0.0

        return 60.0 / np.mean(intervals)

    def herzrate_bereich(self, start, ende):
        peak_times = self.peak_times()
        if len(peak_times) < 2:
            return 0.0

        selected = peak_times[(peak_times >= start) & (peak_times <= ende)]
        if len(selected) < 2:
            return 0.0

        intervals = np.diff(selected)
        if np.any(intervals <= 0):
            intervals = intervals[intervals > 0]
        if len(intervals) == 0:
            return 0.0

        return 60.0 / np.mean(intervals)

    def plot_herzrate(self, start=None, ende=None):
        # Alle Peak-Zeiten
        all_peak_times = self.peak_times()
        if len(all_peak_times) < 2:
            return go.Figure()

        # Gesamtmittel über das gesamte Signal (wenn möglich) - nur positive Intervalle
        all_intervals = np.diff(all_peak_times)
        valid_all = all_intervals > 0
        all_intervals_valid = all_intervals[valid_all]
        if len(all_intervals_valid) == 0:
            return go.Figure()

        durchschnitt_global = np.mean(60.0 / all_intervals_valid)

        # Wähle Peak-Zeiten für die Darstellung (Bereich oder gesamtes Signal)
        if start is not None and ende is not None:
            peak_times = all_peak_times[(all_peak_times >= start) & (all_peak_times <= ende)]
        else:
            peak_times = all_peak_times

        if len(peak_times) < 2:
            return go.Figure()

        intervals_all = np.diff(peak_times)
        valid = intervals_all > 0
        intervals = intervals_all[valid]
        if len(intervals) == 0:
            return go.Figure()

        # Zeitpunkte als Mittelpunkte, nur für gültige Intervalle
        zeitpunkte_all = (peak_times[:-1] + peak_times[1:]) / 2.0
        zeitpunkte = zeitpunkte_all[valid]

        herzrate_werte = 60.0 / intervals

        # Erstelle Plot: rohe Herzratenwerte + gleitender Durchschnitt + Gesamtdurchschnitt
        fig = go.Figure()

        fig.add_scatter(
            x=zeitpunkte,
            y=herzrate_werte,
            mode="lines+markers",
            name="Herzrate (instant)",
            line=dict(color="green"),
            marker=dict(size=6)
        )

        # Gleitender Durchschnitt (zeitbasiert approximiert über 5 Sekunden)
        mean_dt = np.mean(np.diff(zeitpunkte)) if len(zeitpunkte) > 1 else 1.0
        window_seconds = 5.0
        window_points = max(1, int(window_seconds / mean_dt))
        if window_points > 1 and len(herzrate_werte) >= 1:
            kernel = np.ones(window_points) / float(window_points)
            gleit = np.convolve(herzrate_werte, kernel, mode="same")
        else:
            gleit = herzrate_werte

        fig.add_scatter(
            x=zeitpunkte,
            y=gleit,
            mode="lines",
            name=f"Gleit. Mittel ({window_seconds:.0f}s)",
            line=dict(color="blue", width=3)
        )

        # Bestimme x-range für Durchschnittslinien
        if start is not None and ende is not None:
            x0, x1 = float(start), float(ende)
        elif len(zeitpunkte) > 0:
            x0, x1 = float(np.min(zeitpunkte)), float(np.max(zeitpunkte))
        else:
            x0, x1 = 0.0, 1.0

        # Linie für den globalen Durchschnitt (gesamter Test) als Legendentrace
        fig.add_scatter(
            x=[x0, x1],
            y=[durchschnitt_global, durchschnitt_global],
            mode="lines",
            name="Durchschnitt ges. (BPM)",
            line=dict(color="red", dash="dash"),
        )

        # Durchschnitt im gewählten Bereich (falls Bereich gesetzt) als Legendentrace
        if start is not None and ende is not None:
            durchschnitt_bereich = np.mean(herzrate_werte)
            fig.add_scatter(
                x=[x0, x1],
                y=[durchschnitt_bereich, durchschnitt_bereich],
                mode="lines",
                name="Durchschnitt Bereich (BPM)",
                line=dict(color="orange", dash="dot"),
            )

        fig.update_layout(
            title="Herzrate über die Zeit",
            xaxis_title="Zeit [s]",
            yaxis_title="Herzrate [BPM]",
            legend=dict(orientation="v", x=1.02, y=1),
            margin=dict(r=180)
        )

        # X-Achse anpassen: benutze übergebenen Bereich, ansonsten interne Einstellungen
        if start is not None and ende is not None:
            fig.update_xaxes(range=[start, ende])
        elif self.start is not None and self.ende is not None:
            fig.update_xaxes(range=[self.start, self.ende])
        return fig
    
    def test_datum(self):
        datum = self.datum
        return(datum)
    
    def dateipfad(self):
        return self.pfad
    
    def zeitreihe_dauer(self):
        if self.df.empty:
            return 0.0
        df = self.df_plot()
        if len(df) < 2:
            return 0.0
        return float(df["Zeit"].iloc[-1] - df["Zeit"].iloc[0])

    def herzratenvariabilität(self):
        # HRV-Berechnung temporär deaktiviert aufgrund von neurokit2-Instabilität
        # Wird nur mit sehr langen Signalen berechnet (>10000 Punkte)
        # Berechne einfache Zeitbereichs-HRV (Time-domain) aus Peak-Zeiten
        if self.df.empty:
            return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}

        self.peaks()
        peak_times = self.peak_times()
        if len(peak_times) < 2:
            return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}

        # RR-Intervalle in Sekunden
        rr_sec = np.diff(peak_times)
        rr_sec = rr_sec[rr_sec > 0]
        if len(rr_sec) == 0:
            return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}

        # Konvertiere in ms (konform zur bisherigen UI, die durch 1000 teilt)
        rr_ms = rr_sec * 1000.0

        return {
            "HRV_MeanNN": float(np.mean(rr_ms)),
            "HRV_MinNN": float(np.min(rr_ms)),
            "HRV_MaxNN": float(np.max(rr_ms)),
        }
   
    def herzratenvariabilität_bereich(self, start=None, ende=None):
        # HRV für einen angegebenen Bereich (start, ende in Sekunden).
        if self.df.empty:
            return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}

        self.peaks()
        peak_times = self.peak_times()

        # Wähle peaks innerhalb übergebenem Bereich oder alle
        if start is None and ende is None:
            selected = peak_times
        else:
            selected = peak_times[(peak_times >= float(start)) & (peak_times <= float(ende))]

        if len(selected) < 2:
            return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}

        rr_sec = np.diff(selected)
        rr_sec = rr_sec[rr_sec > 0]
        if len(rr_sec) == 0:
            return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}

        rr_ms = rr_sec * 1000.0
        return {
            "HRV_MeanNN": float(np.mean(rr_ms)),
            "HRV_MinNN": float(np.min(rr_ms)),
            "HRV_MaxNN": float(np.max(rr_ms)),
        }

    def plot_hrv(self, start=None, ende=None, simulate=False):
        """Plot der NN-Intervalle (ms) über die Zeit mit globalem und Bereichs-Mittel.

        start/ende optional: Bereich zum Hervorheben und Berechnen des Bereichs-Mittel.
        simulate: Wenn True, verwende kritische Testwerte für Linien und Warnung.
        """
        peak_times = self.peak_times()
        if len(peak_times) < 2:
            return go.Figure()

        all_rr_sec = np.diff(peak_times)
        valid = all_rr_sec > 0
        rr_sec = all_rr_sec[valid]
        if len(rr_sec) == 0:
            return go.Figure()

        rr_ms = rr_sec * 1000.0
        timepoints_all = (peak_times[:-1] + peak_times[1:]) / 2.0
        timepoints = timepoints_all[valid]

        fig = go.Figure()
        fig.add_scatter(x=timepoints, y=rr_ms, mode="lines+markers", name="NN-Intervalle [ms]", line=dict(color="purple"))

        # globales Mittel
        if simulate:
            global_mean = 150.0
        else:
            hrv_global = self.herzratenvariabilität()
            if hrv_global and hrv_global.get("HRV_MeanNN") is not None:
                global_mean = float(hrv_global["HRV_MeanNN"])
            else:
                global_mean = None

        if global_mean is not None:
            # Bestimme x-range
            if start is not None and ende is not None:
                gx0, gx1 = float(start), float(ende)
            elif len(timepoints) > 0:
                gx0, gx1 = float(np.min(timepoints)), float(np.max(timepoints))
            else:
                gx0, gx1 = 0.0, 1.0
            fig.add_scatter(x=[gx0, gx1], y=[global_mean, global_mean], mode="lines", name="Durchschnitt NN ges. (ms)", line=dict(color="red", dash="dash"))

        # Bereichs-Mittel falls Bereich angegeben
        if start is not None and ende is not None:
            # Filtere RR nach Zeitpunkten innerhalb Bereich (mittelpunkte)
            mask = (timepoints >= start) & (timepoints <= ende)
            if np.any(mask):
                if simulate:
                    region_mean = 150.0
                else:
                    rr_region = rr_ms[mask]
                    region_mean = float(np.mean(rr_region))
                fig.add_scatter(x=[start, ende], y=[region_mean, region_mean], mode="lines", name="Durchschnitt NN Bereich (ms)", line=dict(color="orange", dash="dot"))

            # Bereich schattieren (unter den Daten, ohne Legendeneintrag)
            fig.add_shape(type="rect", x0=start, x1=ende, y0=0, y1=1, yref="paper", xref="x", fillcolor="LightSalmon", opacity=0.12, layer="below", line_width=0)

        fig.update_layout(title="NN-Intervalle / Herzvariabilität", xaxis_title="Zeit [s]", yaxis_title="NN-Intervall [ms]", legend=dict(orientation="v", x=1.02, y=1), margin=dict(r=180))
        if start is not None and ende is not None:
            fig.update_xaxes(range=[start, ende])

        return fig

    def pruefe_hrv(self, hrv):
        # Wenn HRV nicht berechnet werden konnte
        if hrv is None or hrv.get("HRV_MeanNN") is None:
            return "danger", "HRV konnte nicht berechnet werden – zu wenige Peaks oder schlechte Signalqualität."

        try:
            import pandas as pd
            
            # HRV-Werte extrahieren und zu Float konvertieren
            meanNN_raw = hrv["HRV_MeanNN"]
            minNN_raw = hrv["HRV_MinNN"]
            maxNN_raw = hrv["HRV_MaxNN"]
            
            # Pandas Series zu float konvertieren
            if isinstance(meanNN_raw, pd.Series):
                meanNN = float(meanNN_raw.iloc[0]) / 1000
            else:
                meanNN = float(meanNN_raw) / 1000
                
            if isinstance(minNN_raw, pd.Series):
                minNN = float(minNN_raw.iloc[0]) / 1000
            else:
                minNN = float(minNN_raw) / 1000
                
            if isinstance(maxNN_raw, pd.Series):
                maxNN = float(maxNN_raw.iloc[0]) / 1000
            else:
                maxNN = float(maxNN_raw) / 1000
                
        except Exception as e:
            print(f"Fehler bei HRV-Konvertierung: {e}")
            return "danger", "HRV-Werte konnten nicht verarbeitet werden."

        # Gefährliche Werte prüfen
        try:
            if float(minNN) < 0.2 or float(maxNN) > 2.0 or float(meanNN) < 0.4 or float(meanNN) > 1.5:
                return "danger", (
                    "Achtung! Die HRV-Werte liegen außerhalb des normalen Bereichs. "
                    "Dies kann auf Stress, Überlastung, Messfehler oder ungewöhnliche Herzaktivität hinweisen."
                )
        except:
            pass

        # Alles gut
        return "success", "Die HRV-Werte liegen im normalen Bereich. Das Herz zeigt eine gesunde Anpassungsfähigkeit."




if __name__ == "__main__":
    import json

    # EKG-Datenbank laden
    with open(DATA_PATH, "r", encoding="utf-8") as datei:
        datenbank = json.load(datei)

    # Ersten EKG-Test der ersten Person auswählen
    ekg_info = datenbank[0]["ekg_tests"][0]

    # Objekt erzeugen
    ekg = EKGData(ekg_info)

    # Analysebereich setzen (Startzeit, Endzeit, Abtastrate)
    ekg.zeitbereich(start=0, ende=5, rate=500)

    # Grundlegende Infos testen
    print("EKG-ID:", ekg.id)
    print("Datum:", ekg.test_datum())
    print("Zeitreihenlänge (Sekunden):", ekg.zeitreihe_dauer())

    # Peaks testen
    ekg.peaks()
    print("Peaks gesamt:", ekg.peaks_alle)
    print("Peaks im Bereich:", ekg.peaks_teil)

    # Herzrate testen
    hr_gesamt, hr_bereich = ekg.herzrate()
    print("Herzrate gesamt:", hr_gesamt)
    print("Herzrate im Bereich:", hr_bereich)

    # HRV testen
    hrv = ekg.herzratenvariabilität()
    print("HRV gesamt:", hrv)

    hrv_bereich = ekg.herzratenvariabilität_bereich()
    print("HRV im Bereich:", hrv_bereich)

    # Plots erzeugen
    fig_signal = ekg.anzeigen_signale()
    fig_herzrate = ekg.plot_herzrate()

    
