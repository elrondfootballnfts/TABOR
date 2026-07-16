import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os
import base64
import json
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------------------------------------------------------
# 1. PAGE SETUP & CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="TABOR 2026 - Tábor Kezelő Szoftver",
    page_icon="⛺"
)

# -----------------------------------------------------------------------------
# 1.a PASSWORD PROTECTION
# -----------------------------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def check_password():
    if st.session_state.get("password") == "1q2w3e4r":
        st.session_state["authenticated"] = True
        if "password" in st.session_state:
            del st.session_state["password"]
    else:
        st.session_state["authenticated"] = False
        st.error("❌ Helytelen jelszó!")

if not st.session_state['authenticated']:
    st.title("⛺ Tábor Kezelő Szoftver")
    st.write("Az alkalmazás eléréséhez kérjük, adja meg a jelszót:")
    st.text_input("Jelszó", type="password", on_change=check_password, key="password")
    st.stop()


# Premium UI CSS injection
st.markdown("""
    <style>
    /* Main container styling */
    .reportview-container {
        background-color: #f8f9fa;
    }
    
    /* Custom headers */
    h1, h2, h3 {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 700;
    }
    
    /* KPI Card styling */
    .kpi-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
    }
    
    .kpi-card {
        flex: 1;
        border-radius: 16px;
        padding: 24px;
        color: white;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        text-align: center;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.12);
    }
    
    .kpi-title {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        opacity: 0.85;
        font-weight: 600;
    }
    
    .kpi-value {
        font-size: 32px;
        font-weight: 800;
        margin-top: 10px;
        letter-spacing: -0.5px;
    }
    
    .kpi-sub {
        font-size: 12px;
        margin-top: 6px;
        opacity: 0.9;
        font-style: italic;
    }
    
    /* Accommodation Card styling */
    .room-card {
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
        transition: all 0.2s ease-in-out;
        border: 2px solid transparent;
    }
    
    .room-card:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
    }
    
    .room-title {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .room-type {
        font-size: 11px;
        opacity: 0.75;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    .room-occ {
        font-size: 14px;
        font-weight: 600;
        margin-top: 8px;
    }
    
    .room-guests {
        font-size: 12px;
        margin-top: 8px;
        font-style: italic;
        line-height: 1.4;
        border-top: 1px solid rgba(0, 0, 0, 0.08);
        padding-top: 6px;
    }
    
    /* Badges */
    .badge {
        padding: 3px 8px;
        border-radius: 8px;
        font-size: 10px;
        font-weight: bold;
        display: inline-block;
        margin-top: 6px;
    }
    
    .badge-pending {
        background-color: #ff9800;
        color: white;
    }
    
    .badge-final {
        background-color: #4caf50;
        color: white;
    }
    
    /* Note container */
    .ui-note {
        padding: 10px 15px;
        border-radius: 8px;
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
        font-size: 13px;
        color: #0d47a1;
        margin-bottom: 15px;
    }
    
    /* Hide sidebar elements */
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="stSidebarCollapseButton"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. HARDCODED STRUCTURES & DEFAULT DATA
# -----------------------------------------------------------------------------
# Accommodations structure definition
accommodations = [
    # 2-Room Houses (Each room is 4-person capacity)
    {"Név": "Vadász Room 1", "Típus": "Kétszobás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Vadász Room 2", "Típus": "Kétszobás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Füzi Room 1", "Típus": "Kétszobás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Füzi Room 2", "Típus": "Kétszobás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Fa Room 1", "Típus": "Kétszobás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Fa Room 2", "Típus": "Kétszobás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Aurum Room 1", "Típus": "Kétszobás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Aurum Room 2", "Típus": "Kétszobás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Nóra Room 1", "Típus": "Kétszobás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Nóra Room 2", "Típus": "Kétszobás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Ágnes Room 1", "Típus": "Kétszobás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Ágnes Room 2", "Típus": "Kétszobás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    
    # Nagyház Rubin (6 rooms, each 4-person capacity, preferably for Szatmáriak)
    {"Név": "Rubin Room 1", "Típus": "Nagyház Rubin", "Kapacitás": 4, "Megjegyzés": "Preferáltan Szatmáriaknak"},
    {"Név": "Rubin Room 2", "Típus": "Nagyház Rubin", "Kapacitás": 4, "Megjegyzés": "Preferáltan Szatmáriaknak"},
    {"Név": "Rubin Room 3", "Típus": "Nagyház Rubin", "Kapacitás": 4, "Megjegyzés": "Preferáltan Szatmáriaknak"},
    {"Név": "Rubin Room 4", "Típus": "Nagyház Rubin", "Kapacitás": 4, "Megjegyzés": "Preferáltan Szatmáriaknak"},
    {"Név": "Rubin Room 5", "Típus": "Nagyház Rubin", "Kapacitás": 4, "Megjegyzés": "Preferáltan Szatmáriaknak"},
    {"Név": "Rubin Room 6", "Típus": "Nagyház Rubin", "Kapacitás": 4, "Megjegyzés": "Preferáltan Szatmáriaknak"},
    
    # Béla Ház (Max 6-person capacity)
    {"Név": "Béla Ház", "Típus": "Béla Ház", "Kapacitás": 6, "Megjegyzés": "Földszinti kihúzható kanapé, emeleti franciaágy"},
    
    # Attila Ház (Max 8-person capacity, pre-booked: Ruzsáék)
    {"Név": "Attila Ház", "Típus": "Attila Ház", "Kapacitás": 8, "Megjegyzés": "Ruzsáék előfoglalása (Végleges)"},
    
    # VIP Ház (7 Upstairs, 2 Downstairs, each 2-person capacity, pre-booked)
    {"Név": "VIP 1", "Típus": "VIP Ház Emelet", "Kapacitás": 2, "Megjegyzés": "Legjobb szoba - Gézáék (Végleges)"},
    {"Név": "VIP 2", "Típus": "VIP Ház Emelet", "Kapacitás": 2, "Megjegyzés": "Vargáék (Végleges)"},
    {"Név": "VIP 3", "Típus": "VIP Ház Emelet", "Kapacitás": 2, "Megjegyzés": "Mihaiék (Végleges)"},
    {"Név": "VIP 4", "Típus": "VIP Ház Emelet", "Kapacitás": 2, "Megjegyzés": "Mézesék (Végleges)"},
    {"Név": "VIP 5", "Típus": "VIP Ház Emelet", "Kapacitás": 2, "Megjegyzés": "Sándorék (Végleges)"},
    {"Név": "VIP 6", "Típus": "VIP Ház Emelet", "Kapacitás": 2, "Megjegyzés": "Filipék (Végleges)"},
    {"Név": "VIP 7", "Típus": "VIP Ház Emelet", "Kapacitás": 2, "Megjegyzés": "Legjobb szoba - Molnár Csabáék (Végleges)"},
    {"Név": "VIP Fsz 1", "Típus": "VIP Ház Földszint", "Kapacitás": 2, "Megjegyzés": "Kolozsváriék (Végleges)"},
    {"Név": "VIP Fsz 2", "Típus": "VIP Ház Földszint", "Kapacitás": 2, "Megjegyzés": "Gábor Attiláék (Végleges)"},
    
    # Tents (5x 4-person, 3x 3-person, preferably for youth)
    {"Név": "Sátor A", "Típus": "Sátor", "Kapacitás": 4, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor B", "Típus": "Sátor", "Kapacitás": 4, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor C", "Típus": "Sátor", "Kapacitás": 4, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor D", "Típus": "Sátor", "Kapacitás": 4, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor E", "Típus": "Sátor", "Kapacitás": 4, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor F", "Típus": "Sátor", "Kapacitás": 3, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor G", "Típus": "Sátor", "Kapacitás": 3, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor H", "Típus": "Sátor", "Kapacitás": 3, "Megjegyzés": "Fiataloknak/diákoknak"}
]

# Total accommodation capacity calculation
max_capacity = sum(r['Kapacitás'] for r in accommodations)

# Pre-populated guest list with status "Végleges"
prepopulated_guests = [
    # Attila Ház: Ruzsáék (4 people)
    {"Név": "Ruzsa János", "Típus": "Felnőtt", "Szállás": "Attila Ház", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 500.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Ruzsáék előfoglalás"},
    {"Név": "Ruzsa Mária", "Típus": "Felnőtt", "Szállás": "Attila Ház", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 500.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Ruzsáék előfoglalás"},
    {"Név": "Ruzsa Péter", "Típus": "Fiatal/Diák", "Szállás": "Attila Ház", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 400.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Ruzsáék előfoglalás"},
    {"Név": "Ruzsa Kata", "Típus": "Gyerek", "Szállás": "Attila Ház", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 300.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Ruzsáék előfoglalás"},
    
    # VIP Emelet 1-7
    {"Név": "Kovács Géza", "Típus": "Felnőtt", "Szállás": "VIP 1", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 600.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Gézáék (VIP)"},
    {"Név": "Kovács Gézáné", "Típus": "Felnőtt", "Szállás": "VIP 1", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 600.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Gézáék (VIP)"},
    
    {"Név": "Varga István", "Típus": "Felnőtt", "Szállás": "VIP 2", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 300.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Vargáék (VIP)"},
    {"Név": "Varga Ilona", "Típus": "Felnőtt", "Szállás": "VIP 2", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 300.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Vargáék (VIP)"},
    
    {"Név": "Mihai Radu", "Típus": "Felnőtt", "Szállás": "VIP 3", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 500.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Mihaiék (VIP)"},
    {"Név": "Mihai Elena", "Típus": "Felnőtt", "Szállás": "VIP 3", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 500.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Mihaiék (VIP)"},
    
    {"Név": "Mézes Gábor", "Típus": "Felnőtt", "Szállás": "VIP 4", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 250.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Mézesék (VIP)"},
    {"Név": "Mézes Klára", "Típus": "Felnőtt", "Szállás": "VIP 4", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 250.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Mézesék (VIP)"},
    
    {"Név": "Sándor Levente", "Típus": "Felnőtt", "Szállás": "VIP 5", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 400.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Sándorék (VIP)"},
    {"Név": "Sándor Kinga", "Típus": "Felnőtt", "Szállás": "VIP 5", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 400.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Sándorék (VIP)"},
    
    {"Név": "Filip Zoltán", "Típus": "Felnőtt", "Szállás": "VIP 6", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 300.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Filipék (VIP)"},
    {"Név": "Filip Andrea", "Típus": "Felnőtt", "Szállás": "VIP 6", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 300.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Filipék (VIP)"},
    
    {"Név": "Molnár Csaba", "Típus": "Felnőtt", "Szállás": "VIP 7", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 700.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Molnár Csabáék (VIP)"},
    {"Név": "Molnár Éva", "Típus": "Felnőtt", "Szállás": "VIP 7", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 700.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Molnár Csabáék (VIP)"},
    
    # VIP Földszint 1-2
    {"Név": "Kolozsvári András", "Típus": "Felnőtt", "Szállás": "VIP Fsz 1", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 500.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Kolozsváriék (VIP Fsz)"},
    {"Név": "Kolozsvári Júlia", "Típus": "Felnőtt", "Szállás": "VIP Fsz 1", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 500.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Kolozsváriék (VIP Fsz)"},
    
    {"Név": "Gábor Attila", "Típus": "Felnőtt", "Szállás": "VIP Fsz 2", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 250.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Gábor Attiláék (VIP Fsz)"},
    {"Név": "Gábor Beatrix", "Típus": "Felnőtt", "Szállás": "VIP Fsz 2", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 250.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Gábor Attiláék (VIP Fsz)"}
]


# -----------------------------------------------------------------------------
# 2b. BUILDING GROUPS - épület -> szobák leképezés (térkép)
# -----------------------------------------------------------------------------
BUILDING_GROUPS = {
    '1':  {'name': 'Vadász',          'label': '1',  'x': 37.0, 'y': 22.5, 'rooms': ['Vadász Room 1', 'Vadász Room 2']},
    '2':  {'name': 'Füzi',            'label': '2',  'x': 42.5, 'y': 22.5, 'rooms': ['Füzi Room 1', 'Füzi Room 2']},
    '3':  {'name': 'Fa',              'label': '3',  'x': 47.5, 'y': 22.5, 'rooms': ['Fa Room 1', 'Fa Room 2']},
    '4':  {'name': 'Nagyház (Rubin)', 'label': '4',  'x': 53.5, 'y': 16.5, 'rooms': ['Rubin Room 1', 'Rubin Room 2', 'Rubin Room 3', 'Rubin Room 4', 'Rubin Room 5', 'Rubin Room 6']},
    '5':  {'name': 'Aurum',           'label': '5',  'x': 60.5, 'y': 22.5, 'rooms': ['Aurum Room 1', 'Aurum Room 2']},
    '6':  {'name': 'Nóra',            'label': '6',  'x': 65.5, 'y': 22.5, 'rooms': ['Nóra Room 1', 'Nóra Room 2']},
    '7':  {'name': 'Ágnes',           'label': '7',  'x': 70.5, 'y': 22.5, 'rooms': ['Ágnes Room 1', 'Ágnes Room 2']},
    '8':  {'name': 'Béla Ház',        'label': '8',  'x': 76.5, 'y': 22.5, 'rooms': ['Béla Ház']},
    '9':  {'name': 'VIP Ház',         'label': '9',  'x': 10.0, 'y': 36.0, 'rooms': ['VIP 1','VIP 2','VIP 3','VIP 4','VIP 5','VIP 6','VIP 7','VIP Fsz 1','VIP Fsz 2']},
    '10': {'name': 'Attila Ház',      'label': '10', 'x': 84.0, 'y': 60.0, 'rooms': ['Attila Ház']},
    'A':  {'name': 'Sátor A',         'label': 'A',  'x': 28.5, 'y': 17.0, 'rooms': ['Sátor A']},
    'B':  {'name': 'Sátor B',         'label': 'B',  'x': 24.5, 'y': 23.0, 'rooms': ['Sátor B']},
    'C':  {'name': 'Sátor C',         'label': 'C',  'x': 18.0, 'y': 27.0, 'rooms': ['Sátor C']},
    'D':  {'name': 'Sátor D',         'label': 'D',  'x': 16.5, 'y': 33.5, 'rooms': ['Sátor D']},
    'E':  {'name': 'Sátor E',         'label': 'E',  'x': 15.5, 'y': 43.0, 'rooms': ['Sátor E']},
    'F':  {'name': 'Sátor F',         'label': 'F',  'x': 17.5, 'y': 51.0, 'rooms': ['Sátor F']},
    'G':  {'name': 'Sátor G',         'label': 'G',  'x': 19.0, 'y': 57.5, 'rooms': ['Sátor G']},
    'H':  {'name': 'Sátor H',         'label': 'H',  'x': 20.5, 'y': 64.5, 'rooms': ['Sátor H']},
    'K':  {'name': 'Külsős Vendégek', 'label': '👤', 'x': 50.0, 'y': 8.0, 'rooms': ['Külsős (Nincs)', 'Külsős (Sátor)', 'Külsős (Lakókocsi)']},
}

# Load saved hotspot positions from JSON (overrides defaults)
_POS_FILE = "hotspot_positions.json"
if os.path.exists(_POS_FILE):
    try:
        with open(_POS_FILE, 'r', encoding='utf-8') as _pf:
            _saved_pos = json.load(_pf)
        for _bid, _pos in _saved_pos.items():
            if _bid in BUILDING_GROUPS:
                BUILDING_GROUPS[_bid]['x'] = float(_pos['x'])
                BUILDING_GROUPS[_bid]['y'] = float(_pos['y'])
    except Exception:
        pass


# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# MAP COMPONENT DEFINITION
# -----------------------------------------------------------------------------
import os
import os
try:
    _comp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tabor_map_component")
    
    # Custom components need to be robust. We create a wrapper function.
    _raw_map_component = components.declare_component("map_component", path=_comp_path)
    
    def map_component(img_b64, status, edit_mode, key):
        return _raw_map_component(img_b64=img_b64, status=status, edit_mode=edit_mode, key=key, default=None)
        
except Exception as e:
    map_component = None
    st.error(f"Failed to load map component: {e}")

# 3. BUSINESS LOGIC & PRICING ENGINE
# -----------------------------------------------------------------------------
def calculate_accommodation_cost(row):
    guest_type = row.get('Típus', 'Felnőtt')
    accommodation = row.get('Szállás', '')
    shared = bool(row.get('Két család egy szobában', False))
    nights = int(row.get('Éjszakák Száma', 5))
    
    if guest_type == 'Külsős' or "Nincs" in str(accommodation) or not accommodation:
        if "Lakókocsi" in str(accommodation):
            return float(100.0 * nights)
        elif "Sátor" in str(accommodation):
            return float(80.0 * nights)
        return 0.0
        
    is_tent = "Sátor" in str(accommodation)
    
    if guest_type == 'Felnőtt':
        rate = 70.0 if shared else 120.0
    elif guest_type == 'Fiatal/Diák':
        rate = 60.0
    elif guest_type == 'Gyerek':
        rate = 25.0
    elif guest_type == 'Kisgyerek':
        rate = 0.0
    else:
        rate = 120.0
        
    if is_tent:
        rate *= 0.80
        
    return float(rate * nights)

def calculate_meals_cost(meals_str, guest_type, child_menu=False):
    if guest_type == 'Kisgyerek':
        return 0.0
    
    all_meals = ['T_D', 'W_BD', 'W_L', 'Th_BD', 'Th_L', 'F_BD', 'F_L', 'S_BD', 'S_L', 'Su_BD', 'Su_L']
    if not meals_str or str(meals_str).strip() == 'ALL' or str(meals_str).strip() == 'nan':
        active_meals = all_meals
    else:
        active_meals = [m.strip() for m in str(meals_str).split(',') if m.strip()]
        
    is_child = (guest_type == 'Gyerek') or bool(child_menu)
    total = 0.0
    
    for m in active_meals:
        if m == 'T_D':
            total += 30.0 if is_child else 40.0
        elif m == 'Su_BD':
            total += 20.0 if is_child else 30.0
        elif m in ['W_BD', 'Th_BD', 'F_BD', 'S_BD']:
            total += 50.0 if is_child else 70.0
        elif m in ['W_L', 'Th_L', 'F_L', 'S_L', 'Su_L']:
            total += 50.0 if is_child else 60.0
            
    return float(total)

def render_meal_badges(meals_str):
    if not meals_str or str(meals_str).strip() == 'ALL' or str(meals_str).strip() == 'nan':
        return '<span style="font-size: 0.85em; background-color: #2e7d32; color: #ffffff; padding: 3px 8px; border-radius: 6px; font-weight: bold; display: inline-block;">🍽️ Mindegyik étkezést kéri</span>'
    
    meal_options = {
        'T_D':    {"label": "Kedd - Vacsora",           "color": "#ef5350", "type": "vacsora", "emoji": "🌆"},
        'W_BD':   {"label": "Szerda - Reggeli+Vacsora", "color": "#ff9800", "type": "reggelivacsora", "emoji": "🥣"},
        'W_L':    {"label": "Szerda - Ebéd",            "color": "#ffb300", "type": "ebed", "emoji": "🍲"},
        'Th_BD':  {"label": "Csütörtök - Reggeli+Vacsora", "color": "#4caf50", "type": "reggelivacsora", "emoji": "🥣"},
        'Th_L':   {"label": "Csütörtök - Ebéd",         "color": "#66bb6a", "type": "ebed", "emoji": "🍲"},
        'F_BD':   {"label": "Péntek - Reggeli+Vacsora",  "color": "#2196f3", "type": "reggelivacsora", "emoji": "🥣"},
        'F_L':    {"label": "Péntek - Ebéd",            "color": "#29b6f6", "type": "ebed", "emoji": "🍲"},
        'S_BD':   {"label": "Szombat - Reggeli+Vacsora", "color": "#9c27b0", "type": "reggelivacsora", "emoji": "🥣"},
        'S_L':    {"label": "Szombat - Ebéd",           "color": "#ba68c8", "type": "ebed", "emoji": "🍲"},
        'Su_BD':  {"label": "Vasárnap - Reggeli",       "color": "#795548", "type": "reggeli", "emoji": "🥣"},
        'Su_L':   {"label": "Vasárnap - Ebéd",          "color": "#8d6e63", "type": "ebed", "emoji": "🍲"}
    }
    
    active_meals = [m.strip() for m in str(meals_str).split(',') if m.strip()]
    badges = []
    for m in active_meals:
        if m in meal_options:
            opt = meal_options[m]
            if opt['type'] == 'ebed':
                bg_style = f"background-color: {opt['color']}; color: #ffffff; border: 1.5px solid {opt['color']};"
            else:
                bg_style = f"background-color: rgba(255,255,255,0.05); color: {opt['color']}; border: 1.5px solid {opt['color']};"
                
            badges.append(f'<span style="font-size: 0.8em; padding: 3px 8px; border-radius: 6px; margin-right: 6px; margin-bottom: 6px; display: inline-block; font-weight: bold; {bg_style}">{opt["emoji"]} {opt["label"]}</span>')
            
    return '<div style="display: flex; flex-wrap: wrap; margin-top: 6px;">' + "".join(badges) + '</div>'

def calculate_single_guest_cost(row):
    acc_cost = calculate_accommodation_cost(row)
    meals_str = row.get('Étkezések', 'ALL')
    guest_type = row.get('Típus', 'Felnőtt')
    child_menu = bool(row.get('Gyermekmenü', False))
    meals_cost = calculate_meals_cost(meals_str, guest_type, child_menu)
    subtotal = float(acc_cost + meals_cost)
    discount_pct = float(row.get('Kedvezmény (%)', 0.0))
    discount_val = subtotal * (discount_pct / 100.0)
    return float(subtotal - discount_val)

def check_guest_status(row):
    nights = int(row.get('Éjszakák Száma', 5))
    guest_type = row.get('Típus', 'Felnőtt')
    if guest_type != 'Külsős' and nights < 5:
        return 'Függőben'
    return row.get('Státusz', 'Végleges')

def check_deposit(row):
    cost = float(row.get('Összköltség', 0.0))
    paid = float(row.get('Fizetett előleg', 0.0))
    if cost > 0 and paid < (cost * 0.20):
        return "⚠️ Hiányzó előleg"
    return "Rendben"

def calculate_bedo_food(row):
    guest_type = row.get('Típus', 'Felnőtt')
    if guest_type == 'Kisgyerek':
        return 0.0
    meals_str = row.get('Étkezések', 'ALL')
    all_meals = ['T_D', 'W_BD', 'W_L', 'Th_BD', 'Th_L', 'F_BD', 'F_L', 'S_BD', 'S_L', 'Su_BD', 'Su_L']
    if not meals_str or str(meals_str).strip() == 'ALL' or str(meals_str).strip() == 'nan':
        active_meals = all_meals
    else:
        active_meals = [m.strip() for m in str(meals_str).split(',') if m.strip()]
        
    is_child = (guest_type == 'Gyerek') or bool(row.get('Gyermekmenü', False))
    total = 0.0
    for m in active_meals:
        if m == 'T_D':
            total += 30.0 if is_child else 40.0
        elif m == 'Su_BD':
            total += 20.0 if is_child else 30.0
        elif m in ['W_BD', 'Th_BD', 'F_BD', 'S_BD']:
            total += 50.0 if is_child else 70.0
    return float(total)

def calculate_tribel_lunch(row):
    guest_type = row.get('Típus', 'Felnőtt')
    if guest_type == 'Kisgyerek':
        return 0.0
    meals_str = row.get('Étkezések', 'ALL')
    all_meals = ['T_D', 'W_BD', 'W_L', 'Th_BD', 'Th_L', 'F_BD', 'F_L', 'S_BD', 'S_L', 'Su_BD', 'Su_L']
    if not meals_str or str(meals_str).strip() == 'ALL' or str(meals_str).strip() == 'nan':
        active_meals = all_meals
    else:
        active_meals = [m.strip() for m in str(meals_str).split(',') if m.strip()]
        
    is_child = (guest_type == 'Gyerek') or bool(row.get('Gyermekmenü', False))
    total = 0.0
    for m in active_meals:
        if m in ['W_L', 'Th_L', 'F_L', 'S_L', 'Su_L']:
            total += 40.0 if is_child else 60.0
    return float(total)

def recalculate_dataframe(df):
    """Calculates all dynamic columns for the entire guest DataFrame."""
    if df.empty:
        return pd.DataFrame(columns=[
            'Név', 'Típus', 'Szállás', 'Éjszakák Száma', 
            'Két család egy szobában', 'Kedvezmény (%)', 'Fizetett előleg', 'Státusz', 
            'Külsős Ebédek Száma', 'Megjegyzés', 'Étkezések', 'Gyermekmenü', 'Összköltség', 
            'Előleg Státusz', 'Bedő Laci Kaja', 'Tribel Ebéd'
        ])
    
    df['Éjszakák Száma'] = df['Éjszakák Száma'].fillna(5).astype(int)
    df['Külsős Ebédek Száma'] = df['Külsős Ebédek Száma'].fillna(0).astype(int)
    df['Fizetett előleg'] = df['Fizetett előleg'].fillna(0.0).astype(float)
    df['Két család egy szobában'] = df['Két család egy szobában'].fillna(False).astype(bool)
    df['Gyermekmenü'] = df.get('Gyermekmenü', False)
    df['Gyermekmenü'] = df['Gyermekmenü'].fillna(False).astype(bool)
    df['Kedvezmény (%)'] = df.get('Kedvezmény (%)', 0.0)
    df['Kedvezmény (%)'] = pd.to_numeric(df['Kedvezmény (%)'], errors='coerce').fillna(0.0).astype(float)
    df['Étkezések'] = df.get('Étkezések', 'ALL')
    df['Étkezések'] = df['Étkezések'].fillna('ALL').astype(str)
    
    df['Összköltség'] = df.apply(calculate_single_guest_cost, axis=1)
    df['Státusz'] = df.apply(check_guest_status, axis=1)
    df['Előleg Státusz'] = df.apply(check_deposit, axis=1)
    df['Bedő Laci Kaja'] = df.apply(calculate_bedo_food, axis=1)
    df['Tribel Ebéd'] = df.apply(calculate_tribel_lunch, axis=1)
    return df


DB_FILE = "guests_db.csv"

def get_gspread_client():
    # Support credentials in Streamlit secrets or local file
    try:
        if "gcp_service_account" in st.secrets:
            creds_info = st.secrets["gcp_service_account"]
            if isinstance(creds_info, str):
                creds_info = json.loads(creds_info)
            else:
                creds_info = dict(creds_info)
            credentials = Credentials.from_service_account_info(creds_info, scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ])
            return gspread.authorize(credentials)
        elif os.path.exists("service_account.json"):
            credentials = Credentials.from_service_account_file("service_account.json", scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ])
            return gspread.authorize(credentials)
    except Exception as e:
        st.warning(f"Google Sheets kapcsolódási hiba: {e}")
    return None

def save_data(df):
    # Save locally as cache/backup
    try:
        df.to_csv(DB_FILE, index=False)
    except Exception as e:
        st.error(f"Hiba a helyi adatok mentésekor: {e}")
        
    # Try syncing to Google Sheets
    try:
        client = get_gspread_client()
        if client:
            sheet_name = st.secrets.get("google_sheet_name", "Tabor_Vendeglista")
            sh = client.open(sheet_name)
            worksheet = sh.get_worksheet(0)
            if not worksheet:
                worksheet = sh.add_worksheet(title="Vendégek", rows="100", cols="20")
            df_to_save = df.copy()
            for col in df_to_save.columns:
                df_to_save[col] = df_to_save[col].astype(str).replace({'nan': '', 'None': '', '<NA>': ''})
            data = [df_to_save.columns.values.tolist()] + df_to_save.values.tolist()
            worksheet.clear()
            worksheet.update('A1', data)
            st.session_state['sheets_sync_status'] = f"✅ Google Táblázat ({sheet_name}) szinkronizálva!"
    except Exception as e:
        st.error(f"Google Táblázat mentési hiba: {e}")

def load_data():
    # Try loading from Google Sheets first
    try:
        client = get_gspread_client()
        if client:
            sheet_name = st.secrets.get("google_sheet_name", "Tabor_Vendeglista")
            sh = client.open(sheet_name)
            worksheet = sh.get_worksheet(0)
            if worksheet:
                records = worksheet.get_all_records()
                if records:
                    df = pd.DataFrame(records)
                    # Convert Két család egy szobában
                    if 'Két család egy szobában' in df.columns:
                        df['Két család egy szobában'] = df['Két család egy szobában'].astype(str).str.lower().isin(['true', '1', 'yes', 't', 'y'])
                    # Convert Gyermekmenü
                    if 'Gyermekmenü' in df.columns:
                        df['Gyermekmenü'] = df['Gyermekmenü'].astype(str).str.lower().isin(['true', '1', 'yes', 't', 'y'])
                    # Ensure numerical values
                    if 'Éjszakák Száma' in df.columns:
                        df['Éjszakák Száma'] = pd.to_numeric(df['Éjszakák Száma'], errors='coerce').fillna(5).astype(int)
                    if 'Kedvezmény (%)' in df.columns:
                        df['Kedvezmény (%)'] = pd.to_numeric(df['Kedvezmény (%)'], errors='coerce').fillna(0.0).astype(float)
                    if 'Fizetett előleg' in df.columns:
                        df['Fizetett előleg'] = pd.to_numeric(df['Fizetett előleg'], errors='coerce').fillna(0.0).astype(float)
                    if 'Külsős Ebédek Száma' in df.columns:
                        df['Külsős Ebédek Száma'] = pd.to_numeric(df['Külsős Ebédek Száma'], errors='coerce').fillna(0).astype(int)
                    
                    if 'Szállás' in df.columns:
                        df['Szállás'] = df['Szállás'].replace({
                            "Sátor 1": "Sátor A",
                            "Sátor 2": "Sátor B",
                            "Sátor 3": "Sátor C",
                            "Sátor 4": "Sátor D",
                            "Sátor 5": "Sátor E",
                            "Sátor 6": "Sátor F",
                            "Sátor 7": "Sátor G",
                            "Sátor 8": "Sátor H"
                        })
                    df.to_csv(DB_FILE, index=False) # update local cache
                    return recalculate_dataframe(df)
    except Exception as e:
        st.warning(f"Nem sikerült betölteni a Google Táblázatból ({e}). Helyi adatbázis használata.")

    # Fallback to local file
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if 'Szállás' in df.columns:
                df['Szállás'] = df['Szállás'].replace({
                    "Sátor 1": "Sátor A",
                    "Sátor 2": "Sátor B",
                    "Sátor 3": "Sátor C",
                    "Sátor 4": "Sátor D",
                    "Sátor 5": "Sátor E",
                    "Sátor 6": "Sátor F",
                    "Sátor 7": "Sátor G",
                    "Sátor 8": "Sátor H"
                })
            df['Két család egy szobában'] = df['Két család egy szobában'].fillna(False).astype(bool)
            df['Éjszakák Száma'] = df['Éjszakák Száma'].fillna(5).astype(int)
            df['Fizetett előleg'] = df['Fizetett előleg'].fillna(0.0).astype(float)
            df['Külsős Ebédek Száma'] = df['Külsős Ebédek Száma'].fillna(0).astype(int)
            if 'Gyermekmenü' not in df.columns:
                df['Gyermekmenü'] = False
            df['Gyermekmenü'] = df['Gyermekmenü'].fillna(False).astype(bool)
            if 'Kedvezmény (%)' not in df.columns:
                df['Kedvezmény (%)'] = 0.0
            df['Kedvezmény (%)'] = df['Kedvezmény (%)'].fillna(0.0).astype(float)
            return recalculate_dataframe(df)
        except Exception as e:
            st.error(f"Hiba az adatbázis betöltésekor: {e}. Alaphelyzet betöltése.")
            
    df_init = pd.DataFrame(prepopulated_guests)
    df_init = recalculate_dataframe(df_init)
    save_data(df_init)
    return df_init

# Initialize the guest database in session state if not already set
if 'guests_df' not in st.session_state:
    st.session_state.guests_df = load_data()
if 'active_building' not in st.session_state:
    st.session_state['active_building'] = None
if 'admin_unlocked' not in st.session_state:
    st.session_state['admin_unlocked'] = False


# -----------------------------------------------------------------------------
# 3b. MAP HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def build_building_status(df, accommodations_list):
    """Épület-szintű foglaltsági állapotot épít a DataFrame alapján."""
    cap_lookup = {r['Név']: r['Kapacitás'] for r in accommodations_list}
    status = {}
    for bid, bdata in BUILDING_GROUPS.items():
        rooms = bdata['rooms']
        total_cap = sum(cap_lookup.get(r, 0) for r in rooms)
        building_guests = df[df['Szállás'].isin(rooms)]
        occ = len(building_guests)
        has_pending = bool((building_guests['Státusz'] == 'Függőben').any()) if occ > 0 else False
        if bid == 'K':
            color = 'blue'
            status_text = 'Külsős Vendégek'
        elif occ == 0:
            color = 'green'
            status_text = 'Szabad'
        elif has_pending:
            color = 'yellow'
            status_text = 'Függőben'
        elif occ >= total_cap:
            color = 'red'
            status_text = 'Foglalt'
        else:
            color = 'half'
            status_text = 'Részben foglalt'
        # Room-level details
        room_details = []
        for rn in rooms:
            rc = cap_lookup.get(rn, 0)
            ro = len(df[df['Szállás'] == rn])
            room_details.append({'name': rn, 'capacity': rc, 'occupancy': ro, 'available': rc - ro})
        # Guest list - include DataFrame index and note for editing
        guests = []
        for idx_g, g in building_guests.iterrows():
            note_val = g.get('Megjegyzés', '')
            meals_val = g.get('Étkezések', 'ALL')
            guests.append({
                'idx': int(idx_g),
                'name': g['Név'], 'type': g['Típus'], 'room': g['Szállás'],
                'nights': int(g['Éjszakák Száma']), 'status': g['Státusz'],
                'paid': float(g['Fizetett előleg']), 'cost': float(g['Összköltség']),
                'note': str(note_val) if (note_val is not None and str(note_val) != 'nan') else '',
                'meals': str(meals_val) if (meals_val is not None and str(meals_val) != 'nan') else 'ALL',
                'is_shared': bool(g.get('Két család egy szobában', False))
            })
        status[bid] = {
            'id': bid, 'name': bdata['name'],
            'capacity': total_cap, 'occupancy': occ,
            'color': color, 'status_text': status_text,
            'room_details': room_details, 'guests': guests,
            'x': bdata['x'], 'y': bdata['y'], 'label': str(bdata.get('label', bid))
        }
    return status

@st.dialog("🏡 Épület Foglalások Kezelése", width="large")
def manage_building_bookings(building_id):
    bdata = BUILDING_GROUPS.get(building_id)
    if not bdata:
        st.error("Épület nem található.")
        return
        
    st.markdown(f"## 🏢 {bdata['name']}")
    
    df = st.session_state.guests_df
    rooms = bdata['rooms']
    building_guests = df[df['Szállás'].isin(rooms)]
    
    is_external_group = (building_id == 'K')

    # Initialize session state flags if not present
    if 'booking_edit_mode' not in st.session_state:
        st.session_state['booking_edit_mode'] = False
    if 'edit_guest_idx' not in st.session_state:
        st.session_state['edit_guest_idx'] = None
    if 'preset_room' not in st.session_state:
        st.session_state['preset_room'] = None

    # 1. View Mode (Read-only listing with inline actions next to records)
    if not st.session_state['booking_edit_mode']:
        if is_external_group:
            col_room_title, col_room_add = st.columns([5, 1])
            col_room_title.markdown(f"#### 👥 Külsős Vendégek listája — `{len(building_guests)} regisztrált`")
            if col_room_add.button("➕", key="btn_add_external", help="Új külsős vendég regisztrálása", use_container_width=True):
                st.session_state['booking_edit_mode'] = True
                st.session_state['preset_room'] = 'Külsős'
                st.session_state['edit_guest_idx'] = None
                st.rerun()
                
            if building_guests.empty:
                st.caption("*(Még nincs regisztrált külsős vendég)*")
            else:
                for idx_g, g in building_guests.iterrows():
                    col_g_info, col_g_edit = st.columns([5, 1])
                    
                    paid = g.get('Fizetett előleg', 0.0)
                    total = g.get('Összköltség', 0.0)
                    status_text = "🟢 Véglegesítve" if g['Státusz'] == "Végleges" else "🟡 Függőben"
                    status_color = "#4caf50" if g['Státusz'] == "Végleges" else "#ffb300"
                    
                    menu_badge = ""
                    if g.get('Gyermekmenü', False):
                        menu_badge = '<span style="font-size: 0.75em; background-color: #0288d1; color: #ffffff; padding: 2px 6px; border-radius: 4px; margin-left: 8px; font-weight: bold;">👶 Gyermekmenü</span>'
                    
                    room_val = g.get('Szállás', 'Külsős (Nincs)')
                    label_map = {
                        'Külsős (Nincs)': "🍽️ Csak Étkezés",
                        'Külsős (Sátor)': "⛺ Sátorhely",
                        'Külsős (Lakókocsi)': "🚐 Lakókocsi hely"
                    }
                    acc_label = label_map.get(room_val, room_val)
                    acc_badge = f'<span style="font-size: 0.85em; background-color: #2196f3; color: #ffffff; padding: 2px 6px; border-radius: 4px; margin-left: 8px; font-weight: bold;">{acc_label}</span>'
                    
                    note_html = ""
                    if g.get('Megjegyzés'):
                        note_html = f'<div style="font-size: 0.85em; color: #a5a5a5; margin-top: 6px; font-style: italic;">💬 {g["Megjegyzés"]}</div>'
                        
                    unpaid = max(0.0, total - paid)
                    unpaid_str = f" | Hátralék: <strong style='color: #ff5252;'>{unpaid:.0f} RON</strong>" if unpaid > 0 else " | ✨ Rendezte"
                    
                    meals_val = g.get('Étkezések', 'ALL')
                    meals_html = render_meal_badges(meals_val)
                    
                    guest_html = f"""
                    <div style="background-color: #222530; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; border-left: 4px solid {status_color}; display: flex; flex-direction: column; justify-content: space-between;">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div>
                                <strong style="color: #ffffff; font-size: 1.1em;">{g['Név']}</strong>
                                <span style="font-size: 0.8em; background-color: #3b3f54; color: #d1d5db; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">{g['Típus']}</span>
                                {acc_badge}
                                {menu_badge}
                            </div>
                            <div style="text-align: right; font-size: 0.9em;">
                                <span style="color: {status_color}; font-weight: bold;">{status_text}</span>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; border-top: 1px dashed #2d3142; padding-top: 8px; font-size: 0.9em; color: #a5a5a5;">
                            <div>
                                Befizetett előleg: <strong style="color: #4caf50;">{paid:.0f} RON</strong> / Összesen: <strong style="color: #ffffff;">{total:.0f} RON</strong>{unpaid_str}
                            </div>
                            <div style="font-size: 0.85em; color: #888;">
                                {g.get('Éjszakák Száma', 5)} nap
                            </div>
                        </div>
                        {note_html}
                        <div style="margin-top: 8px; border-top: 1px dashed #2d3142; padding-top: 8px;">
                            <div style="font-size: 0.85em; color: #a5a5a5; font-weight: bold; margin-bottom: 4px;">🍽️ Igényelt étkezések:</div>
                            {meals_html}
                        </div>
                    </div>
                    """
                    
                    clean_html = "\n".join([line.strip() for line in guest_html.split("\n")])
                    col_g_info.markdown(clean_html, unsafe_allow_html=True)
                    
                    if col_g_edit.button("✏️", key=f"btn_edit_{idx_g}", help=f"{g['Név']} foglalásának szerkesztése", use_container_width=True):
                        st.session_state['booking_edit_mode'] = True
                        st.session_state['edit_guest_idx'] = idx_g
                        st.session_state['preset_room'] = None
                        st.rerun()
            st.markdown("---")
        else:
            st.subheader("📋 Jelenlegi szobabeosztás")
            cap_lookup = {r['Név']: r['Kapacitás'] for r in accommodations}
            for room in rooms:
                room_guests = building_guests[building_guests['Szállás'] == room]
                occ = len(room_guests)
                cap = cap_lookup.get(room, 4)
                col_room_title, col_room_add = st.columns([5, 1])
                badge_color = "🟢" if occ < cap else "🔴"
                col_room_title.markdown(f"#### 🚪 Szoba: **{room}** — {badge_color} `{occ}/{cap} fő`")
                if col_room_add.button("➕", key=f"btn_add_{room}", help=f"Új vendég hozzáadása a(z) {room} szobába", use_container_width=True):
                    st.session_state['booking_edit_mode'] = True
                    st.session_state['preset_room'] = room
                    st.session_state['edit_guest_idx'] = None
                    st.rerun()
            
            if room_guests.empty:
                st.caption("*(Ebben a szobában még nincs foglalás)*")
            else:
                for idx_g, g in room_guests.iterrows():
                    col_g_info, col_g_edit = st.columns([5, 1])
                    
                    paid = g.get('Fizetett előleg', 0.0)
                    total = g.get('Összköltség', 0.0)
                    status_text = "🟢 Véglegesítve" if g['Státusz'] == "Végleges" else "🟡 Függőben"
                    status_color = "#4caf50" if g['Státusz'] == "Végleges" else "#ffb300"
                    
                    menu_badge = ""
                    if g.get('Gyermekmenü', False):
                        menu_badge = '<span style="font-size: 0.75em; background-color: #0288d1; color: #ffffff; padding: 2px 6px; border-radius: 4px; margin-left: 8px; font-weight: bold;">👶 Gyermekmenü</span>'
                    
                    note_html = ""
                    if g.get('Megjegyzés'):
                        note_html = f'<div style="font-size: 0.85em; color: #a5a5a5; margin-top: 6px; font-style: italic;">💬 {g["Megjegyzés"]}</div>'
                        
                    # Calculate unpaid
                    unpaid = max(0.0, total - paid)
                    unpaid_str = f" | Hátralék: <strong style='color: #ff5252;'>{unpaid:.0f} RON</strong>" if unpaid > 0 else " | ✨ Rendezte"
                    
                    meals_val = g.get('Étkezések', 'ALL')
                    meals_html = render_meal_badges(meals_val)
                    
                    guest_html = f"""
                    <div style="background-color: #222530; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; border-left: 4px solid {status_color}; display: flex; flex-direction: column; justify-content: space-between;">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div>
                                <strong style="color: #ffffff; font-size: 1.1em;">{g['Név']}</strong>
                                <span style="font-size: 0.8em; background-color: #3b3f54; color: #d1d5db; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">{g['Típus']}</span>
                                {menu_badge}
                            </div>
                            <div style="text-align: right; font-size: 0.9em;">
                                <span style="color: {status_color}; font-weight: bold;">{status_text}</span>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; border-top: 1px dashed #2d3142; padding-top: 8px; font-size: 0.9em; color: #a5a5a5;">
                            <div>
                                Befizetett előleg: <strong style="color: #4caf50;">{paid:.0f} RON</strong> / Összesen: <strong style="color: #ffffff;">{total:.0f} RON</strong>{unpaid_str}
                            </div>
                            <div style="font-size: 0.85em; color: #888;">
                                {g.get('Éjszakák Száma', 5)} éjszaka
                            </div>
                        </div>
                        {note_html}
                        <div style="margin-top: 8px; border-top: 1px dashed #2d3142; padding-top: 8px;">
                            <div style="font-size: 0.85em; color: #a5a5a5; font-weight: bold; margin-bottom: 4px;">🍽️ Igényelt étkezések:</div>
                            {meals_html}
                        </div>
                    </div>
                    """
                    
                    # Clean whitespaces for rendering
                    clean_html = "\n".join([line.strip() for line in guest_html.split("\n")])
                    col_g_info.markdown(clean_html, unsafe_allow_html=True)
                    
                    # Inline Edit Guest (✏️) button next to the guest card
                    if col_g_edit.button("✏️", key=f"btn_edit_{idx_g}", help=f"{g['Név']} foglalásának szerkesztése", use_container_width=True):
                        st.session_state['booking_edit_mode'] = True
                        st.session_state['edit_guest_idx'] = idx_g
                        st.session_state['preset_room'] = None
                        st.rerun()
            st.markdown("---")
            
        if st.button("Bezárás", use_container_width=True):
            st.session_state["active_building"] = None
            st.rerun()
        return

    # 2. Edit Mode
    # Scenario A: Editing a single selected guest
    if st.session_state.get('edit_guest_idx') is not None:
        idx = st.session_state['edit_guest_idx']
        if idx in df.index:
            g = df.loc[idx]
            st.subheader(f"✏️ Foglalás szerkesztése: {g['Név']}")
            
            with st.container(border=True):
                col1, col2, col3, col3b = st.columns([2.5, 1.5, 1.5, 1.2])
                g_name = col1.text_input("Név", value=g['Név'])
                cat_opts = ["Felnőtt", "Fiatal/Diák", "Gyerek", "Kisgyerek", "Külsős"]
                g_type = col2.selectbox(
                    "Kategória", 
                    cat_opts, 
                    index=cat_opts.index(g['Típus']) if g['Típus'] in cat_opts else 0
                )
                if is_external_group:
                    ext_types = {
                        "Külsős (Nincs)": "Csak étkezés",
                        "Külsős (Sátor)": "Sátorhely (80 RON/nap)",
                        "Külsős (Lakókocsi)": "Lakókocsi hely (100 RON/nap)"
                    }
                    selected_ext_label = col3.selectbox(
                        "Külsős Szállás",
                        options=list(ext_types.values()),
                        index=list(ext_types.keys()).index(g['Szállás']) if g['Szállás'] in ext_types else 0
                    )
                    reverse_ext_types = {v: k for k, v in ext_types.items()}
                    g_room = reverse_ext_types[selected_ext_label]
                else:
                    g_room = col3.selectbox("Szoba", rooms, index=rooms.index(g['Szállás']) if g['Szállás'] in rooms else 0)
                g_child_menu = col3b.checkbox("Gyermekmenü?", value=bool(g.get('Gyermekmenü', False)))
                
                col4, col5, col5b, col6 = st.columns([1, 1, 1, 1])
                g_nights = col4.slider("Éjszakák", min_value=1, max_value=5, value=int(g['Éjszakák Száma']))
                g_paid = col5.number_input("Befizetett előleg (RON)", min_value=0.0, value=float(g['Fizetett előleg']), step=50.0)
                g_discount = col5b.number_input("Kedvezmény (%)", min_value=0.0, max_value=100.0, value=float(g.get('Kedvezmény (%)', 0.0)), step=5.0)
                g_status_bool = col6.checkbox("Véglegesített?", value=(g['Státusz'] == "Végleges"))
                g_status = "Végleges" if g_status_bool else "Függőben"
                
                g_note = st.text_input("Megjegyzés", value=g.get('Megjegyzés', ''))
                
                st.markdown("##### 🍽️ Igényelt étkezések:")
                m_cols = st.columns(6)
                
                cur_meals = str(g.get('Étkezések', 'ALL'))
                if cur_meals == 'ALL':
                    active_set = {'T_D', 'W_BD', 'W_L', 'Th_BD', 'Th_L', 'F_BD', 'F_L', 'S_BD', 'S_L', 'Su_BD', 'Su_L'}
                else:
                    active_set = {m.strip() for m in cur_meals.split(',') if m.strip()}
                    
                selected_meals = []
                
                # Tuesday
                with m_cols[0]:
                    st.markdown("🔴 **Kedd**")
                    t_d = st.checkbox("🌆 Vacsora", value=('T_D' in active_set), key="chk_td")
                    if t_d: selected_meals.append('T_D')
                    
                # Wednesday
                with m_cols[1]:
                    st.markdown("🟡 **Szerda**")
                    w_bd = st.checkbox("🥣 Regg+Vac", value=('W_BD' in active_set), key="chk_wbd")
                    w_l = st.checkbox("🍲 Ebéd", value=('W_L' in active_set), key="chk_wl")
                    if w_bd: selected_meals.append('W_BD')
                    if w_l: selected_meals.append('W_L')
                    
                # Thursday
                with m_cols[2]:
                    st.markdown("🟢 **Csütörtök**")
                    th_bd = st.checkbox("🥣 Regg+Vac", value=('Th_BD' in active_set), key="chk_thbd")
                    th_l = st.checkbox("🍲 Ebéd", value=('Th_L' in active_set), key="chk_thl")
                    if th_bd: selected_meals.append('Th_BD')
                    if th_l: selected_meals.append('Th_L')
                    
                # Friday
                with m_cols[3]:
                    st.markdown("🔵 **Péntek**")
                    f_bd = st.checkbox("🥣 Regg+Vac", value=('F_BD' in active_set), key="chk_fbd")
                    f_l = st.checkbox("🍲 Ebéd", value=('F_L' in active_set), key="chk_fl")
                    if f_bd: selected_meals.append('F_BD')
                    if f_l: selected_meals.append('F_L')
                    
                # Saturday
                with m_cols[4]:
                    st.markdown("🟣 **Szombat**")
                    s_bd = st.checkbox("🥣 Regg+Vac", value=('S_BD' in active_set), key="chk_sbd")
                    s_l = st.checkbox("🍲 Ebéd", value=('S_L' in active_set), key="chk_sl")
                    if s_bd: selected_meals.append('S_BD')
                    if s_l: selected_meals.append('S_L')
                    
                # Sunday
                with m_cols[5]:
                    st.markdown("🟤 **Vasárnap**")
                    su_bd = st.checkbox("🥣 Reggeli", value=('Su_BD' in active_set), key="chk_subd")
                    su_l = st.checkbox("🍲 Ebéd", value=('Su_L' in active_set), key="chk_sul")
                    if su_bd: selected_meals.append('Su_BD')
                    if su_l: selected_meals.append('Su_L')
                    
                g_meals = ",".join(selected_meals)
                
                # Active visual price calculation
                temp_row = {
                    'Típus': g_type,
                    'Szállás': g_room,
                    'Két család egy szobában': bool(g.get('Két család egy szobában', False)),
                    'Éjszakák Száma': g_nights
                }
                acc_cost = calculate_accommodation_cost(temp_row)
                meal_cost = calculate_meals_cost(g_meals, g_type, g_child_menu)
                
                subtotal = acc_cost + meal_cost
                discount_val = subtotal * (g_discount / 100.0)
                total_cost = subtotal - discount_val
                st.markdown(f"✨ **Kalkulált részösszeg:** Szállás: {acc_cost:.0f} RON + Kaja: {meal_cost:.0f} RON = {subtotal:.0f} RON")
                if g_discount > 0:
                    st.markdown(f"🎁 **Kedvezmény ({g_discount:.0f}%):** -{discount_val:.0f} RON | **Fizetendő végösszeg: {total_cost:.0f} RON**")
                else:
                    st.markdown(f"**Fizetendő végösszeg: {total_cost:.0f} RON**")
                
                # Delete Confirmation Flow
                if st.session_state.get('confirm_delete_idx') == idx:
                    st.warning("⚠️ **Biztosan véglegesen törölni szeretnéd ezt a foglalást?**")
                    col_yes, col_no = st.columns(2)
                    if col_yes.button("🗑️ Igen, Törlés", type="primary", key="del_yes_s1", use_container_width=True):
                        df = df.drop(idx)
                        st.session_state.guests_df = recalculate_dataframe(df)
                        save_data(st.session_state.guests_df)
                        st.session_state['edit_guest_idx'] = None
                        st.session_state['booking_edit_mode'] = False
                        st.session_state['confirm_delete_idx'] = None
                        st.rerun()
                    if col_no.button("Mégse", key="del_no_s1", use_container_width=True):
                        st.session_state['confirm_delete_idx'] = None
                        st.rerun()
                else:
                    if st.button("🗑️ Foglalás Törlése", type="secondary", use_container_width=True):
                        st.session_state['confirm_delete_idx'] = idx
                        st.rerun()

            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.button("💾 Mentés", type="primary", use_container_width=True):
                df.loc[idx, 'Név'] = g_name
                df.loc[idx, 'Típus'] = g_type
                df.loc[idx, 'Szállás'] = g_room
                df.loc[idx, 'Éjszakák Száma'] = g_nights
                df.loc[idx, 'Gyermekmenü'] = g_child_menu
                df.loc[idx, 'Kedvezmény (%)'] = g_discount
                df.loc[idx, 'Fizetett előleg'] = g_paid
                df.loc[idx, 'Státusz'] = g_status
                df.loc[idx, 'Megjegyzés'] = g_note
                df.loc[idx, 'Étkezések'] = g_meals
                
                st.session_state.guests_df = recalculate_dataframe(df)
                save_data(st.session_state.guests_df)
                st.session_state['edit_guest_idx'] = None
                st.session_state['booking_edit_mode'] = False
                st.rerun()
                
            if col_btn2.button("Bezárás mentés nélkül", use_container_width=True):
                st.session_state['edit_guest_idx'] = None
                st.session_state['booking_edit_mode'] = False
                st.rerun()
        return

    # Scenario B: Registering a new guest directly to a preset room
    if st.session_state.get('preset_room') is not None:
        preset_room = st.session_state['preset_room']
        st.subheader(f"➕ Új foglalás: {preset_room}")
        
        with st.container(border=True):
            col_n1, col_n2, col_n3, col_n3b = st.columns([2.5, 1.5, 1.5, 1.2])
            new_name = col_n1.text_input("Új vendég neve:", key="new_g_name", placeholder="Pl. Szabó Család")
            new_cat_opts = ["Felnőtt", "Fiatal/Diák", "Gyerek", "Kisgyerek", "Külsős"]
            new_type = col_n2.selectbox(
                "Kategória:", 
                new_cat_opts, 
                index=4 if is_external_group else 0,
                key="new_g_type"
            )
            
            if preset_room == 'Külsős':
                ext_types = {
                    "Külsős (Nincs)": "Csak étkezés",
                    "Külsős (Sátor)": "Sátorhely (80 RON/nap)",
                    "Külsős (Lakókocsi)": "Lakókocsi hely (100 RON/nap)"
                }
                selected_ext_label = col_n3.selectbox(
                    "Külsős Szállás",
                    options=list(ext_types.values()),
                    key="new_g_ext_room"
                )
                reverse_ext_types = {v: k for k, v in ext_types.items()}
                new_room = reverse_ext_types[selected_ext_label]
            else:
                avail_rooms = [r for r in rooms if r == preset_room]
                new_room = col_n3.selectbox("Szoba választás:", avail_rooms, key="new_g_room")
            new_child_menu = col_n3b.checkbox("Gyermekmenü?", value=False, key="new_g_child_menu")
                
            col_n4, col_n5, col_n5b, col_n6 = st.columns([1, 1, 1, 1])
            new_nights = col_n4.slider("Éjszakák száma:", min_value=1, max_value=5, value=5, key="new_g_nights")
            new_paid = col_n5.number_input("Előleg (RON):", min_value=0.0, value=0.0, step=50.0, key="new_g_paid")
            new_discount = col_n5b.number_input("Kedvezmény (%)", min_value=0.0, max_value=100.0, value=0.0, step=5.0, key="new_g_discount")
            new_status_bool = col_n6.checkbox("Véglegesített foglalás?", value=True, key="new_g_status")
            new_status = "Végleges" if new_status_bool else "Függőben"
            new_note = st.text_input("Megjegyzés:", key="new_g_note", placeholder="Pl. Ételallergia...")
            
            st.markdown("##### 🍽️ Igényelt étkezések (új vendég):")
            m_cols_new = st.columns(6)
            new_selected_meals = []
            
            # Tuesday
            with m_cols_new[0]:
                st.markdown("🔴 **Kedd**")
                new_t_d = st.checkbox("🌆 Vacsora", value=True, key="new_chk_td")
                if new_t_d: new_selected_meals.append('T_D')
                
            # Wednesday
            with m_cols_new[1]:
                st.markdown("🟡 **Szerda**")
                new_w_bd = st.checkbox("🥣 Regg+Vac", value=True, key="new_chk_wbd")
                new_w_l = st.checkbox("🍲 Ebéd", value=True, key="new_chk_wl")
                if new_w_bd: new_selected_meals.append('W_BD')
                if new_w_l: new_selected_meals.append('W_L')
                
            # Thursday
            with m_cols_new[2]:
                st.markdown("🟢 **Csütörtök**")
                new_th_bd = st.checkbox("🥣 Regg+Vac", value=True, key="new_chk_thbd")
                new_th_l = st.checkbox("🍲 Ebéd", value=True, key="new_chk_thl")
                if new_th_bd: new_selected_meals.append('Th_BD')
                if new_th_l: new_selected_meals.append('Th_L')
                
            # Friday
            with m_cols_new[3]:
                st.markdown("🔵 **Péntek**")
                new_f_bd = st.checkbox("🥣 Regg+Vac", value=True, key="new_chk_fbd")
                new_f_l = st.checkbox("🍲 Ebéd", value=True, key="new_chk_fl")
                if new_f_bd: new_selected_meals.append('F_BD')
                if new_f_l: new_selected_meals.append('F_L')
                
            # Saturday
            with m_cols_new[4]:
                st.markdown("🟣 **Szombat**")
                new_s_bd = st.checkbox("🥣 Regg+Vac", value=True, key="new_chk_sbd")
                new_s_l = st.checkbox("🍲 Ebéd", value=True, key="new_chk_sl")
                if new_s_bd: new_selected_meals.append('S_BD')
                if new_s_l: new_selected_meals.append('S_L')
                
            # Sunday
            with m_cols_new[5]:
                st.markdown("🟤 **Vasárnap**")
                new_su_bd = st.checkbox("🥣 Reggeli", value=True, key="new_chk_subd")
                new_su_l = st.checkbox("🍲 Ebéd", value=True, key="new_chk_sul")
                if new_su_bd: new_selected_meals.append('Su_BD')
                if new_su_l: new_selected_meals.append('Su_L')
                
            new_meals = ",".join(new_selected_meals)
            
            # New guest price calculation
            if new_name.strip():
                temp_row = {
                    'Típus': new_type,
                    'Szállás': new_room,
                    'Két család egy szobában': False,
                    'Éjszakák Száma': new_nights
                }
                new_acc_cost = calculate_accommodation_cost(temp_row)
                new_meal_cost = calculate_meals_cost(new_meals, new_type, new_child_menu)
                
                new_subtotal = new_acc_cost + new_meal_cost
                new_discount_val = new_subtotal * (new_discount / 100.0)
                new_total_cost = new_subtotal - new_discount_val
                st.markdown(f"✨ **Új vendég kalkulált részösszege:** Szállás: {new_acc_cost:.0f} RON + Kaja: {new_meal_cost:.0f} RON = {new_subtotal:.0f} RON")
                if new_discount > 0:
                    st.markdown(f"🎁 **Kedvezmény ({new_discount:.0f}%):** -{new_discount_val:.0f} RON | **Végleges fizetendő: {new_total_cost:.0f} RON**")
                else:
                    st.markdown(f"**Végleges fizetendő: {new_total_cost:.0f} RON**")
            
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("💾 Foglalás Mentése", type="primary", use_container_width=True):
            if new_name.strip():
                new_row = {
                    'Név': new_name.strip(),
                    'Típus': new_type,
                    'Szállás': new_room,
                    'Éjszakák Száma': new_nights,
                    'Két család egy szobában': False,
                    'Gyermekmenü': new_child_menu,
                    'Kedvezmény (%)': new_discount,
                    'Fizetett előleg': new_paid,
                    'Státusz': new_status,
                    'Külsős Ebédek Száma': 0,
                    'Megjegyzés': new_note,
                    'Étkezések': new_meals
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.guests_df = recalculate_dataframe(df)
                save_data(st.session_state.guests_df)
                st.session_state['preset_room'] = None
                st.session_state['booking_edit_mode'] = False
                st.rerun()
                
        if col_btn2.button("Bezárás mentés nélkül", use_container_width=True):
            st.session_state['preset_room'] = None
            st.session_state['booking_edit_mode'] = False
            st.rerun()
        return

    # Default fallback
    st.session_state['booking_edit_mode'] = False
    st.rerun()

# -----------------------------------------------------------------------------
# 5. FINANCIAL CALCULATIONS & SERVICE PROVIDER PAYOUT ENGINE
# -----------------------------------------------------------------------------
df = st.session_state.guests_df

# Expected Income
total_income = df['Összköltség'].sum()

# Collected deposits
total_collected = df['Fizetett előleg'].sum()

# Bedő Laci Payouts
fixed_rent_laci = 12500.0 * 5.0 # 62500 RON
prepaid_deduction_laci = 20000.0
total_bedo_food_cost = df['Bedő Laci Kaja'].sum()
gross_payout_laci = fixed_rent_laci + total_bedo_food_cost
net_payout_laci = gross_payout_laci - prepaid_deduction_laci

# Tribel Payouts
total_tribel_lunch_cost = df['Tribel Ebéd'].sum()

# Net Profit (Income minus all provider gross fees)
net_profit = total_income - (gross_payout_laci + total_tribel_lunch_cost)


# -----------------------------------------------------------------------------
# 6. MAIN PANEL - DASHBOARD
# -----------------------------------------------------------------------------
st.title("⛺ Nyári Tábor Kezelő Szoftver - 2026")
st.markdown("---")

# 4 KPI Cards at the top
registered_guests = len(df[df['Típus'] != 'Külsős'])

kpi_html = f"""
<div class="kpi-container">
    <!-- Card 1 -->
    <div class="kpi-card" style="background: linear-gradient(135deg, #1d976c 0%, #93f9b9 100%);">
        <div class="kpi-title">Regisztrált Vendégek</div>
        <div class="kpi-value">{registered_guests} / {max_capacity}</div>
        <div class="kpi-sub">Szálláshely kihasználtság</div>
    </div>
    <!-- Card 2 -->
    <div class="kpi-card" style="background: linear-gradient(135deg, #3a7bd5 0%, #3a6073 100%);">
        <div class="kpi-title">Várható Tábori Bevétel</div>
        <div class="kpi-value">{total_income:,.0f} RON</div>
        <div class="kpi-sub">Összesített tábori részvételi díjak</div>
    </div>
    <!-- Card 3 -->
    <div class="kpi-card" style="background: linear-gradient(135deg, #f12711 0%, #f5af19 100%);">
        <div class="kpi-title">Befizetett Előlegek</div>
        <div class="kpi-value">{total_collected:,.0f} RON</div>
        <div class="kpi-sub">Begyűjtött előlegek / összegek</div>
    </div>
    <!-- Card 4 -->
    <div class="kpi-card" style="background: linear-gradient(135deg, #8a2387 0%, #e94057 50%, #f27121 100%);">
        <div class="kpi-title">Nettó Tábori Profit</div>
        <div class="kpi-value">{net_profit:,.0f} RON</div>
        <div class="kpi-sub">Bevétel - Kiadások (Bedő Laci + Tribel)</div>
    </div>
</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)


