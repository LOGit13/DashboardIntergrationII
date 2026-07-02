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
    # Messwerte und Zeit aus dem DataFrame holen
        werte = self.df["Messwert"].to_numpy()
        zeit = self.df["Zeit"].to_numpy()

    # Zeitabstand zwischen Samples (in ms)
        ms_pro_sample = np.mean(np.diff(zeit))

    # Mindestabstand zwischen Peaks (300 ms)
        min_distance_samples = int(300 / ms_pro_sample)

    # Dynamischer Schwellenwert: Mittelwert + Standardabweichung
        schwelle = np.mean(werte) + np.std(werte)

    # Peaks finden
        peaks, _ = find_peaks(werte, height=schwelle, distance=min_distance_samples)

    # Alle Peaks speichern
        self.peaks_alle = list(peaks)

    # Peaks im Zeitfenster filtern
        if self.start is not None and self.ende is not None:
            self.peaks_teil = [
                p for p in self.peaks_alle
                if self.start <= (p / self.rate) <= self.ende
            ]
        else:
            self.peaks_teil = self.peaks_alle
        
    def anzeigen_signale(self):
        df = self.df_plot()
        self.peaks()
        fig = go.Figure()
        fig.add_scatter(x=df["Zeit"], y=df["Messwert"], mode="lines", name="Signal")
        if len(self.peaks_alle) > 0:
            fig.add_scatter(x=df["Zeit"].iloc[self.peaks_alle], y=df["Messwert"].iloc[self.peaks_alle],mode="markers", marker=dict(color="red", size = 10), name= "Peaks")
        fig.update_xaxes(range=[self.start, self.ende])
        return fig

    def herzrate(self):
        self.peaks()

        if len(self.peaks_alle) > 1:
            abstand = [self.peaks_alle[i+1] - self.peaks_alle[i] for i in range(len(self.peaks_alle)-1)]
            herzrate_überall = 60 / ((sum(abstand) / len(abstand)) / self.rate)
        else:
            herzrate_überall = 0

        if len(self.peaks_teil) > 1:
            abstand_zwei = [self.peaks_teil[i+1] - self.peaks_teil[i] for i in range(len(self.peaks_teil)-1)]
            herzrate_teil = 60 / ((sum(abstand_zwei) / len(abstand_zwei)) / self.rate)
        else:
            herzrate_teil = 0
        return herzrate_überall, herzrate_teil
    
    def plot_herzrate(self, fenster_größe=5):
        df = self.df_plot()
        self.peaks()
        peak_zeiten = df["Zeit"].iloc[self.peaks_alle].tolist()
        if len(peak_zeiten) < fenster_größe + 1:
            return go.Figure()
        
        herzrate_werte = []
        herzrate_zeiten = []

        for start in range(len(peak_zeiten)-fenster_größe):
            t0 = peak_zeiten[start]
            t1 = peak_zeiten[start + fenster_größe]
            if t1 == t0:
                continue

            bpm = 60 * fenster_größe / (t1-t0)

            herzrate_werte.append(bpm)
            herzrate_zeiten.append(t0)

        fig = go.Figure()
        fig.add_scatter(x=herzrate_zeiten, y=herzrate_werte, mode="lines", name="Herzrate", line=dict(color="green"))
        fig.update_xaxes(range=[self.start, self.ende])
        return fig
    
    def test_datum(self):
        datum = self.datum
        return(datum)
    
    def dateipfad(self):
        return self.pfad
    
    def zeitreihe_dauer(self):
        return len(self.df) / self.rate
    
    def herzratenvariabilität(self):
        # HRV-Berechnung temporär deaktiviert aufgrund von neurokit2-Instabilität
        # Wird nur mit sehr langen Signalen berechnet (>10000 Punkte)
        if self.df.empty or self.rate is None:
            return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}

        signal = self.df["Messwert"].values
        
        # Nur für sehr lange Signale versuchen
        if len(signal) < 10000:
            print(f"Signal zu kurz für HRV: {len(signal)} Punkte (mindestens 10000 benötigt)")
            return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}
        
        try:
            self.peaks()
            if len(self.peaks_alle) < 2:
                return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}
            
            abtastrate = self.rate
            
            # Nur R-Peaks erkennen
            _, rpeaks_info = nk.ecg_peaks(signal, sampling_rate=abtastrate)
            r_peaks = rpeaks_info.get("ECG_R_Peaks", [])
            
            if r_peaks is None or len(r_peaks) < 2:
                print("Zu wenige R-Peaks gefunden")
                return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}

            r_zeiten = r_peaks / abtastrate
            hrv = nk.hrv_time(r_zeiten, sampling_rate=abtastrate)
            return hrv

        except Exception as e:
            print(f"Fehler in herzratenvariabilität: {e}")
            return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}
   
    def herzratenvariabilität_bereich(self):
        # HRV-Berechnung für Bereich - temporär deaktiviert
        if self.df.empty or self.rate is None:
            return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}

        try:
            self.peaks()
            if len(self.peaks_teil) < 2:
                return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}
            
            df_bereich = self.df_bereich()
            signal = df_bereich["Messwert"].values
            
            # Nur für längere Segmente
            if len(signal) < 500:
                return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}
            
            abtastrate = self.rate

            # Nur R-Peaks erkennen
            _, rpeaks_info = nk.ecg_peaks(signal, sampling_rate=abtastrate)
            r_peaks = rpeaks_info.get("ECG_R_Peaks", [])
            
            if r_peaks is None or len(r_peaks) < 2:
                return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}

            r_zeiten = r_peaks / abtastrate
            hrv_bereich = nk.hrv_time(r_zeiten, sampling_rate=abtastrate)

            return hrv_bereich

        except Exception as e:
            print(f"Fehler in herzratenvariabilität_bereich: {e}")
            return {"HRV_MeanNN": None, "HRV_MinNN": None, "HRV_MaxNN": None}

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

    
