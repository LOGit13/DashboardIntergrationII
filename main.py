"""Minimaler Streamlit-Einstiegspunkt.

Aufruf: `streamlit run main.py`

Dieser File delegiert direkt an `interfaceWebsite.py`, damit die eigentliche
App im Streamlit-Skriptkontext ausgeführt wird.
"""

from pathlib import Path
import runpy


APP_PATH = Path(__file__).with_name("interfaceWebsite.py")
runpy.run_path(str(APP_PATH), run_name="__main__")