# Warnings Section
has_pending_short = df[(df['Státusz'] == 'Függőben') & (df['Éjszakák Száma'] < 5) & (df['Típus'] != 'Külsős')]
if not has_pending_short.empty:
    st.warning("⚠️ **Figyelem:** Van olyan vendég, aki **csak pár napra** (kevesebb mint 5 éjszaka) jelentkezett! Státuszuk kötelezően **Függőben** marad. *Csak akkor véglegesíthető, ha marad hely a táborban!*")

has_missing_deposit = df[df['Előleg Státusz'].str.contains("⚠️", na=False)]
if not has_missing_deposit.empty:
    st.warning(f"⚠️ **Figyelem:** {len(has_missing_deposit)} vendégnél a befizetett előleg **kevesebb mint a részvételi díj 20%-a**!")

# Google Sheets Connection Status Info
g_client = get_gspread_client()
if g_client:
    sheet_name = st.secrets.get("google_sheet_name", "Tabor_Vendeglista")
    st.info(f"🟢 **Google Táblázat szinkronizáció aktív:** `{sheet_name}`")
else:
    with st.expander("📊 Google Táblázat összekötés (Biztonsági mentés)"):
        st.markdown("""
        Az adatok biztonsága érdekében összekötheted a programot egy Google Táblázattal (Google Sheets). 
        Így minden mentés azonnal szinkronizálódik a felhőbe.
        
        **Lépések az összekötéshez:**
        1. Hozz létre egy Google Táblázatot pl. `Tabor_Vendeglista` néven.
        2. Hozz létre egy Google Cloud Service Account-ot (a Google Drive & Sheets API-k legyenek engedélyezve), és töltsd le a hozzáférési kulcsot JSON formátumban.
        3. Oszd meg a Google Táblázatodat a Service Account email címével (szerkesztési joggal).
        4. Helyezd el a letöltött JSON kulcs tartalmát a Streamlit Cloud **Secrets** beállításaiba `gcp_service_account` név alatt (vagy mentsd le helyileg `service_account.json` néven a program mellé).
        """)
