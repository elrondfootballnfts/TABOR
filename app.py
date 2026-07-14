import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os
import base64
import json

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
    {"Név": "Sátor 1", "Típus": "Sátor", "Kapacitás": 4, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor 2", "Típus": "Sátor", "Kapacitás": 4, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor 3", "Típus": "Sátor", "Kapacitás": 4, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor 4", "Típus": "Sátor", "Kapacitás": 4, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor 5", "Típus": "Sátor", "Kapacitás": 4, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor 6", "Típus": "Sátor", "Kapacitás": 3, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor 7", "Típus": "Sátor", "Kapacitás": 3, "Megjegyzés": "Fiataloknak/diákoknak"},
    {"Név": "Sátor 8", "Típus": "Sátor", "Kapacitás": 3, "Megjegyzés": "Fiataloknak/diákoknak"}
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
    'A':  {'name': 'Sátor A',         'label': 'A',  'x': 28.5, 'y': 17.0, 'rooms': ['Sátor 1']},
    'B':  {'name': 'Sátor B',         'label': 'B',  'x': 24.5, 'y': 23.0, 'rooms': ['Sátor 2']},
    'C':  {'name': 'Sátor C',         'label': 'C',  'x': 18.0, 'y': 27.0, 'rooms': ['Sátor 3']},
    'D':  {'name': 'Sátor D',         'label': 'D',  'x': 16.5, 'y': 33.5, 'rooms': ['Sátor 4']},
    'E':  {'name': 'Sátor E',         'label': 'E',  'x': 15.5, 'y': 43.0, 'rooms': ['Sátor 5']},
    'F':  {'name': 'Sátor F',         'label': 'F',  'x': 17.5, 'y': 51.0, 'rooms': ['Sátor 6']},
    'G':  {'name': 'Sátor G',         'label': 'G',  'x': 19.0, 'y': 57.5, 'rooms': ['Sátor 7']},
    'H':  {'name': 'Sátor H',         'label': 'H',  'x': 20.5, 'y': 64.5, 'rooms': ['Sátor 8']},
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
try:
    map_component = components.declare_component("map_component", path="tabor_map_component")
except Exception:
    map_component = None

# 3. BUSINESS LOGIC & PRICING ENGINE
# -----------------------------------------------------------------------------
def calculate_accommodation_cost(row):
    guest_type = row.get('Típus', 'Felnőtt')
    accommodation = row.get('Szállás', '')
    shared = bool(row.get('Két család egy szobában', False))
    nights = int(row.get('Éjszakák Száma', 5))
    
    if guest_type == 'Külsős' or "Nincs" in str(accommodation) or not accommodation:
        return 0.0
        
    if guest_type == 'Felnőtt':
        is_tent = "Sátor" in str(accommodation)
        rate = 70.0 if (is_tent or shared) else 120.0
    elif guest_type == 'Fiatal/Diák':
        rate = 60.0
    elif guest_type == 'Gyerek':
        rate = 25.0
    elif guest_type == 'Kisgyerek':
        rate = 0.0
    else:
        rate = 120.0
        
    return float(rate * nights)

def calculate_meals_cost(meals_str, guest_type):
    if guest_type == 'Kisgyerek':
        return 0.0
    
    all_meals = ['T_D', 'W_BD', 'W_L', 'Th_BD', 'Th_L', 'F_BD', 'F_L', 'S_BD', 'S_L', 'Su_BD', 'Su_L']
    if not meals_str or str(meals_str).strip() == 'ALL' or str(meals_str).strip() == 'nan':
        active_meals = all_meals
    else:
        active_meals = [m.strip() for m in str(meals_str).split(',') if m.strip()]
        
    is_child = (guest_type == 'Gyerek')
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

