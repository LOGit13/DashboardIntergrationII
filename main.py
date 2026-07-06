"""Minimaler Streamlit-Einstiegspunkt.

Aufruf: `streamlit run main.py`

Dieser File enthält nur wenig Code; die gesamte App-Logik bleibt in
`interfaceWebsite.py`.
"""

import importlib

# Importiert die existierende App-Datei. Beim Import wird der Streamlit-UI-Code
# in `interfaceWebsite.py` ausgeführt, sodass `streamlit run main.py` die App
# startet, ohne die Logik hier duplizieren zu müssen.
import interfaceWebsite  # noqa: F401


if __name__ == "__main__":
    # Wenn das Skript direkt mit `python main.py` ausgeführt wird, ist kein
    # zusätzliches Verhalten nötig — Import hat bereits die App aufgebaut.
    pass