# Open dialog globally if there's an active building selected
if st.session_state.get("active_building") is not None:
    manage_building_bookings(st.session_state["active_building"])

# Tabs for different views
tab_map, tab_rooms, tab_guests, tab_financials, tab_meals = st.tabs([
    "🗺️ Interaktív Térkép",
    "🏡 Szállásosztó & Szobák",
    "👥 Vendég Nyilvántartás",
    "📊 Admin 1",
    "🍽️ Admin 2"
])

# -----------------------------------------------------------------------------
# TAB 0: INTERACTIVE SATELLITE MAP
# -----------------------------------------------------------------------------
with tab_map:
    st.header("🗺️ Interaktív Tábortérkép")
    st.markdown("Kattints egy **épületre vagy sátorra** a részletek megtekintéséhez, illetve új foglalás bejegyzéséhez.")
    
    # Show success/error from query_params booking
    if st.session_state.get('map_success_msg'):
        st.success(st.session_state.pop('map_success_msg'))
    if st.session_state.get('map_error_msg'):
        st.error(st.session_state.pop('map_error_msg'))

    # Color legend
    leg1, leg2, leg3, leg4, leg5 = st.columns(5)
    leg1.markdown("🟢 **Szabad**")
    leg2.markdown("🟢🔴 **Részben**")
    leg3.markdown("🔴 **Foglalt**")
    leg4.markdown("🟡 **Függőben**")
    leg5.markdown("_(Kattints a körre!)_")

    if os.path.exists("tabor_muhold.jpg"):


        # Edit-mode toggle
        _edit_mode = st.toggle(
            "🔧 Jelölők pozíciójának szerkesztése",
            value=False,
            key="map_edit_toggle_drag",
            help="Bekapcsolva a köröket egérrel lehet húzni a helyes épületre. Mentés után a pozíciók véglegesen tárolódnak."
        )
        if _edit_mode:
            st.info("✋ **Szerkesztési mód aktív.** Húzd a jelölőket a térképen a helyükre, majd a térkép alatti Mentés gombbal mentsd!")
            

        # Resolve base URL dynamically for link routing in iframe map
        _base_url = 'https://fuzitabor.streamlit.app'
        try:
            addr = st.get_option('browser.serverAddress')
            if addr in ['localhost', '127.0.0.1'] or 'localhost' in str(addr):
                _server_port = int(st.get_option('server.port') or 8501)
                _base_url = f'http://localhost:{_server_port}'
        except Exception:
            pass

        # Load and encode image
        with open("tabor_muhold.jpg", "rb") as _f:
            _img_b64 = base64.b64encode(_f.read()).decode()

        # Build building-level status
        _bstatus = build_building_status(st.session_state.guests_df, accommodations)

        # Use custom map component
        if map_component:
            map_result = map_component(img_b64=_img_b64, status=_bstatus, edit_mode=_edit_mode, key="tabor_map_widget")
            if map_result:
                if map_result.get("action") == "click":
                    click_ts = map_result.get("ts")
                    if st.session_state.get("last_map_click_ts") != click_ts:
                        st.session_state["last_map_click_ts"] = click_ts
                        st.session_state["active_building"] = map_result.get("bid")
                        st.session_state['booking_edit_mode'] = False
                        st.session_state['edit_guest_idx'] = None
                        st.session_state['preset_room'] = None
                        st.rerun()
                elif map_result.get("action") == "save_positions":
                    save_ts = map_result.get("ts", 0)
                    if st.session_state.get("last_map_save_ts") != save_ts:
                        st.session_state["last_map_save_ts"] = save_ts
                        new_positions = map_result.get("positions")
                        if new_positions:
                            import json
                            for bid, bdata in new_positions.items():
                                if bid in BUILDING_GROUPS:
                                    BUILDING_GROUPS[bid]['x'] = float(bdata['x'])
                                    BUILDING_GROUPS[bid]['y'] = float(bdata['y'])
                            with open(_POS_FILE, 'w', encoding='utf-8') as _pf:
                                json.dump({b: {'x': v['x'], 'y': v['y']} for b, v in BUILDING_GROUPS.items()}, _pf, ensure_ascii=False, indent=2)
                            st.session_state['map_success_msg'] = "✅ Pozíciók sikeresen mentve!"
                            st.session_state['map_edit_toggle_drag'] = False
                            st.rerun()

        if not _edit_mode:
            st.caption("💡 Kattints egy jelölőre a részletek megtekintéséhez, vagy új foglalás bejegyzéséhez.")
    else:
        st.warning("A műholdfelvétel képfájl (`tabor_muhold.jpg`) nem található. Helyezd az `app.py` mellé!")

