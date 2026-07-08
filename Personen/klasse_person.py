from datetime import datetime

class Person:
    """
    Repräsentiert eine Person aus der Datenbank und stellt Funktionen zur
    Alters- und Maximalpulsberechnung bereit. Übernimmt alle relevanten
    Personendaten wie Name, Bildpfad und Geburtsdatum.
    """
    def __init__(self, person_dict):
        """ 
        Personenobjekt wird angelegt und alle Daten werden übernommen.
        """
        self.vorname = person_dict.get("firstname", "")
        self.nachname = person_dict.get("lastname", "")
        self.bildpfad = person_dict.get("picture_path", "")
        self.id = person_dict.get("id", None)

        geboren = str(person_dict.get("date_of_birth", ""))
        if len(geboren) == 4 and geboren.isdigit():
            self.geburtsdatum = f"{geboren}-01-01"
        else:
            self.geburtsdatum = geboren

    def berechne_alter(self):
        """
        Alter der Person wird berechnet, indem das Geburtsjahr von dem aktuellen Jahr subtrahiert wird.
        """
        geburt= str(self.geburtsdatum)
        if "-" in geburt:
            jahr = int(geburt.split("-")[0])
        else:
            jahr = int(geburt)
        return datetime.now().year - jahr
    
    def berechne_max_puls(self):
        """
        Maximalpuls wird anhand dem Alter der Person berechnet.
        """
        alter = self.berechne_alter()
        if alter <= 0:
            return None
        max_puls = 220 - alter
        return max_puls
    
