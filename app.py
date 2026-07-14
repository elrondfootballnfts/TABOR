import streamlit as st
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
    </style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. HARDCODED STRUCTURES & DEFAULT DATA
# -----------------------------------------------------------------------------
# Accommodations structure definition
accommodations = [
    # 2-Room Houses (Each room is 4-person capacity)
    {"Név": "Vadász Room 1", "Típus": "Kétkamrás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Vadász Room 2", "Típus": "Kétkamrás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Füzi Room 1", "Típus": "Kétkamrás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Füzi Room 2", "Típus": "Kétkamrás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Fa Room 1", "Típus": "Kétkamrás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Fa Room 2", "Típus": "Kétkamrás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Aurum Room 1", "Típus": "Kétkamrás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Aurum Room 2", "Típus": "Kétkamrás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Nóra Room 1", "Típus": "Kétkamrás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Nóra Room 2", "Típus": "Kétkamrás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Ágnes Room 1", "Típus": "Kétkamrás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    {"Név": "Ágnes Room 2", "Típus": "Kétkamrás Ház", "Kapacitás": 4, "Megjegyzés": ""},
    
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
# 3. BUSINESS LOGIC & PRICING ENGINE
# -----------------------------------------------------------------------------
def calculate_single_guest_cost(row):
    guest_type = row.get('Típus', 'Felnőtt')
    nights = int(row.get('Éjszakák Száma', 5))
    shared = bool(row.get('Két család egy szobában', False))
    accommodation = row.get('Szállás', 'Külsős (Nincs)')
    lunches_count = int(row.get('Külsős Ebédek Száma', 0))
    
    if guest_type == 'Külsős':
        return float(lunches_count * 60.0)
    
    # Base price mapping (for full 5-night period)
    if guest_type == 'Felnőtt':
        base = 1250.0
        # Discount rule: 20% off if Tent OR sharing a room (2 families)
        is_tent = "Sátor" in str(accommodation)
        if is_tent or shared:
            base = 1000.0  # 1250 * 0.8
    elif guest_type == 'Fiatal/Diák':
        base = 950.0
    elif guest_type == 'Gyerek':
        base = 625.0
    elif guest_type == 'Kisgyerek':
        base = 0.0
    else:
        base = 1250.0
        
    # Scale proportionally for nights stayed
    cost = (base / 5.0) * nights
    return float(cost)

def check_guest_status(row):
    # Rule: If a guest registers for only "pár nap" (less than 5 nights),
    # their status must be forced to "Függőben" (Pending).
    nights = int(row.get('Éjszakák Száma', 5))
    guest_type = row.get('Típus', 'Felnőtt')
    
    if guest_type != 'Külsős' and nights < 5:
        return 'Függőben'
    return row.get('Státusz', 'Végleges')

def check_deposit(row):
    # Rule: Minimum 20% deposit is required.
    cost = float(row.get('Összköltség', 0.0))
    paid = float(row.get('Fizetett előleg', 0.0))
    if cost > 0 and paid < (cost * 0.20):
        return "⚠️ Hiányzó előleg"
    return "Rendben"

def calculate_bedo_food(row):
    # Bedő Laci Fees: Food cost 70 RON/adult/day and 50 RON/kid/day (for breakfast + dinner)
    guest_type = row.get('Típus', 'Felnőtt')
    nights = int(row.get('Éjszakák Száma', 5))
    if guest_type == 'Külsős':
        return 0.0
    
    # Youth/Students eat like adults
    if guest_type in ['Felnőtt', 'Fiatal/Diák']:
        return float(70.0 * nights)
    elif guest_type == 'Gyerek':
        return float(50.0 * nights)
    return 0.0

def calculate_tribel_lunch(row):
    # Tribel Fees: Lunch cost 60 RON/adult/day and 40 RON/kid/day
    guest_type = row.get('Típus', 'Felnőtt')
    nights = int(row.get('Éjszakák Száma', 5))
    lunches = int(row.get('Külsős Ebédek Száma', 0))
    
    if guest_type == 'Külsős':
        return float(60.0 * lunches)
    
    # Youth/Students eat like adults
    if guest_type in ['Felnőtt', 'Fiatal/Diák']:
        return float(60.0 * nights)
    elif guest_type == 'Gyerek':
        return float(40.0 * nights)
    return 0.0

def recalculate_dataframe(df):
    """Calculates all dynamic columns for the entire guest DataFrame."""
    if df.empty:
        return pd.DataFrame(columns=[
            'Név', 'Típus', 'Szállás', 'Éjszakák Száma', 
            'Két család egy szobában', 'Fizetett előleg', 'Státusz', 
            'Külsős Ebédek Száma', 'Megjegyzés', 'Összköltség', 
            'Előleg Státusz', 'Bedő Laci Kaja', 'Tribel Ebéd'
        ])
    
    df['Éjszakák Száma'] = df['Éjszakák Száma'].fillna(5).astype(int)
    df['Külsős Ebédek Száma'] = df['Külsős Ebédek Száma'].fillna(0).astype(int)
    df['Fizetett előleg'] = df['Fizetett előleg'].fillna(0.0).astype(float)
    df['Két család egy szobában'] = df['Két család egy szobában'].fillna(False).astype(bool)
    
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
            guests.append({
                'idx': int(idx_g),
                'name': g['Név'], 'type': g['Típus'], 'room': g['Szállás'],
                'nights': int(g['Éjszakák Száma']), 'status': g['Státusz'],
                'paid': float(g['Fizetett előleg']), 'cost': float(g['Összköltség']),
                'note': str(note_val) if (note_val is not None and str(note_val) != 'nan') else ''
            })
        status[bid] = {
            'id': bid, 'name': bdata['name'],
            'capacity': total_cap, 'occupancy': occ,
            'color': color, 'status_text': status_text,
            'room_details': room_details, 'guests': guests
        }
    return status


def generate_map_html(img_b64: str, building_status: dict, edit_mode: bool = False, base_url: str = 'http://localhost:8501') -> str:
    """Generálja az interaktív műholdfelvétel HTML komponenst."""
    status_json = json.dumps(building_status, ensure_ascii=False)
    bgroups_json = json.dumps({b: {'x': v['x'], 'y': v['y']} for b, v in BUILDING_GROUPS.items()}, ensure_ascii=False)
    edit_mode_js = 'true' if edit_mode else 'false'

    # Hidden position fields for the save-positions form
    pos_fields_html = ''.join(
        '<input type="hidden" id="pf-{bid}" name="pos_{bid}" value="{x:.2f},{y:.2f}">\n'.format(
            bid=bid, x=bdata['x'], y=bdata['y'])
        for bid, bdata in BUILDING_GROUPS.items()
    )

    drag_bar_html = ''
    if edit_mode:
        drag_bar_html = (
            '<div id="drag-bar">'
            '<span>\u270b H\u00fazd a jel\u00f6l\u0151ket a helyes poz\u00edci\u00f3ba, majd mentsd a fenti nat\u00edv gombbal!</span>'
            '</div>'
        )

    hotspots_html = ''
    for bid, bdata in BUILDING_GROUPS.items():
        s = building_status.get(bid, {})
        color_map = {'red': '#ef5350', 'yellow': '#FFA726', 'green': '#66BB6A'}
        bg = color_map.get(s.get('color', 'red'), '#ef5350')
        x, y = bdata['x'], bdata['y']
        label = bdata['label']
        name = bdata['name']
        font_size = '11px' if len(label) <= 2 else '9px'
        drag_cursor = 'grab' if edit_mode else 'pointer'
        hotspots_html += (
            '<div class="hotspot" data-id="{bid}" style="left:{x}%;top:{y}%;cursor:{cursor};">'
            '<div class="marker" style="background:{bg};font-size:{fs};">{label}</div>'
            '<div class="hs-label">{name}</div>'
            '</div>'
        ).format(bid=bid, x=x, y=y, cursor=drag_cursor, bg=bg, fs=font_size, label=label, name=name)

    css = """
* {margin:0;padding:0;box-sizing:border-box;}
body {font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;background:#0a0a0a;overflow-x:hidden;}
#map-wrapper {position:relative;width:100%;border-radius:12px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,.5);}
#map-img {width:100%;display:block;user-select:none;}
.hotspot {position:absolute;transform:translate(-50%,-50%);z-index:10;}
.marker {
  width:32px;height:32px;border-radius:50%;color:#fff;font-weight:800;
  display:flex;align-items:center;justify-content:center;
  border:2.5px solid rgba(255,255,255,.85);
  box-shadow:0 2px 10px rgba(0,0,0,.55);
  transition:transform .18s,box-shadow .18s;
  text-shadow:0 1px 3px rgba(0,0,0,.5);
}
.hotspot:hover .marker {transform:scale(1.35);box-shadow:0 4px 18px rgba(0,0,0,.7);}
.hs-label {
  position:absolute;top:35px;left:50%;transform:translateX(-50%);
  background:rgba(15,15,15,.82);color:#fff;padding:2px 7px;
  border-radius:6px;font-size:10px;white-space:nowrap;
  pointer-events:none;opacity:0;transition:opacity .15s;backdrop-filter:blur(4px);
}
.hotspot:hover .hs-label {opacity:1;}
#drag-bar {
  position:absolute;bottom:0;left:0;right:0;z-index:20;
  background:linear-gradient(135deg,rgba(124,58,237,.92),rgba(168,85,247,.92));
  padding:10px 16px;display:flex;align-items:center;justify-content:space-between;
  backdrop-filter:blur(6px);
}
#drag-bar span {color:#fff;font-size:13px;font-weight:600;}
#drag-bar button {
  background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.4);
  color:#fff;padding:6px 16px;border-radius:8px;cursor:pointer;
  font-size:13px;font-weight:700;transition:background .15s;
}
#drag-bar button:hover {background:rgba(255,255,255,.35);}
#overlay {display:none;position:fixed;inset:0;z-index:50;background:rgba(0,0,0,.45);backdrop-filter:blur(2px);}
#popup {
  position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
  background:#1a1a2e;color:#e8e8f0;
  border-radius:16px;padding:0;min-width:340px;max-width:460px;width:92vw;
  box-shadow:0 20px 60px rgba(0,0,0,.7);z-index:100;
  max-height:88vh;overflow-y:auto;border:1px solid rgba(255,255,255,.1);
}
.popup-header {
  display:flex;align-items:center;justify-content:space-between;
  padding:16px 20px 12px;
  background:linear-gradient(135deg,#16213e,#0f3460);
  border-radius:16px 16px 0 0;border-bottom:1px solid rgba(255,255,255,.08);
}
.popup-title {font-size:17px;font-weight:700;color:#fff;display:flex;align-items:center;gap:8px;}
.popup-badge {font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;margin-left:6px;}
.badge-red {background:#ef5350;color:#fff;}
.badge-yellow {background:#FFA726;color:#fff;}
.badge-green {background:#66BB6A;color:#fff;}
.popup-close {
  background:rgba(255,255,255,.1);border:none;color:#fff;cursor:pointer;
  width:30px;height:30px;border-radius:50%;font-size:18px;
  display:flex;align-items:center;justify-content:center;transition:background .15s;
}
.popup-close:hover {background:rgba(255,255,255,.25);}
.popup-body {padding:14px 18px;}
.stat-row {display:flex;gap:10px;margin-bottom:12px;}
.stat-card {flex:1;background:rgba(255,255,255,.06);border-radius:10px;padding:10px;text-align:center;border:1px solid rgba(255,255,255,.08);}
.stat-num {font-size:22px;font-weight:700;color:#a78bfa;}
.stat-lbl {font-size:10px;color:#aaa;margin-top:2px;}
.sec-title {font-size:11px;font-weight:600;color:#888;text-transform:uppercase;letter-spacing:.8px;margin:12px 0 6px;}
.room-row {display:flex;align-items:center;background:rgba(255,255,255,.05);border-radius:8px;padding:6px 12px;margin-bottom:4px;font-size:12px;border:1px solid rgba(255,255,255,.06);}
.room-bar {height:5px;border-radius:3px;background:#333;flex:1;margin:0 10px;}
.room-fill {height:100%;border-radius:3px;}
.guest-row {background:rgba(255,255,255,.05);border-radius:8px;padding:8px 12px;margin-bottom:5px;border-left:3px solid #a78bfa;display:flex;justify-content:space-between;align-items:center;}
.guest-name {font-weight:600;color:#e8e8f0;font-size:13px;}
.guest-meta {color:#aaa;font-size:11px;margin-top:2px;}
.s-chip {display:inline-block;font-size:10px;font-weight:600;padding:1px 7px;border-radius:10px;margin-left:6px;}
.cg {background:#1b5e20;color:#a5d6a7;} .cy {background:#e65100;color:#ffe0b2;}
.edit-btn {background:rgba(167,139,250,.2);border:1px solid rgba(167,139,250,.4);color:#a78bfa;border-radius:6px;padding:4px 10px;font-size:11px;cursor:pointer;white-space:nowrap;transition:background .15s;}
.edit-btn:hover {background:rgba(167,139,250,.4);}
.divider {height:1px;background:rgba(255,255,255,.08);margin:12px 0;}
form.bf label {display:block;font-size:11px;color:#aaa;margin-bottom:2px;margin-top:8px;}
form.bf input,form.bf select {width:100%;background:#0d1117;color:#e8e8f0;border:1px solid rgba(255,255,255,.15);border-radius:8px;padding:7px 10px;font-size:12px;outline:none;transition:border-color .15s;}
form.bf input:focus,form.bf select:focus {border-color:#a78bfa;}
form.bf select option {background:#1a1a2e;}
.fr {display:flex;gap:8px;} .fr>div{flex:1;}
.sb {width:100%;margin-top:10px;background:linear-gradient(135deg,#7c3aed,#a855f7);color:#fff;border:none;border-radius:10px;padding:10px;font-size:14px;font-weight:700;cursor:pointer;transition:opacity .15s,transform .1s;}
.sb:hover {opacity:.9;transform:translateY(-1px);}
.sb.back {background:rgba(255,255,255,.08);}
.sb.esave {background:linear-gradient(135deg,#1565c0,#1976d2);}
.empty-hint {color:#888;font-size:13px;text-align:center;padding:8px 0;}
"""

    js = r"""
var STATUS = """ + status_json + r""";
var BUILDING_GROUPS = """ + bgroups_json + r""";
var EDIT_MODE = """ + edit_mode_js + r""";
var currentBid = null;

function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }
var BASE_URL = (function(){
  var ref = document.referrer;
  if (!ref) return window.location.origin + '/';
  var base = ref.split('?')[0];
  return base.endsWith('/') ? base : base + '/';
})();

// ── Click / Drag ───────────────────────────────────────────────────────
document.querySelectorAll('.hotspot').forEach(function(h){
  if(EDIT_MODE){
    var dragging=false, startX, startY, origLeft, origTop, mapRect;
    function onDown(cx,cy){
      dragging=true;
      mapRect=document.getElementById('map-wrapper').getBoundingClientRect();
      startX=cx; startY=cy;
      origLeft=parseFloat(h.style.left);
      origTop=parseFloat(h.style.top);
      h.querySelector('.marker').style.transform='scale(1.4)';
    }
    function onMove(cx,cy){
      if(!dragging)return;
      var dx=((cx-startX)/mapRect.width)*100;
      var dy=((cy-startY)/mapRect.height)*100;
      h.style.left=Math.max(2,Math.min(98,origLeft+dx)).toFixed(2)+'%';
      h.style.top =Math.max(2,Math.min(98,origTop +dy)).toFixed(2)+'%';
    }
    function onUp(){
      if(dragging) {
        var bid=h.getAttribute('data-id');
        BUILDING_GROUPS[bid].x = parseFloat(h.style.left);
        BUILDING_GROUPS[bid].y = parseFloat(h.style.top);
        var jsonStr = JSON.stringify(BUILDING_GROUPS);
        try {
          var parentUrl = new URL(window.parent.location.href);
          parentUrl.searchParams.set('tabor_pos_data', jsonStr);
          window.parent.history.replaceState(null, '', parentUrl.pathname + parentUrl.search);
        } catch(e) { console.error("URL sync failed:", e); }
      }
      dragging=false;
      h.querySelector('.marker').style.transform='';
    }
    h.addEventListener('mousedown',function(e){onDown(e.clientX,e.clientY);e.preventDefault();e.stopPropagation();});
    document.addEventListener('mousemove',function(e){if(dragging){onMove(e.clientX,e.clientY);e.preventDefault();}});
    document.addEventListener('mouseup',onUp);
    h.addEventListener('touchstart',function(e){onDown(e.touches[0].clientX,e.touches[0].clientY);e.preventDefault();},{passive:false});
    h.addEventListener('touchmove',function(e){onMove(e.touches[0].clientX,e.touches[0].clientY);e.preventDefault();},{passive:false});
    h.addEventListener('touchend',onUp);
  } else {
    h.addEventListener('click',function(){ openPopup(h.getAttribute('data-id')); });
  }
});


// ── Popup ────────────────────────────────────────────────────────────
function openPopup(bid){
  currentBid=bid;
  var s=STATUS[bid]; if(!s)return;
  var icon=bid.match(/^[A-H]$/)? '\u26fa' : '\ud83c\udfe1';
  document.getElementById('pp-icon').textContent=icon;
  document.getElementById('pp-title').textContent=s.name;
  var badge=document.getElementById('pp-badge');
  badge.textContent=s.status_text;
  badge.className='popup-badge badge-'+s.color;
  document.getElementById('pp-occ').textContent=s.occupancy;
  document.getElementById('pp-cap').textContent=s.capacity;
  document.getElementById('pp-free').textContent=Math.max(0,s.capacity-s.occupancy);

  var roomsEl=document.getElementById('pp-rooms');
  roomsEl.innerHTML='';
  var sec=document.getElementById('pp-rooms-sec');
  if(s.room_details && s.room_details.length>1){
    s.room_details.forEach(function(r){
      var pct=r.capacity>0?Math.round((r.occupancy/r.capacity)*100):0;
      var fc=pct===0?'#ef5350':(pct===100?'#66BB6A':'#FFA726');
      roomsEl.innerHTML+='<div class="room-row"><span style="min-width:100px">'+r.name+'</span><div class="room-bar"><div class="room-fill" style="width:'+pct+'%;background:'+fc+';"></div></div><span>'+r.occupancy+'/'+r.capacity+'</span></div>';
    });
    sec.style.display='';
  } else { sec.style.display='none'; }

  showGuestList(s);
  document.getElementById('overlay').style.display='block';
  document.getElementById('popup').style.display='block';
}

function showGuestList(s){
  var baseUrl=BASE_URL;
  var html='';
  if(s.guests && s.guests.length>0){
    html+='<div class="sec-title">Vend\u00e9gek</div>';
    s.guests.forEach(function(g){
      var cc=g.status==='V\u00e9gleges'?'cg':'cy';
      var ct=g.status==='V\u00e9gleges'?'\u2713 V\u00e9gleges':'\u23f3 F\u00fcgg\u0151ben';
      var payColor = '#ef5350';
      if (g.paid >= g.cost) {
        payColor = '#66BB6A';
      } else if (g.paid > 0) {
        payColor = '#FFA726';
      }
      html+='<div class="guest-row">'
        +'<div><div class="guest-name">'+esc(g.name)+'<span class="s-chip '+cc+'">'+ct+'</span></div>'
        +'<div class="guest-meta">'+esc(g.type)+' \u00b7 '+esc(g.room)+' \u00b7 '+g.nights+' \u00e9j \u00b7 <span style="color:'+payColor+';font-weight:600;">'+g.paid.toFixed(0)+' / '+g.cost.toFixed(0)+' RON</span></div></div>'
        +'<button class="edit-btn" onclick="showEditForm('+g.idx+')">\u270f\ufe0f Szerk.</button>'
        +'</div>';
    });
  } else {
    html+='<div class="empty-hint">Nincs vend\u00e9g ebben az \u00e9p\u00fcletben.</div>';
  }

  var avail=(s.room_details||[]).filter(function(r){return r.available>0;});
  html+='<div class="divider"></div>';
  if(avail.length>0){
    var roomOpts=avail.map(function(r){return '<option value="'+esc(r.name)+'">'+esc(r.name)+' ('+r.available+' szabad)</option>';}).join('');
    html+='<div class="sec-title">\u2795 \u00daj foglal\u00e1s</div>'
      +'<form class="bf" method="GET" action="'+baseUrl+'" target="_parent">'
      +'<input type="hidden" name="tabor_action" value="book">'
      +'<label>Vend\u00e9g neve</label><input type="text" name="tabor_name" required placeholder="Pl. Kov\u00e1cs Fam\u00edlia">'
      +'<label>Kateg\u00f3ria</label><select name="tabor_type"><option>Feln\u0151tt</option><option>Fiatal/Di\u00e1k</option><option>Gyerek</option><option>Kisgyerek</option><option>K\u00fcls\u0151s</option></select>'
      +'<label>Szoba</label><select name="tabor_room">'+roomOpts+'</select>'
      +'<div class="fr"><div><label>\u00c9jszak\u00e1k</label><input type="number" name="tabor_nights" value="5" min="1" max="5"></div>'
      +'<div><label>El\u0151leg (RON)</label><input type="number" name="tabor_paid" value="0" min="0" step="50"></div></div>'
      +'<label><input type="checkbox" name="tabor_status" value="V\u00e9gleges" style="width:auto;margin-right:6px;">V\u00e9gleges\u00edtett foglal\u00e1s</label>'
      +'<label>Megjegyz\u00e9s</label><input type="text" name="tabor_note" placeholder="Opcion\u00e1lis...">'
      +'<button type="submit" class="sb">💾 Ment\u00e9s</button>'
      +'</form>';
  } else {
    html+='<div class="empty-hint" style="color:#ef5350;">\U0001f534 Ez az \u00e9p\u00fclet megtelt.</div>';
  }
  document.getElementById('pp-main').innerHTML=html;
}

function showEditForm(guestIdx){
  var s=STATUS[currentBid]; if(!s)return;
  var g=s.guests.find(function(x){return x.idx===guestIdx;}); if(!g)return;
  var baseUrl=BASE_URL;

  var roomOpts=(s.room_details||[]).map(function(r){
    return '<option value="'+esc(r.name)+'"'+(r.name===g.room?' selected':'')+'>'+esc(r.name)+'</option>';
  }).join('');

  var typeOpts=['Feln\u0151tt','Fiatal/Di\u00e1k','Gyerek','Kisgyerek','K\u00fcls\u0151s'].map(function(t){
    return '<option value="'+t+'"'+(t===g.type?' selected':'')+'>'+t+'</option>';
  }).join('');

  var stChk=g.status==='V\u00e9gleges'?' checked':'';

  var html='<div class="sec-title">\u270f\ufe0f Vend\u00e9g szerkeszt\u00e9se</div>'
    +'<form class="bf" method="GET" action="'+baseUrl+'" target="_parent">'
    +'<input type="hidden" name="tabor_action" value="edit_guest">'
    +'<input type="hidden" name="tabor_guest_idx" value="'+guestIdx+'">'
    +'<label>Vend\u00e9g neve</label><input type="text" name="tabor_name" value="'+esc(g.name)+'" required>'
    +'<label>Kateg\u00f3ria</label><select name="tabor_type">'+typeOpts+'</select>'
    +'<label>Szoba</label><select name="tabor_room">'+roomOpts+'</select>'
    +'<div class="fr"><div><label>\u00c9jszak\u00e1k</label><input type="number" name="tabor_nights" value="'+g.nights+'" min="1" max="5"></div>'
    +'<div><label>El\u0151leg (RON)</label><input type="number" name="tabor_paid" value="'+g.paid+'" min="0" step="50"></div></div>'
    +'<label><input type="checkbox" name="tabor_status" value="V\u00e9gleges"'+stChk+' style="width:auto;margin-right:6px;">V\u00e9gleges\u00edtett foglal\u00e1s</label>'
    +'<label>Megjegyz\u00e9s</label><input type="text" name="tabor_note" value="'+esc(g.note||'')+'">'
    +'<button type="submit" class="sb esave">💾 M\u00f3dos\u00edt\u00e1sok ment\u00e9se</button>'
    +'</form>'
    +'<button class="sb back" onclick="showGuestList(STATUS[currentBid])">\u2190 Vissza</button>';

  document.getElementById('pp-main').innerHTML=html;
}

function closePopup(){
  document.getElementById('overlay').style.display='none';
  document.getElementById('popup').style.display='none';
}
document.addEventListener('keydown',function(e){if(e.key==='Escape')closePopup();});
"""

    popup_html = (
        '<div id="overlay" onclick="closePopup()"></div>'
        '<div id="popup" style="display:none;">'
        '  <div class="popup-header">'
        '    <div class="popup-title">'
        '      <span id="pp-icon">\U0001f3e1</span>'
        '      <span id="pp-title">-</span>'
        '      <span class="popup-badge" id="pp-badge">-</span>'
        '    </div>'
        '    <button class="popup-close" onclick="closePopup()">\u2715</button>'
        '  </div>'
        '  <div class="popup-body">'
        '    <div class="stat-row">'
        '      <div class="stat-card"><div class="stat-num" id="pp-occ">0</div><div class="stat-lbl">Foglalt</div></div>'
        '      <div class="stat-card"><div class="stat-num" id="pp-cap">0</div><div class="stat-lbl">Kapacit\u00e1s</div></div>'
        '      <div class="stat-card"><div class="stat-num" id="pp-free">0</div><div class="stat-lbl">Szabad</div></div>'
        '    </div>'
        '    <div id="pp-rooms-sec"><div class="sec-title">Szob\u00e1k</div><div id="pp-rooms"></div></div>'
        '    <div id="pp-main"></div>'
        '  </div>'
        '</div>'
    )

    return (
        '<!DOCTYPE html>\n<html lang="hu">\n<head>\n<meta charset="UTF-8">\n'
        '<style>\n' + css + '\n</style>\n</head>\n<body>\n'
        '<div id="map-wrapper">\n'
        '  <img id="map-img" src="data:image/jpeg;base64,' + img_b64 + '" draggable="false" />\n'
        + hotspots_html + '\n'
        + drag_bar_html + '\n'
        '</div>\n'
        + popup_html + '\n'
        '<script>\n' + js + '\n</script>\n'
        '</body>\n</html>'
    )



# -----------------------------------------------------------------------------
# 3c. QUERY PARAMS HANDLER – Térkép popup formból érkező foglalások
# -----------------------------------------------------------------------------
if 'tabor_action' in st.query_params:
    _action = st.query_params.get('tabor_action', '')
    try:
        qp = st.query_params

        if _action == 'book':
            new_name   = qp.get('tabor_name', '').strip()
            new_type   = qp.get('tabor_type', 'Feln\u0151tt')
            new_room   = qp.get('tabor_room', '')
            new_nights = int(qp.get('tabor_nights', 5))
            new_paid   = float(qp.get('tabor_paid', 0))
            new_status = 'V\u00e9gleges' if qp.get('tabor_status', '') == 'V\u00e9gleges' else 'F\u00fcgg\u0151ben'
            new_note   = qp.get('tabor_note', '')
            if new_nights < 5:
                new_status = 'F\u00fcgg\u0151ben'
            if new_name and new_room:
                new_row = {
                    'N\u00e9v': new_name, 'T\u00edpus': new_type, 'Sz\u00e1ll\u00e1s': new_room,
                    '\u00c9jszak\u00e1k Sz\u00e1ma': new_nights, 'K\u00e9t csal\u00e1d egy szob\u00e1ban': False,
                    'Fizetett el\u0151leg': new_paid, 'St\u00e1tusz': new_status,
                    'K\u00fcls\u0151s Eb\u00e9dek Sz\u00e1ma': 0, 'Megjegyz\u00e9s': new_note
                }
                _df = pd.concat([st.session_state.guests_df, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.guests_df = recalculate_dataframe(_df)
                save_data(st.session_state.guests_df)
                st.session_state['map_success_msg'] = f"\u2705 {new_name} sikeresen hozz\u00e1adva ({new_room})!"

        elif _action == 'edit_guest':
            g_idx    = int(qp.get('tabor_guest_idx', -1))
            g_name   = qp.get('tabor_name', '').strip()
            g_type   = qp.get('tabor_type', 'Feln\u0151tt')
            g_room   = qp.get('tabor_room', '')
            g_nights = int(qp.get('tabor_nights', 5))
            g_paid   = float(qp.get('tabor_paid', 0))
            g_status = 'V\u00e9gleges' if qp.get('tabor_status', '') == 'V\u00e9gleges' else 'F\u00fcgg\u0151ben'
            g_note   = qp.get('tabor_note', '')
            if g_nights < 5:
                g_status = 'F\u00fcgg\u0151ben'
            _df = st.session_state.guests_df
            if g_idx >= 0 and g_idx in _df.index and g_name and g_room:
                _df.loc[g_idx, 'N\u00e9v']               = g_name
                _df.loc[g_idx, 'T\u00edpus']             = g_type
                _df.loc[g_idx, 'Sz\u00e1ll\u00e1s']     = g_room
                _df.loc[g_idx, '\u00c9jszak\u00e1k Sz\u00e1ma'] = g_nights
                _df.loc[g_idx, 'Fizetett el\u0151leg']  = g_paid
                _df.loc[g_idx, 'St\u00e1tusz']           = g_status
                _df.loc[g_idx, 'Megjegyz\u00e9s']        = g_note
                st.session_state.guests_df = recalculate_dataframe(_df)
                save_data(st.session_state.guests_df)
                st.session_state['map_success_msg'] = f"\u2705 {g_name} adatai sikeresen m\u00f3dos\u00edtva!"
            else:
                st.session_state['map_error_msg'] = "Nem siker\u00fclt a vend\u00e9g azonos\u00edt\u00e1sa a m\u00f3dos\u00edt\u00e1shoz."

        elif _action == 'save_positions':
            new_positions = {}
            for bid in BUILDING_GROUPS:
                val = qp.get(f'pos_{bid}', '')
                if val and ',' in val:
                    parts = val.split(',')
                    try:
                        new_positions[bid] = {'x': float(parts[0]), 'y': float(parts[1])}
                        BUILDING_GROUPS[bid]['x'] = float(parts[0])
                        BUILDING_GROUPS[bid]['y'] = float(parts[1])
                    except ValueError:
                        pass
            if new_positions:
                with open(_POS_FILE, 'w', encoding='utf-8') as _pf:
                    json.dump(new_positions, _pf, ensure_ascii=False, indent=2)
                st.session_state['map_success_msg'] = "\u2705 Jelölők pozíciói sikeresen elmentve!"
                st.session_state['map_edit_toggle_drag'] = False
            else:
                st.session_state['map_error_msg'] = f"Nem érkezett érvényes pozíció adat! (Paraméterek: {dict(qp)})"

    except Exception as _e:
        st.session_state['map_error_msg'] = f"Hiba: {_e}"
    finally:
        st.query_params.clear()


@st.dialog("🏡 Foglalás Módosítása")
def edit_booking(room_name):
    st.write(f"A(z) **{room_name}** szálláshelyen lakó vendégek adatainak módosítása:")
    
    df = st.session_state.guests_df
    idx_list = df[df['Szállás'] == room_name].index.tolist()
    
    if not idx_list:
        st.write("Nincs vendég ebben a szobában.")
        if st.button("Bezárás"):
            st.rerun()
        return
        
    updated_guests = []
    
    for i, idx in enumerate(idx_list):
        guest_data = df.loc[idx]
        st.markdown(f"##### {i+1}. Vendég: {guest_data['Név']}")
        
        col1, col2 = st.columns(2)
        g_name = col1.text_input(f"Név##{idx}", value=guest_data['Név'])
        g_type = col2.selectbox(f"Kategória##{idx}", ["Felnőtt", "Fiatal/Diák", "Gyerek", "Kisgyerek"], index=["Felnőtt", "Fiatal/Diák", "Gyerek", "Kisgyerek"].index(guest_data['Típus']) if guest_data['Típus'] in ["Felnőtt", "Fiatal/Diák", "Gyerek", "Kisgyerek"] else 0)
        
        col3, col4 = st.columns(2)
        active_guests = df[df['Típus'] != 'Külsős']
        occ_counts = active_guests['Szállás'].value_counts().to_dict()
        
        room_options = ["Külsős (Nincs)"]
        room_mapping = {"Külsős (Nincs)": "Külsős (Nincs)"}
        for r in accommodations:
            occ_val = occ_counts.get(r['Név'], 0)
            cap = r['Kapacitás']
            label = f"{r['Név']} ({occ_val}/{cap} fő)"
            room_options.append(label)
            room_mapping[label] = r['Név']
            
        initial_index = 0
        for idx_opt, opt in enumerate(room_options):
            if opt.startswith(guest_data['Szállás']):
                initial_index = idx_opt
                break
                
        g_room_label = col3.selectbox(f"Szálláshely##{idx}", room_options, index=initial_index)
        g_room = room_mapping[g_room_label]
        
        g_nights = col4.slider(f"Éjszakák##{idx}", min_value=1, max_value=5, value=int(guest_data['Éjszakák Száma']))
        
        col5, col6 = st.columns(2)
        g_shared = col5.checkbox(f"Két család egy szobában##{idx}", value=bool(guest_data['Két család egy szobában']))
        g_paid = col6.number_input(f"Befizetett előleg (RON)##{idx}", min_value=0.0, value=float(guest_data['Fizetett előleg']), step=50.0)
        
        col7, col8 = st.columns(2)
        g_status_bool = col7.checkbox(f"Véglegesített foglalás?##{idx}", value=(guest_data['Státusz'] == "Végleges"))
        g_status = "Végleges" if g_status_bool else "Függőben"
        g_note = col8.text_input(f"Megjegyzés##{idx}", value=guest_data['Megjegyzés'])
        
        updated_guests.append({
            'idx': idx,
            'Név': g_name,
            'Típus': g_type,
            'Szállás': g_room,
            'Éjszakák Száma': g_nights,
            'Két család egy szobában': g_shared,
            'Fizetett előleg': g_paid,
            'Státusz': g_status,
            'Megjegyzés': g_note
        })
        st.markdown("---")
        
    if st.button("Mentés és Újraszámolás", type="primary"):
        for ug in updated_guests:
            idx = ug['idx']
            df.loc[idx, 'Név'] = ug['Név']
            df.loc[idx, 'Típus'] = ug['Típus']
            df.loc[idx, 'Szállás'] = ug['Szállás']
            df.loc[idx, 'Éjszakák Száma'] = ug['Éjszakák Száma']
            df.loc[idx, 'Két család egy szobában'] = ug['Két család egy szobában']
            df.loc[idx, 'Fizetett előleg'] = ug['Fizetett előleg']
            df.loc[idx, 'Státusz'] = ug['Státusz']
            df.loc[idx, 'Megjegyzés'] = ug['Megjegyzés']
            
        st.session_state.guests_df = recalculate_dataframe(df)
        save_data(st.session_state.guests_df)
        st.success("Módosítások sikeresen mentve!")
        st.rerun()


# -----------------------------------------------------------------------------
# 4. SIDEBAR - GUEST ACTIONS & FORM
# -----------------------------------------------------------------------------
st.sidebar.title("⛺ Tábor Kezelés")

# Adatbázis letöltése

# Download CSV
csv_data = st.session_state.guests_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Vendéglista letöltése (CSV)",
    data=csv_data,
    file_name="tabor_vendeglista_2026.csv",
    mime="text/csv"
)

st.sidebar.markdown("---")
st.sidebar.header("➕ Új vendég hozzáadása")

# Form inputs for adding a guest
with st.sidebar.form(key='add_guest_form', clear_on_submit=True):
    new_name = st.text_input("Vendég / Csoport neve:", placeholder="Pl. Szabó Család")
    new_type = st.selectbox("Vendég kategória:", ["Felnőtt", "Fiatal/Diák", "Gyerek", "Kisgyerek", "Külsős"])
    
    # Calculate occupancy options to show in selection
    # Compute active guest occupancy by room
    active_guests = st.session_state.guests_df[st.session_state.guests_df['Típus'] != 'Külsős']
    occ_counts = active_guests['Szállás'].value_counts().to_dict()
    
    room_options = []
    room_mapping = {}
    
    # External guest doesn't need accommodation
    room_options.append("Külsős (Nincs)")
    room_mapping["Külsős (Nincs)"] = "Külsős (Nincs)"
    
    for r in accommodations:
        occ = occ_counts.get(r['Név'], 0)
        cap = r['Kapacitás']
        label = f"{r['Név']} ({occ}/{cap} fő)"
        if occ >= cap:
            label += " - MEGTELT"
        room_options.append(label)
        room_mapping[label] = r['Név']
        
    selected_room_label = st.selectbox("Szálláshely választás:", room_options)
    new_room = room_mapping[selected_room_label]
    
    new_nights = st.slider("Eltöltött éjszakák (tábor hossza: 5)", min_value=1, max_value=5, value=5)
    new_shared = st.checkbox("Két család egy szobában (20% felnőtt kedvezmény)", value=False)
    new_paid = st.number_input("Befizetett előleg / összeg (RON):", min_value=0.0, value=0.0, step=50.0)
    new_lunches = st.number_input("Külsős ebédek száma (csak Külsős kategória esetén):", min_value=0, max_value=10, value=0, step=1)
    new_status_bool = st.checkbox("Véglegesített foglalás?", value=True)
    new_status = "Végleges" if new_status_bool else "Függőben"
    new_note = st.text_input("Megjegyzés:", placeholder="Pl. Ételallergia, Szatmári...")
    
    submit_button = st.form_submit_button(label="Regisztrálás")
    
    if submit_button:
        if not new_name.strip():
            st.error("Kérlek adj meg egy nevet!")
        else:
            # Check room capacity constraints (warning but allow if explicitly forced or if we want to block)
            target_room = next((r for r in accommodations if r['Név'] == new_room), None)
            current_occ = occ_counts.get(new_room, 0)
            
            if target_room and current_occ >= target_room['Kapacitás']:
                st.sidebar.error(f"Sikertelen! A(z) {new_room} szálláshely már megtelt ({current_occ}/{target_room['Kapacitás']} fő)!")
            else:
                # Construct new guest row
                new_row = {
                    "Név": new_name,
                    "Típus": new_type,
                    "Szállás": new_room,
                    "Éjszakák Száma": new_nights,
                    "Két család egy szobában": new_shared,
                    "Fizetett előleg": float(new_paid),
                    "Státusz": new_status,
                    "Külsős Ebédek Száma": new_lunches if new_type == 'Külsős' else 0,
                    "Megjegyzés": new_note
                }
                
                # Append and recalculate
                new_df = pd.concat([st.session_state.guests_df, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.guests_df = recalculate_dataframe(new_df)
                save_data(st.session_state.guests_df)
                st.success(f"{new_name} sikeresen regisztrálva!")
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
tab_map, tab_rooms, tab_guests, tab_financials = st.tabs([
    "🗺️ Interaktív Térkép",
    "🏡 Szállásosztó & Szobák",
    "👥 Vendég Nyilvántartás",
    "📊 Elszámolás & Pénzügy"
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
        def save_positions_callback():
            pos_json = st.query_params.get('tabor_pos_data', '')
            if pos_json:
                try:
                    new_pos = json.loads(pos_json)
                    for bid, bdata in new_pos.items():
                        if bid in BUILDING_GROUPS:
                            BUILDING_GROUPS[bid]['x'] = float(bdata['x'])
                            BUILDING_GROUPS[bid]['y'] = float(bdata['y'])
                    
                    with open(_POS_FILE, 'w', encoding='utf-8') as _pf:
                        json.dump({b: {'x': v['x'], 'y': v['y']} for b, v in BUILDING_GROUPS.items()}, _pf, ensure_ascii=False, indent=2)
                    st.session_state['map_success_msg'] = "✅ Pozíciók sikeresen és véglegesen mentve!"
                    st.session_state['map_edit_toggle_drag'] = False
                    st.query_params.clear()
                except Exception as e:
                    st.session_state['map_error_msg'] = f"Hiba a pozíciók mentése során: {e}"

        # Edit-mode toggle
        _edit_mode = st.toggle(
            "🔧 Jelölők pozíciójának szerkesztése",
            value=False,
            key="map_edit_toggle_drag",
            help="Bekapcsolva a köröket egérrel lehet húzni a helyes épületre. Mentés után a pozíciók véglegesen tárolódnak."
        )
        if _edit_mode:
            st.info("✋ **Szerkesztési mód aktív.** Húzd a jelölőket a térképen a helyükre, majd kattints az alábbi gombra!")
            st.button("💾 Végleges Pozíciók Mentése", type="primary", on_click=save_positions_callback)

        # Resolve base URL for form submissions from within the iframe
        try:
            _server_port = int(st.get_option('server.port') or 8501)
        except Exception:
            _server_port = 8501
        _base_url = f'http://localhost:{_server_port}'

        # Load and encode image
        with open("tabor_muhold.jpg", "rb") as _f:
            _img_b64 = base64.b64encode(_f.read()).decode()

        # Build building-level status
        _bstatus = build_building_status(st.session_state.guests_df, accommodations)

        # Render interactive map – taller in edit mode
        _map_html = generate_map_html(_img_b64, _bstatus, edit_mode=_edit_mode, base_url=_base_url)
        st.components.v1.html(_map_html, height=560 if _edit_mode else 520, scrolling=False)

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
        "Kétkamrás Házak (2-Room Houses - 4 fő/szoba)": "Kétkamrás Ház",
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
        - Új sort a táblázat alján lévő `+` gombbal vagy a bal oldali regisztrációs űrlapon adhatsz hozzá.
        - Kiválasztott sorokat a törlés gombbal (kijelölés után Delete) távolíthatsz el.
        - Bármely cella dupla kattintással módosítható. A mentés és újraszámítás automatikus.
    """)
    
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

# Footer info
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 12px;'>"
    "Created with ❤️ by <a href='https://optibase.ro' target='_blank' style='color: gray; text-decoration: underline;'>OptiBase</a>"
    "</div>",
    unsafe_allow_html=True
)