def calculate_single_guest_cost(row):
    acc_cost = calculate_accommodation_cost(row)
    meals_str = row.get('Étkezések', 'ALL')
    guest_type = row.get('Típus', 'Felnőtt')
    meals_cost = calculate_meals_cost(meals_str, guest_type)
    return float(acc_cost + meals_cost)

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
        
    is_child = (guest_type == 'Gyerek')
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
        
    is_child = (guest_type == 'Gyerek')
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
            'Két család egy szobában', 'Fizetett előleg', 'Státusz', 
            'Külsős Ebédek Száma', 'Megjegyzés', 'Étkezések', 'Összköltség', 
            'Előleg Státusz', 'Bedő Laci Kaja', 'Tribel Ebéd'
        ])
    
    df['Éjszakák Száma'] = df['Éjszakák Száma'].fillna(5).astype(int)
    df['Külsős Ebédek Száma'] = df['Külsős Ebédek Száma'].fillna(0).astype(int)
    df['Fizetett előleg'] = df['Fizetett előleg'].fillna(0.0).astype(float)
    df['Két család egy szobában'] = df['Két család egy szobában'].fillna(False).astype(bool)
    df['Étkezések'] = df.get('Étkezések', 'ALL')
    df['Étkezések'] = df['Étkezések'].fillna('ALL').astype(str)
    
    df['Összköltség'] = df.apply(calculate_single_guest_cost, axis=1)
    df['Státusz'] = df.apply(check_guest_status, axis=1)
    df['Előleg Státusz'] = df.apply(check_deposit, axis=1)
    df['Bedő Laci Kaja'] = df.apply(calculate_bedo_food, axis=1)
    df['Tribel Ebéd'] = df.apply(calculate_tribel_lunch, axis=1)
    return df


DB_FILE = "guests_db.csv"

def save_data(df):
    try:
        df.to_csv(DB_FILE, index=False)
    except Exception as e:
        st.error(f"Hiba az adatok mentésekor: {e}")

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # Ensure correct types and handle NA
            df['Két család egy szobában'] = df['Két család egy szobában'].fillna(False).astype(bool)
            df['Éjszakák Száma'] = df['Éjszakák Száma'].fillna(5).astype(int)
            df['Fizetett előleg'] = df['Fizetett előleg'].fillna(0.0).astype(float)
            df['Külsős Ebédek Száma'] = df['Külsős Ebédek Száma'].fillna(0).astype(int)
            return recalculate_dataframe(df)
        except Exception as e:
            st.error(f"Hiba az adatbázis betöltésekor: {e}. Alaphelyzet betöltése.")
            
    # Default initial data
    df_init = pd.DataFrame(prepopulated_guests)
    df_init = recalculate_dataframe(df_init)
    save_data(df_init)
    return df_init

# Initialize the guest database in session state if not already set
if 'guests_df' not in st.session_state:
    st.session_state.guests_df = load_data()


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
        if occ == 0:
            color = 'red'
            status_text = 'Üres'
        elif has_pending:
            color = 'yellow'
            status_text = 'Függőben'
        else:
            color = 'green'
            status_text = 'Végleges'
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
            'room_details': room_details, 'guests': guests
        }
    return status