# -----------------------------------------------------------------------------
# TAB 1: VISUAL ROOM ALLOCATOR
# -----------------------------------------------------------------------------
with tab_rooms:
    st.header("🏡 Interaktív Szálláshely Térkép")
    st.markdown("A szobák és sátrak foglaltságának vizuális áttekintése. A kártyák színei a telítettséget jelzik.")
    
    # Tábor Műholdfelvétel megjelenítése
    with st.expander("🗺️ Tábor Műholdfelvétel / Helyszín Térkép"):
        if os.path.exists("tabor_muhold.jpg"):
            st.image("tabor_muhold.jpg", caption="A tábor műholdas felülnézete (Google Maps)", use_container_width=True)
        else:
            st.warning("A műholdfelvétel képfájl ('tabor_muhold.jpg') nem található a rendszerben.")
    
    # Recalculate room occupancy
    current_occupancy = {}
    room_guests_list = {}
    room_has_pending = {}
    
    for r in accommodations:
        current_occupancy[r['Név']] = 0
        room_guests_list[r['Név']] = []
        room_has_pending[r['Név']] = False
        
    for idx, row in df.iterrows():
        room_name = row['Szállás']
        if room_name in current_occupancy:
            current_occupancy[room_name] += 1
            # Format display string for guest inside the card
            guest_info = f"{row['Név']} ({row['Típus']})"
            if row['Státusz'] == 'Függőben' or row['Éjszakák Száma'] < 5:
                guest_info += " ⏳"
                room_has_pending[room_name] = True
            room_guests_list[room_name].append(guest_info)
            
    # Group rooms by types for display in sections
    room_types = {
        "Kétszobás Házak (2-Room Houses - 4 fő/szoba)": "Kétszobás Ház",
        "Nagyház Rubin (4 fő/szoba - Szatmáriak előnyben)": "Nagyház Rubin",
        "VIP Ház (Emelet & Földszint - 2 fő/szoba)": "VIP Ház",
        "Különálló Házak (Béla Ház & Attila Ház)": "Ház",
        "Sátrak (Tents - Fiatalok & Diákok)": "Sátor"
    }
    
    for section_title, type_key in room_types.items():
        st.subheader(section_title)
        
        # Display specific notes for Rubin or Tents
        if type_key == "Nagyház Rubin":
            st.markdown('<div class="ui-note">💡 <strong>Megjegyzés:</strong> Rubin házak szobái elsősorban a szatmáriak elhelyezésére szolgálnak.</div>', unsafe_allow_html=True)
        elif type_key == "Sátor":
            st.markdown('<div class="ui-note">💡 <strong>Megjegyzés:</strong> A sátrakba javasolt a fiatalok és diákok elhelyezése a kedvezményes árért.</div>', unsafe_allow_html=True)
        elif type_key == "Ház":
            st.info("Béla Ház: Max 6 fő (földszinti kanapé, emeleti franciaágy). | Attila Ház: Max 8 fő (előfoglalt Ruzsáék).")
            
        # Filter accommodations for this section
        if type_key == "VIP Ház":
            section_rooms = [r for r in accommodations if "VIP" in r['Típus']]
        elif type_key == "Ház":
            section_rooms = [r for r in accommodations if r['Típus'] in ["Béla Ház", "Attila Ház"]]
        else:
            section_rooms = [r for r in accommodations if r['Típus'] == type_key]
            
        # Grid layout using streamlit columns
        cols = st.columns(4)
        for i, room in enumerate(section_rooms):
            col = cols[i % 4]
            name = room['Név']
            occ = current_occupancy[name]
            cap = room['Kapacitás']
            note = room['Megjegyzés']
            
            # Color code logic
            if occ == 0:
                # Green theme for completely empty (free)
                bg = "#e8f5e9"
                text_col = "#2e7d32"
                border_col = "#a5d6a7"
                border_style = f"2px solid {border_col}"
            elif room_has_pending[name]:
                # Yellow theme for temporary status
                bg = "#fff8e1"
                text_col = "#e65100"
                border_col = "#ffe082"
                border_style = f"2px dashed #ff9800"
            elif occ >= cap:
                # Red theme for fully occupied (booked)
                bg = "#ffebee"
                text_col = "#c62828"
                border_col = "#ffcdd2"
                border_style = f"2px solid {border_col}"
            else:
                # Split theme (gradient) for partially occupied (has free spots left)
                bg = "linear-gradient(135deg, #e8f5e9 50%, #ffebee 50%)"
                text_col = "#212121"
                border_col = "#b0bec5"
                border_style = f"2px solid {border_col}"
            
            # Guest list formatted
            guests_html = "<br>".join(room_guests_list[name]) if room_guests_list[name] else "Nincs vendég elhelyezve"
            
            # Pending badge
            badge_html = ""
            if room_has_pending[name]:
                badge_html = '<span class="badge badge-pending">⏳ FÜGGŐBEN</span>'
            elif occ == 0:
                badge_html = '<span class="badge badge-final" style="background-color: #2e7d32; color: #ffffff;">🟢 SZABAD</span>'
            elif occ >= cap:
                badge_html = '<span class="badge badge-final" style="background-color: #c62828; color: #ffffff;">🔴 TELI</span>'
            else:
                badge_html = '<span class="badge badge-final" style="background: linear-gradient(90deg, #2e7d32 50%, #c62828 50%); color: #ffffff; width: auto; font-size: 9px; padding: 3px 6px;">🌗 RÉSZBEN FOGLALT</span>'
                
            col.markdown(f"""<div class="room-card" style="background: {bg}; color: {text_col}; border: {border_style};">
<div class="room-title">{name}</div>
<div class="room-type">{room['Típus']}</div>
<div class="room-occ">Férőhely: {occ} / {cap} fő</div>
{badge_html}
<div class="room-guests">
<strong>Lakosok:</strong><br>
{guests_html}
</div>
</div>""", unsafe_allow_html=True)
            if occ > 0:
                btn_col1, btn_col2, btn_col3 = col.columns(3)
                if btn_col1.button("✏️", key=f"edit_btn_{name}", help=f"Szállás és lakók adatainak szerkesztése", use_container_width=True):
                    b_id = None
                    for bid, bdata in BUILDING_GROUPS.items():
                        if name in bdata['rooms']:
                            b_id = bid
                            break
                    if b_id:
                        st.session_state["active_building"] = b_id
                        st.session_state['booking_edit_mode'] = False
                        st.session_state['edit_guest_idx'] = None
                        st.session_state['preset_room'] = None
                        st.rerun()
                if btn_col2.button("➕", key=f"add_btn_occ_{name}", help=f"Új vendég hozzáadása a(z) {name} szobába", use_container_width=True):
                    b_id = None
                    for bid, bdata in BUILDING_GROUPS.items():
                        if name in bdata['rooms']:
                            b_id = bid
                            break
                    if b_id:
                        st.session_state["active_building"] = b_id
                        st.session_state['booking_edit_mode'] = True
                        st.session_state['preset_room'] = name
                        st.session_state['edit_guest_idx'] = None
                        st.rerun()
                if btn_col3.button("🗑️", key=f"reset_{name}", help=f"Foglalás törlése és előleg kivétele a(z) {name} szálláshelyről", use_container_width=True):
                    st.session_state.guests_df = st.session_state.guests_df[st.session_state.guests_df['Szállás'] != name]
                    st.session_state.guests_df = recalculate_dataframe(st.session_state.guests_df)
                    save_data(st.session_state.guests_df)
                    st.rerun()
            else:
                if col.button("➕", key=f"add_btn_empty_{name}", use_container_width=True, help=f"Új foglalás indítása a(z) {name} szobába"):
                    b_id = None
                    for bid, bdata in BUILDING_GROUPS.items():
                        if name in bdata['rooms']:
                            b_id = bid
                            break
                    if b_id:
                        st.session_state["active_building"] = b_id
                        st.session_state['booking_edit_mode'] = True
                        st.session_state['preset_room'] = name
                        st.session_state['edit_guest_idx'] = None
                        st.rerun()
            
    # Show list of External Guests on this tab as well
    external_guests = df[df['Típus'] == 'Külsős']
    if not external_guests.empty:
        st.subheader("🍽️ Külsős Ebédet Igénylők (Nem szállásosak)")
        st.dataframe(
            external_guests[['Név', 'Típus', 'Külsős Ebédek Száma', 'Összköltség', 'Fizetett előleg', 'Előleg Státusz', 'Megjegyzés']],
            use_container_width=True
        )


