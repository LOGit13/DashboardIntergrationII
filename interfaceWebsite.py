import streamlit as st
import pandas as pd
import math
import os
import json
from PIL import Image
from streamlit_option_menu import option_menu

#import data_resampling
#from Benutzer_Verwaltung import funktion_verwaltung
#from Personen import read_data, Klasse_ekgdata, Klasse_person
#from CSV_analyse import Einteilung_Zonen, Power_Curve

with st.altair_chart:
    selected = option_menu (menu_title= "Menü", options= ["Übersicht", "Personen Verwaltung", "EKG App", "CSV Analyse"])

json_file_link = 'data/person_db.json'
data_json_aktuell = read_data.load_person_data(json_file_link)