@st.dialog("🏡 Épület Foglalások Kezelése", width="large")
def manage_building_bookings(building_id):
    bdata = BUILDING_GROUPS.get(building_id)
    if not bdata:
        st.error("Épület nem található.")
        return
        
    st.markdown(f"### {bdata['name']}")
    
    df = st.session_state.guests_df
    rooms = bdata['rooms']
    
    # 1. Edit existing guests in building
    st.subheader("👥 Meglévő vendégek szerkesztése")
    
    building_guests = df[df['Szállás'].isin(rooms)]
    
    if building_guests.empty:
        st.info("Nincs még vendég elhelyezve ebben az épületben.")
        updated_guests = []
    else:
        updated_guests = []
        for idx_g, g in building_guests.iterrows():
            st.markdown(f"##### {g['Név']} - szoba: **{g['Szállás']}** ({g['Típus']})")
            col1, col2, col3 = st.columns([2, 1, 1])
            g_name = col1.text_input(f"Név##{idx_g}", value=g['Név'])
            g_type = col2.selectbox(f"Kategória##{idx_g}", ["Felnőtt", "Fiatal/Diák", "Gyerek", "Kisgyerek"], index=["Felnőtt", "Fiatal/Diák", "Gyerek", "Kisgyerek"].index(g['Típus']) if g['Típus'] in ["Felnőtt", "Fiatal/Diák", "Gyerek", "Kisgyerek"] else 0)
            g_room = col3.selectbox(f"Szoba##{idx_g}", rooms, index=rooms.index(g['Szállás']) if g['Szállás'] in rooms else 0)
            
            col4, col5, col6 = st.columns([1, 1, 1])
            g_nights = col4.slider(f"Éjszakák##{idx_g}", min_value=1, max_value=5, value=int(g['Éjszakák Száma']))
            g_paid = col5.number_input(f"Befizetett előleg (RON)##{idx_g}", min_value=0.0, value=float(g['Fizetett előleg']), step=50.0)
            g_status_bool = col6.checkbox(f"Véglegesített?##{idx_g}", value=(g['Státusz'] == "Végleges"))
            g_status = "Végleges" if g_status_bool else "Függőben"
            
            g_note = st.text_input(f"Megjegyzés##{idx_g}", value=g.get('Megjegyzés', ''))
            
            meal_options = {
                'T_D': "Kedd - Vacsora",
                'W_BD': "Szerda - Reggeli+Vacsora",
                'W_L': "Szerda - Ebéd",
                'Th_BD': "Csütörtök - Reggeli+Vacsora",
                'Th_L': "Csütörtök - Ebéd",
                'F_BD': "Péntek - Reggeli+Vacsora",
                'F_L': "Péntek - Ebéd",
                'S_BD': "Szombat - Reggeli+Vacsora",
                'S_L': "Szombat - Ebéd",
                'Su_BD': "Vasárnap - Reggeli",
                'Su_L': "Vasárnap - Ebéd"
            }
            reverse_meal_options = {v: k for k, v in meal_options.items()}
            cur_meals = str(g.get('Étkezések', 'ALL'))
            if cur_meals == 'ALL':
                default_selected = list(meal_options.values())
            else:
                default_selected = [meal_options[m.strip()] for m in cur_meals.split(',') if m.strip() in meal_options]
                
            selected_meal_labels = st.multiselect(
                f"Étkezések##{idx_g}",
                options=list(meal_options.values()),
                default=default_selected
            )
            g_meals = ",".join([reverse_meal_options[lbl] for lbl in selected_meal_labels])
            
            # Active visual price calculation
            # Calculate price
            acc_rate = 0
            if g_type == 'Felnőtt':
                is_tent = "Sátor" in g_room
                is_shared = bool(g.get('Két család egy szobában', False))
                acc_rate = 70 if (is_tent or is_shared) else 120
            elif g_type == 'Fiatal/Diák':
                acc_rate = 60
            elif g_type == 'Gyerek':
                acc_rate = 25
            
            acc_cost = acc_rate * g_nights
            meal_cost = 0
            for code in [reverse_meal_options[lbl] for lbl in selected_meal_labels]:
                if g_type in ['Felnőtt', 'Fiatal/Diák']:
                    if code == 'T_D': meal_cost += 40
                    elif '_BD' in code:
                        meal_cost += 30 if code == 'Su_BD' else 70
                    elif '_L' in code: meal_cost += 60
                elif g_type == 'Gyerek':
                    if code == 'T_D': meal_cost += 30
                    elif '_BD' in code:
                        meal_cost += 20 if code == 'Su_BD' else 50
                    elif '_L' in code: meal_cost += 50
            
            total_cost = acc_cost + meal_cost
            st.markdown(f"✨ **Kalkulált összeg:** Szállás: {acc_cost} RON + Kaja: {meal_cost} RON = **{total_cost} RON**")
            
            # Delete button for this guest
            if st.button(f"🗑️ {g['Név']} Törlése", key=f"del_g_{idx_g}", type="secondary"):
                df = df.drop(idx_g)
                st.session_state.guests_df = recalculate_dataframe(df)
                save_data(st.session_state.guests_df)
                st.success(f"{g['Név']} sikeresen törölve!")
                st.rerun()
                
            updated_guests.append({
                'idx': idx_g,
                'Név': g_name,
                'Típus': g_type,
                'Szállás': g_room,
                'Éjszakák Száma': g_nights,
                'Két család egy szobában': bool(g.get('Két család egy szobában', False)),
                'Fizetett előleg': g_paid,
                'Státusz': g_status,
                'Megjegyzés': g_note,
                'Étkezések': g_meals
            })
            st.markdown("---")
            
    # 2. Add new guest
    st.subheader("➕ Új foglalás regisztrálása")
    
    col_n1, col_n2, col_n3 = st.columns([2, 1, 1])
    new_name = col_n1.text_input("Új vendég neve:", key="new_g_name", placeholder="Pl. Szabó Család")
    new_type = col_n2.selectbox("Kategória:", ["Felnőtt", "Fiatal/Diák", "Gyerek", "Kisgyerek"], key="new_g_type")
    
    cap_lookup = {r['Név']: r['Kapacitás'] for r in accommodations}
    avail_rooms = []
    for r in rooms:
        occ = len(df[df['Szállás'] == r])
        cap = cap_lookup.get(r, 0)
        if occ < cap:
            avail_rooms.append(f"{r} ({occ}/{cap} fő)")
            
    if not avail_rooms:
        st.warning("⚠️ Ez az épület teljesen megtelt, nem adható hozzá új vendég!")
        new_room = None
    else:
        new_room_label = col_n3.selectbox("Szoba választás:", avail_rooms, key="new_g_room")
        new_room = new_room_label.split(' (')[0] if new_room_label else None
        
    col_n4, col_n5, col_n6 = st.columns([1, 1, 1])
    new_nights = col_n4.slider("Éjszakák száma:", min_value=1, max_value=5, value=5, key="new_g_nights")
    new_paid = col_n5.number_input("Előleg (RON):", min_value=0.0, value=0.0, step=50.0, key="new_g_paid")
    new_status_bool = col_n6.checkbox("Véglegesített foglalás?", value=True, key="new_g_status")
    new_status = "Végleges" if new_status_bool else "Függőben"
    new_note = st.text_input("Megjegyzés:", key="new_g_note", placeholder="Pl. Ételallergia...")
    
    new_meal_options = {
        'T_D': "Kedd - Vacsora",
        'W_BD': "Szerda - Reggeli+Vacsora",
        'W_L': "Szerda - Ebéd",
        'Th_BD': "Csütörtök - Reggeli+Vacsora",
        'Th_L': "Csütörtök - Ebéd",
        'F_BD': "Péntek - Reggeli+Vacsora",
        'F_L': "Péntek - Ebéd",
        'S_BD': "Szombat - Reggeli+Vacsora",
        'S_L': "Szombat - Ebéd",
        'Su_BD': "Vasárnap - Reggeli",
        'Su_L': "Vasárnap - Ebéd"
    }
    reverse_new_meal_options = {v: k for k, v in new_meal_options.items()}
    selected_new_meal_labels = st.multiselect(
        "Igényelt étkezések (új vendég):",
        options=list(new_meal_options.values()),
        default=list(new_meal_options.values()),
        key="new_g_meals"
    )
    new_meals = ",".join([reverse_new_meal_options[lbl] for lbl in selected_new_meal_labels])
    
    # New guest price calculation
    if new_name.strip() and new_room:
        new_acc_rate = 0
        if new_type == 'Felnőtt':
            is_tent = "Sátor" in new_room
            new_acc_rate = 70 if is_tent else 120
        elif new_type == 'Fiatal/Diák':
            new_acc_rate = 60
        elif new_type == 'Gyerek':
            new_acc_rate = 25
            
        new_acc_cost = new_acc_rate * new_nights
        new_meal_cost = 0
        for code in [reverse_new_meal_options[lbl] for lbl in selected_new_meal_labels]:
            if new_type in ['Felnőtt', 'Fiatal/Diák']:
                if code == 'T_D': new_meal_cost += 40
                elif '_BD' in code:
                    new_meal_cost += 30 if code == 'Su_BD' else 70
                elif '_L' in code: new_meal_cost += 60
            elif new_type == 'Gyerek':
                if code == 'T_D': new_meal_cost += 30
                elif '_BD' in code:
                    new_meal_cost += 20 if code == 'Su_BD' else 50
                elif '_L' in code: new_meal_cost += 50
        
        new_total_cost = new_acc_cost + new_meal_cost
        st.markdown(f"✨ **Új vendég kalkulált összege:** Szállás: {new_acc_cost} RON + Kaja: {new_meal_cost} RON = **{new_total_cost} RON**")
    
    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("💾 Módosítások Mentése", type="primary", use_container_width=True):
        # Update existing
        for ug in updated_guests:
            idx = ug['idx']
            df.loc[idx, 'Név'] = ug['Név']
            df.loc[idx, 'Típus'] = ug['Típus']
            df.loc[idx, 'Szállás'] = ug['Szállás']
            df.loc[idx, 'Éjszakák Száma'] = ug['Éjszakák Száma']
            df.loc[idx, 'Fizetett előleg'] = ug['Fizetett előleg']
            df.loc[idx, 'Státusz'] = ug['Státusz']
            df.loc[idx, 'Megjegyzés'] = ug['Megjegyzés']
            df.loc[idx, 'Étkezések'] = ug['Étkezések']
            
        # Add new if present
        if new_name.strip() and new_room:
            new_row = {
                'Név': new_name.strip(),
                'Típus': new_type,
                'Szállás': new_room,
                'Éjszakák Száma': new_nights,
                'Két család egy szobában': False,
                'Fizetett előleg': new_paid,
                'Státusz': new_status,
                'Külsős Ebédek Száma': 0,
                'Megjegyzés': new_note,
                'Étkezések': new_meals
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
        st.session_state.guests_df = recalculate_dataframe(df)
        save_data(st.session_state.guests_df)
        st.session_state['map_success_msg'] = "🏡 Foglalások sikeresen elmentve!"
        
        st.rerun()
        
    if col_btn2.button("Bezárás", use_container_width=True):
        
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


# Tabs for different views
tab_map, tab_rooms, tab_guests, tab_financials, tab_meals = st.tabs([
    "🗺️ Interaktív Térkép",
    "🏡 Szállásosztó & Szobák",
    "👥 Vendég Nyilvántartás",
    "📊 Elszámolás & Pénzügy",
    "🍽️ Étkezés Összesítő"
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
    leg1, leg2, leg3, leg4 = st.columns(4)
    leg1.markdown("🔴 **Üres** – szabad")
    leg2.markdown("🟡 **Függőben** – ideiglenes")
    leg3.markdown("🟢 **Végleges** – foglalt")
    leg4.markdown("_(Kattints a körre!)_")

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
                        manage_building_bookings(map_result.get("bid"))
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
            # Color code logic: Red = completely empty, Yellow = temporary/pending status, Green = finalized status
            if occ == 0:
                # Red theme for completely empty
                bg = "#ffebee"
                text_col = "#c62828"
                border_col = "#ffcdd2"
                border_style = f"2px solid {border_col}"
            else:
                if room_has_pending[name]:
                    # Yellow theme for temporary status
                    bg = "#fff8e1"
                    text_col = "#e65100"
                    border_col = "#ffe082"
                    border_style = f"2px dashed #ff9800"
                else:
                    # Green theme for finalized status
                    bg = "#e8f5e9"
                    text_col = "#2e7d32"
                    border_col = "#a5d6a7"
                    border_style = f"2px solid {border_col}"
            
            # Guest list formatted
            guests_html = "<br>".join(room_guests_list[name]) if room_guests_list[name] else "Nincs vendég elhelyezve"
            
            # Pending badge
            badge_html = ""
            if room_has_pending[name]:
                badge_html = '<span class="badge badge-pending">⏳ FÜGGŐBEN</span>'
            elif occ > 0:
                badge_html = '<span class="badge badge-final">✅ VÉGLEGES</span>'
                
            col.markdown(f"""<div class="room-card" style="background-color: {bg}; color: {text_col}; border: {border_style};">
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
                btn_col1, btn_col2 = col.columns(2)
                if btn_col1.button(f"✏️ Szerkeszt", key=f"edit_btn_{name}", help=f"Szállás és lakók adatainak szerkesztése"):
                    edit_booking(name)
                if btn_col2.button(f"🗑️ Töröl", key=f"reset_{name}", help=f"Foglalás törlése és előleg kivétele a(z) {name} szálláshelyről"):
                    st.session_state.guests_df = st.session_state.guests_df[st.session_state.guests_df['Szállás'] != name]
                    st.session_state.guests_df = recalculate_dataframe(st.session_state.guests_df)
                    save_data(st.session_state.guests_df)
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
    room_list = [r['Név'] for r in accommodations] + ["Külsős (Nincs)"]
    
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
    st.header("📊 Szolgáltatói Elszámolás és Pénzügyek")
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
    st.header("🍽️ Napi Étkezés és Adagszám Összesítő")
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