# -----------------------------------------------------------------------------
# TAB 2: GUEST DIRECTORY TABLE
# -----------------------------------------------------------------------------
with tab_guests:
    st.header("👥 Vendégek Részletes Nyilvántartása")
    st.markdown("""
        Itt látható a teljes vendég adatbázis. A táblázat közvetlenül szerkeszthető!
        - Új sort a táblázat alján lévő `+` gombbal adhatsz hozzá.
        - Kiválasztott sorokat a törlés gombbal (kijelölés után Delete) távolíthatsz el.
        - Bármely cella dupla kattintással módosítható. A mentés és újraszámítás automatikus.
    """)
    
    # Download CSV
    csv_data = st.session_state.guests_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Vendéglista letöltése (CSV)",
        data=csv_data,
        file_name="tabor_vendeglista_2026.csv",
        mime="text/csv"
    )
    
    # Simple search bar
    search_query = st.text_input("🔍 Keresés a vendégek neve vagy szállása alapján:", "")
    
    # Prepare column options for editor
    room_list = [r['Név'] for r in accommodations] + ["Külsős (Nincs)", "Külsős (Sátor)", "Külsős (Lakókocsi)"]
    
    if search_query:
        # Filtered View (Read-Only to avoid complex merge bugs)
        filtered_df = df[
            df['Név'].str.contains(search_query, case=False, na=False) |
            df['Szállás'].str.contains(search_query, case=False, na=False)
        ]
        st.warning("⚠️ **Keresési üzemmód aktív:** A táblázat most csak olvasható. A módosításhoz ürítsd ki a fenti keresőmezőt!")
        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "Név": "Név",
                "Típus": "Kategória",
                "Szállás": "Szálláshely",
                "Éjszakák Száma": "Éjszakák",
                "Két család egy szobában": "Szobamegosztás (2 család)",
                "Kedvezmény (%)": "Kedvezmény (%)",
                "Fizetett előleg": "Befizetett előleg (RON)",
                "Státusz": "Státusz",
                "Külsős Ebédek Száma": "Külsős Ebédek",
                "Összköltség": "Összes Költség (RON)",
                "Előleg Státusz": "Előleg Ellenőrzés",
                "Megjegyzés": "Megjegyzés"
            }
        )
    else:
        # Fully Editable Data Editor
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Név": st.column_config.TextColumn("Név (Vendég / Csoport)", required=True),
                "Típus": st.column_config.SelectboxColumn("Vendég Kategória", options=["Felnőtt", "Fiatal/Diák", "Gyerek", "Kisgyerek", "Külsős"], required=True),
                "Szállás": st.column_config.SelectboxColumn("Szálláshely", options=room_list, required=True),
                "Éjszakák Száma": st.column_config.NumberColumn("Éjszakák száma", min_value=1, max_value=5, step=1, default=5, required=True),
                "Két család egy szobában": st.column_config.CheckboxColumn("Szobamegosztás (2 család)"),
                "Kedvezmény (%)": st.column_config.NumberColumn("Kedvezmény (%)", min_value=0.0, max_value=100.0, step=1.0, default=0.0),
                "Fizetett előleg": st.column_config.NumberColumn("Befizetett előleg (RON)", min_value=0.0, step=10.0),
                "Státusz": st.column_config.SelectboxColumn("Foglalás Státusza", options=["Végleges", "Függőben"], required=True),
                "Külsős Ebédek Száma": st.column_config.NumberColumn("Külsős Ebédek", min_value=0, max_value=10, step=1, default=0),
                "Megjegyzés": st.column_config.TextColumn("Megjegyzés"),
                # Calculated columns (ReadOnly)
                "Összköltség": st.column_config.NumberColumn("Összköltség (RON)", format="%.2f RON", disabled=True),
                "Előleg Státusz": st.column_config.TextColumn("Előleg Státusz", disabled=True),
                "Bedő Laci Kaja": st.column_config.NumberColumn("Bedő Laci kaja (RON)", format="%.2f", disabled=True),
                "Tribel Ebéd": st.column_config.NumberColumn("Tribel ebéd (RON)", format="%.2f", disabled=True),
            }
        )
        
        # Save modifications if there are changes
        if not edited_df.equals(df):
            st.session_state.guests_df = recalculate_dataframe(edited_df)
            save_data(st.session_state.guests_df)
            st.rerun()


# -----------------------------------------------------------------------------
# TAB 3: FINANCIALS PANEL
# -----------------------------------------------------------------------------
with tab_financials:
    st.header("📊 Admin 1")
    if not st.session_state.get('admin_unlocked'):
        pwd = st.text_input("Kérlek, add meg a jelszót a belépéshez:", type="password", key="pwd_admin_1")
        if pwd == "lajcsika87":
            st.session_state['admin_unlocked'] = True
            st.rerun()
        elif pwd:
            st.error("❌ Hibás jelszó!")
            
    if st.session_state.get('admin_unlocked'):
        if st.button("🔒 Admin zárolása", key="lock_admin_1"):
            st.session_state['admin_unlocked'] = False
            st.rerun()
            
        st.subheader("Szolgáltatói Elszámolás és Pénzügyek")
        st.markdown("A tábor kiadásainak részletezése a szolgáltatók szerint, valamint a nettó profit számítása.")
        
        col_fin1, col_fin2 = st.columns([1, 1.2])
        
        with col_fin1:
            st.subheader("Kiadások Részletezése")
            
            # Bedő Laci detail
            st.markdown("#### 🧑‍🍳 Bedő Laci (Szállás & Félpanzió)")
            st.write(f"- **Szállásbérlés (Fix 5 nap):** {fixed_rent_laci:,.0f} RON")
            st.write(f"- **Félpanziós étkeztetés:** {total_bedo_food_cost:,.0f} RON")
            st.write(f"- **Bruttó elszámolás:** {gross_payout_laci:,.0f} RON")
            st.write(f"- *Már kifizetett előleg (levonás):* -{prepaid_deduction_laci:,.0f} RON")
            st.info(f"👉 **Bedő Lacinak most fizetendő nettó:** **{net_payout_laci:,.0f} RON**")
            
            # Tribel detail
            st.markdown("#### 🍱 Tribel (Ebéd)")
            st.write(f"- **Táborozók ebédje (felnőtt/diák/gyerek):** {df[df['Típus'] != 'Külsős']['Tribel Ebéd'].sum():,.0f} RON")
            st.write(f"- **Külsős vendégek ebédje:** {df[df['Típus'] == 'Külsős']['Tribel Ebéd'].sum():,.0f} RON")
            st.info(f"👉 **Tribel részére fizetendő összesen:** **{total_tribel_lunch_cost:,.0f} RON**")
            
            # Overall Summary Table
            st.markdown("#### 📈 Pénzügyi Mérleg Összegzés")
            summary_data = {
                "Megnevezés": [
                    "Összes Várható Részvételi Díj (Bevétel)",
                    "Bedő Laci Bruttó Díja (Kiadás)",
                    "Tribel Díja (Kiadás)",
                    "Összesített Kiadás",
                    "Nettó Tábori Profit"
                ],
                "Összeg (RON)": [
                    total_income,
                    gross_payout_laci,
                    total_tribel_lunch_cost,
                    gross_payout_laci + total_tribel_lunch_cost,
                    net_profit
                ]
            }
            st.table(pd.DataFrame(summary_data))
            
        with col_fin2:
            st.subheader("Pénzügyi Megoszlás Grafikonon")
            
            # Create chart
            categories = ['Bevételek', 'Bedő Laci (Kiadás)', 'Tribel (Kiadás)', 'Nettó Profit']
            amounts = [total_income, gross_payout_laci, total_tribel_lunch_cost, net_profit]
            colors = ['#2ca02c', '#d62728', '#ff7f0e', '#9467bd']
            
            fig = go.Figure(data=[go.Bar(
                x=categories,
                y=amounts,
                marker_color=colors,
                text=[f"{val:,.0f} RON" for val in amounts],
                textposition='auto',
            )])
            
            fig.update_layout(
                title='Tábor Pénzügyi Egyenlege (RON)',
                xaxis_title='Kategória',
                yaxis_title='Összeg (RON)',
                template='plotly_white',
                height=450
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics breakdown card
            st.subheader("Táborozók statisztikája")
            stats_df = df.groupby('Típus').agg(
                Fő=('Név', 'count'),
                Befizetett=('Fizetett előleg', 'sum'),
                Költség=('Összköltség', 'sum')
            ).reset_index()
            
            st.dataframe(stats_df, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: MEAL PORTIONS BREAKDOWN
# -----------------------------------------------------------------------------
with tab_meals:
    st.header("🍽️ Admin 2")
    if not st.session_state.get('admin_unlocked'):
        pwd = st.text_input("Kérlek, add meg a jelszót a belépéshez:", type="password", key="pwd_admin_2")
        if pwd == "lajcsika87":
            st.session_state['admin_unlocked'] = True
            st.rerun()
        elif pwd:
            st.error("❌ Hibás jelszó!")
            
    if st.session_state.get('admin_unlocked'):
        if st.button("🔒 Admin zárolása", key="lock_admin_2"):
            st.session_state['admin_unlocked'] = False
            st.rerun()
            
        st.subheader("Napi Étkezés és Adagszám Összesítő")
        st.markdown("""
            Ez a táblázat napi bontásban mutatja meg, hogy hány adag ételt kell rendelni a szolgáltatóktól.
            - **Felnőtt adagok:** Felnőtt, Fiatal/Diák és Külsős kategóriák részére.
            - **Gyermek adagok:** Gyerek kategóriájú vendégek részére.
            - *Megjegyzés: A Kisgyerekek (0-3 év) részére a szoftver nem számol külön adagot.*
        """)
        
        # Initialize daily totals
        days_data = {
            'Kedd (08.18)':       {'R_A': 0, 'R_K': 0, 'E_A': 0, 'E_K': 0, 'V_A': 0, 'V_K': 0},
            'Szerda (08.19)':     {'R_A': 0, 'R_K': 0, 'E_A': 0, 'E_K': 0, 'V_A': 0, 'V_K': 0},
            'Csütörtök (08.20)':  {'R_A': 0, 'R_K': 0, 'E_A': 0, 'E_K': 0, 'V_A': 0, 'V_K': 0},
            'Péntek (08.21)':     {'R_A': 0, 'R_K': 0, 'E_A': 0, 'E_K': 0, 'V_A': 0, 'V_K': 0},
            'Szombat (08.22)':    {'R_A': 0, 'R_K': 0, 'E_A': 0, 'E_K': 0, 'V_A': 0, 'V_K': 0},
            'Vasárnap (08.23)':   {'R_A': 0, 'R_K': 0, 'E_A': 0, 'E_K': 0, 'V_A': 0, 'V_K': 0}
        }
        
        all_meals = ['T_D', 'W_BD', 'W_L', 'Th_BD', 'Th_L', 'F_BD', 'F_L', 'S_BD', 'S_L', 'Su_BD', 'Su_L']
        
        for _, r in df.iterrows():
            g_type = r.get('Típus', 'Felnőtt')
            if g_type == 'Kisgyerek':
                continue
                
            is_child = (g_type == 'Gyerek')
            suffix = '_K' if is_child else '_A'
            
            meals_str = r.get('Étkezések', 'ALL')
            if not meals_str or str(meals_str).strip() == 'ALL' or str(meals_str).strip() == 'nan':
                active = all_meals
            else:
                active = [m.strip() for m in str(meals_str).split(',') if m.strip()]
                
            for m in active:
                if m == 'T_D':
                    days_data['Kedd (08.18)']['V' + suffix] += 1
                elif m == 'W_BD':
                    days_data['Szerda (08.19)']['R' + suffix] += 1
                    days_data['Szerda (08.19)']['V' + suffix] += 1
                elif m == 'W_L':
                    days_data['Szerda (08.19)']['E' + suffix] += 1
                elif m == 'Th_BD':
                    days_data['Csütörtök (08.20)']['R' + suffix] += 1
                    days_data['Csütörtök (08.20)']['V' + suffix] += 1
                elif m == 'Th_L':
                    days_data['Csütörtök (08.20)']['E' + suffix] += 1
                elif m == 'F_BD':
                    days_data['Péntek (08.21)']['R' + suffix] += 1
                    days_data['Péntek (08.21)']['V' + suffix] += 1
                elif m == 'F_L':
                    days_data['Péntek (08.21)']['E' + suffix] += 1
                elif m == 'S_BD':
                    days_data['Szombat (08.22)']['R' + suffix] += 1
                    days_data['Szombat (08.22)']['V' + suffix] += 1
                elif m == 'S_L':
                    days_data['Szombat (08.22)']['E' + suffix] += 1
                elif m == 'Su_BD':
                    days_data['Vasárnap (08.23)']['R' + suffix] += 1
                elif m == 'Su_L':
                    days_data['Vasárnap (08.23)']['E' + suffix] += 1
                    
        # Format into DataFrame for st.dataframe
        rows = []
        for day, vals in days_data.items():
            total_day_portions = sum(vals.values())
            rows.append({
                'Nap': day,
                'Reggeli (Felnőtt)': vals['R_A'],
                'Reggeli (Gyerek)': vals['R_K'],
                'Ebéd (Felnőtt)': vals['E_A'],
                'Ebéd (Gyerek)': vals['E_K'],
                'Vacsora (Felnőtt)': vals['V_A'],
                'Vacsora (Gyerek)': vals['V_K'],
                'Napi Összesen': total_day_portions
            })
            
        portions_df = pd.DataFrame(rows)
        
        st.subheader("📊 Napi rendelési táblázat")
        st.dataframe(portions_df, use_container_width=True, hide_index=True)
        
        st.subheader("💡 Gyors összesítések a konyha számára")
        
        col_meal1, col_meal2, col_meal3 = st.columns(3)
        
        # Calculate global totals
        total_breakfast_a = sum(v['R_A'] for v in days_data.values())
        total_breakfast_k = sum(v['R_K'] for v in days_data.values())
        total_lunch_a = sum(v['E_A'] for v in days_data.values())
        total_lunch_k = sum(v['E_K'] for v in days_data.values())
        total_dinner_a = sum(v['V_A'] for v in days_data.values())
        total_dinner_k = sum(v['V_K'] for v in days_data.values())
        
        col_meal1.metric("Reggeli Összes adag", f"{total_breakfast_a + total_breakfast_k} adag", f"F: {total_breakfast_a} | Gy: {total_breakfast_k}")
        col_meal2.metric("Ebéd Összes adag", f"{total_lunch_a + total_lunch_k} adag", f"F: {total_lunch_a} | Gy: {total_lunch_k}")
        col_meal3.metric("Vacsora Összes adag", f"{total_dinner_a + total_dinner_k} adag", f"F: {total_dinner_a} | Gy: {total_dinner_k}")

# Footer info
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 12px;'>"
    "Created with ❤️ by <a href='https://optibase.ro' target='_blank' style='color: gray; text-decoration: underline;'>OptiBase</a>"
    "</div>",
    unsafe_allow_html=True
)
