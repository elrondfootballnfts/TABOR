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
from datetime import datetime
import io
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# -----------------------------------------------------------------------------
# 1. PAGE SETUP & CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="TABOR 2026 - Tábor Kezelő Szoftver",
    page_icon="⛺"
)

# -----------------------------------------------------------------------------
# 1.a PASSWORD PROTECTION (PUBLIC MOBILE MAP BYPASS)
# -----------------------------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

query_params = st.query_params
is_public_mobile_map_view = (
    query_params.get("view") == "map" or
    query_params.get("mobile") == "1" or
    query_params.get("mobile") == "true" or
    st.session_state.get("mobile_mode") is True
)

def check_password():
    if st.session_state.get("password") == "1q2w3e4r":
        st.session_state["authenticated"] = True
        if "password" in st.session_state:
            del st.session_state["password"]
    else:
        st.session_state["authenticated"] = False
        st.error("❌ Helytelen jelszó!")

if not st.session_state['authenticated'] and not is_public_mobile_map_view:
    st.title("⛺ Tábor Kezelő Szoftver")
    st.write("Az alkalmazás eléréséhez kérjük, adja meg a jelszót:")
    st.text_input("Jelszó", type="password", on_change=check_password, key="password")
    st.markdown("---")
    st.info("📱 **Publikus Mobil Térkép Megnyitása Jelszó Nélkül:** [Megnyitás](/?view=map)")
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
    
    # Nagyház Rubin (4 rooms, each 4-person capacity, preferably for Szatmáriak)
    {"Név": "Rubin Room 1", "Típus": "Nagyház Rubin", "Kapacitás": 4, "Megjegyzés": "Preferáltan Szatmáriaknak"},
    {"Név": "Rubin Room 2", "Típus": "Nagyház Rubin", "Kapacitás": 4, "Megjegyzés": "Preferáltan Szatmáriaknak"},
    {"Név": "Rubin Room 3", "Típus": "Nagyház Rubin", "Kapacitás": 4, "Megjegyzés": "Preferáltan Szatmáriaknak"},
    {"Név": "Rubin Room 4", "Típus": "Nagyház Rubin", "Kapacitás": 4, "Megjegyzés": "Preferáltan Szatmáriaknak"},
    
    # Béla Ház (Max 8-person capacity)
    {"Név": "Béla Ház", "Típus": "Béla Ház", "Kapacitás": 8, "Megjegyzés": "Különálló nagy ház (8 fő)"},
    
    # Attila Ház (2x 4-person rooms, max 8 capacity)
    {"Név": "Attila Ház 1", "Típus": "Attila Ház", "Kapacitás": 4, "Megjegyzés": "Attila Ház 1. szoba (4 fő)"},
    {"Név": "Attila Ház 2", "Típus": "Attila Ház", "Kapacitás": 4, "Megjegyzés": "Attila Ház 2. szoba (4 fő)"},
    
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
    {"Név": "Ruzsa János", "Típus": "Felnőtt", "Szállás": "Attila Ház 1", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 500.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Ruzsáék előfoglalás"},
    {"Név": "Ruzsa Mária", "Típus": "Felnőtt", "Szállás": "Attila Ház 1", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 500.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Ruzsáék előfoglalás"},
    {"Név": "Ruzsa Péter", "Típus": "Fiatal/Diák", "Szállás": "Attila Ház 1", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 400.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Ruzsáék előfoglalás"},
    {"Név": "Ruzsa Kata", "Típus": "Gyerek", "Szállás": "Attila Ház 1", "Éjszakák Száma": 5, "Két család egy szobában": False, "Fizetett előleg": 300.0, "Státusz": "Végleges", "Külsős Ebédek Száma": 0, "Megjegyzés": "Ruzsáék előfoglalás"},
    
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
    '1':  {'name': 'Vadász',          'label': '1',  'x': 28.8, 'y': 29.5, 'rooms': ['Vadász Room 1', 'Vadász Room 2']},
    '2':  {'name': 'Füzi',            'label': '2',  'x': 34.0, 'y': 28.2, 'rooms': ['Füzi Room 1', 'Füzi Room 2']},
    '3':  {'name': 'Fa',              'label': '3',  'x': 38.8, 'y': 26.2, 'rooms': ['Fa Room 1', 'Fa Room 2']},
    '4':  {'name': 'Nagyház (Rubin)', 'label': '4',  'x': 45.5, 'y': 19.5, 'rooms': ['Rubin Room 1', 'Rubin Room 2', 'Rubin Room 3', 'Rubin Room 4']},
    '5':  {'name': 'Aurum',           'label': '5',  'x': 53.0, 'y': 21.5, 'rooms': ['Aurum Room 1', 'Aurum Room 2']},
    '6':  {'name': 'Nóra',            'label': '6',  'x': 58.6, 'y': 19.5, 'rooms': ['Nóra Room 1', 'Nóra Room 2']},
    '7':  {'name': 'Ágnes',           'label': '7',  'x': 64.8, 'y': 18.0, 'rooms': ['Ágnes Room 1', 'Ágnes Room 2']},
    '8':  {'name': 'Béla Ház',        'label': '8',  'x': 70.5, 'y': 16.5, 'rooms': ['Béla Ház']},
    '9':  {'name': 'VIP Ház',         'label': '9',  'x': 5.8,  'y': 44.5, 'rooms': ['VIP 1','VIP 2','VIP 3','VIP 4','VIP 5','VIP 6','VIP 7','VIP Fsz 1','VIP Fsz 2']},
    '10': {'name': 'Attila Ház',      'label': '10', 'x': 82.8, 'y': 43.5, 'rooms': ['Attila Ház 1', 'Attila Ház 2']},
    'A':  {'name': 'Sátor A',         'label': 'A',  'x': 19.5, 'y': 29.5, 'rooms': ['Sátor A']},
    'B':  {'name': 'Sátor B',         'label': 'B',  'x': 16.0, 'y': 35.0, 'rooms': ['Sátor B']},
    'C':  {'name': 'Sátor C',         'label': 'C',  'x': 11.0, 'y': 39.0, 'rooms': ['Sátor C']},
    'D':  {'name': 'Sátor D',         'label': 'D',  'x': 13.0, 'y': 45.5, 'rooms': ['Sátor D']},
    'E':  {'name': 'Sátor E',         'label': 'E',  'x': 21.5, 'y': 42.5, 'rooms': ['Sátor E']},
    'F':  {'name': 'Sátor F',         'label': 'F',  'x': 17.0, 'y': 50.5, 'rooms': ['Sátor F']},
    'G':  {'name': 'Sátor G',         'label': 'G',  'x': 12.8, 'y': 55.8, 'rooms': ['Sátor G']},
    'H':  {'name': 'Sátor H',         'label': 'H',  'x': 22.0, 'y': 53.0, 'rooms': ['Sátor H']},
    'K':  {'name': 'Külsős Vendégek', 'label': '👤', 'x': 31.0, 'y': 7.5,  'rooms': ['Külsős (Nincs)', 'Külsős (Sátor)', 'Külsős (Lakókocsi)']},
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

try:
    _gs_pos = load_positions_from_gsheets()
    if _gs_pos:
        for _bid, _pos in _gs_pos.items():
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
CAT_DISPLAY_MAP = {
    "Felnőtt": "Felnőtt (alapár)",
    "Fiatal/Diák": "Fiatal/Diák (48% kedvezmény)",
    "Gyerek": "Gyerek (68% kedvezmény)",
    "Kisgyerek": "Kisgyerek (100% kedvezmény)",
    "Külsős": "Külsős"
}
CAT_REVERSE_MAP = {v: k for k, v in CAT_DISPLAY_MAP.items()}

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
        rate = 70.0 if shared else 125.0
    elif guest_type == 'Fiatal/Diák':
        rate = 65.0
    elif guest_type == 'Gyerek':
        rate = 40.0
    elif guest_type == 'Kisgyerek':
        rate = 0.0
    else:
        rate = 125.0
        
    if is_tent:
        rate *= 0.80
        
    return float(rate * nights)

def calculate_meals_cost(meals_str, guest_type, child_menu=False):
    if guest_type == 'Kisgyerek':
        return 0.0
    meals_str_clean = str(meals_str).strip()
    if meals_str_clean in ['NONE', 'none', 'Nincs', 'nincs']:
        return 0.0
    all_meals = ['T_D', 'W_B', 'W_L', 'W_D', 'Th_B', 'Th_L', 'Th_D', 'F_B', 'F_L', 'F_D', 'S_B', 'S_L', 'S_D', 'Su_BD', 'Su_L']
    if not meals_str or meals_str_clean == 'ALL' or meals_str_clean == 'nan':
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
        elif m in ['W_B', 'Th_B', 'F_B', 'S_B']:
            total += 20.0 if is_child else 30.0
        elif m in ['W_D', 'Th_D', 'F_D', 'S_D']:
            total += 30.0 if is_child else 40.0
        elif m in ['W_L', 'Th_L', 'F_L', 'S_L', 'Su_L']:
            total += 35.0 if is_child else 55.0
            
    return float(total)

def render_meal_badges(meals_str):
    meals_str_clean = str(meals_str).strip()
    if meals_str_clean in ['NONE', 'none', 'Nincs', 'nincs']:
        return '<span style="font-size: 0.75em; background-color: #ef5350; color: #ffffff; padding: 2px 5px; border-radius: 4px; font-weight: bold; display: inline-block;">🚫 Nincs étkezés</span>'
    if not meals_str or meals_str_clean == 'ALL' or meals_str_clean == 'nan':
        return '<span style="font-size: 0.75em; background-color: #2e7d32; color: #ffffff; padding: 2px 5px; border-radius: 4px; font-weight: bold; display: inline-block;">🍽️ Mindegyik étkezés</span>'
    
    meal_options = {
        'T_D':    {"label": "Ke - Vacsora",        "color": "#ef5350", "type": "vacsora", "emoji": "🌆"},
        'W_B':    {"label": "Sze - Reggeli",       "color": "#ff9800", "type": "reggeli", "emoji": "🥣"},
        'W_BD':   {"label": "Sze - Regg+Vac",      "color": "#ff9800", "type": "reggelivacsora", "emoji": "🥣"},
        'W_L':    {"label": "Sze - Ebéd",          "color": "#ffb300", "type": "ebed", "emoji": "🍲"},
        'W_D':    {"label": "Sze - Vacsora",       "color": "#f57c00", "type": "vacsora", "emoji": "🌆"},
        'Th_B':   {"label": "Csü - Reggeli",       "color": "#4caf50", "type": "reggeli", "emoji": "🥣"},
        'Th_BD':  {"label": "Csü - Regg+Vac",      "color": "#4caf50", "type": "reggelivacsora", "emoji": "🥣"},
        'Th_L':   {"label": "Csü - Ebéd",          "color": "#66bb6a", "type": "ebed", "emoji": "🍲"},
        'Th_D':   {"label": "Csü - Vacsora",       "color": "#388e3c", "type": "vacsora", "emoji": "🌆"},
        'F_B':    {"label": "Pé - Reggeli",        "color": "#2196f3", "type": "reggeli", "emoji": "🥣"},
        'F_BD':   {"label": "Pé - Regg+Vac",       "color": "#2196f3", "type": "reggelivacsora", "emoji": "🥣"},
        'F_L':    {"label": "Pé - Ebéd",           "color": "#29b6f6", "type": "ebed", "emoji": "🍲"},
        'F_D':    {"label": "Pé - Vacsora",        "color": "#1976d2", "type": "vacsora", "emoji": "🌆"},
        'S_B':    {"label": "Szo - Reggeli",       "color": "#9c27b0", "type": "reggeli", "emoji": "🥣"},
        'S_BD':   {"label": "Szo - Regg+Vac",      "color": "#9c27b0", "type": "reggelivacsora", "emoji": "🥣"},
        'S_L':    {"label": "Szo - Ebéd",          "color": "#ba68c8", "type": "ebed", "emoji": "🍲"},
        'S_D':    {"label": "Szo - Vacsora",       "color": "#7b1fa2", "type": "vacsora", "emoji": "🌆"},
        'Su_BD':  {"label": "Vas - Reggeli",       "color": "#795548", "type": "reggeli", "emoji": "🥣"},
        'Su_L':   {"label": "Vas - Ebéd",          "color": "#8d6e63", "type": "ebed", "emoji": "🍲"}
    }
    
    active_meals = [m.strip() for m in str(meals_str).split(',') if m.strip()]
    badges = []
    for m in active_meals:
        if m in meal_options:
            opt = meal_options[m]
            if opt['type'] == 'ebed':
                bg_style = f"background-color: {opt['color']}; color: #ffffff; border: 1.2px solid {opt['color']};"
            else:
                bg_style = f"background-color: rgba(255,255,255,0.05); color: {opt['color']}; border: 1.2px solid {opt['color']};"
                
            badges.append(f'<span style="font-size: 0.72em; padding: 1.5px 5px; border-radius: 4px; margin-right: 4px; margin-bottom: 4px; display: inline-block; font-weight: bold; {bg_style}">{opt["emoji"]} {opt["label"]}</span>')
            
    return '<div style="display: flex; flex-wrap: wrap; margin-top: 3px;">' + "".join(badges) + '</div>'

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
    status = row.get('Státusz')
    if status is not None and str(status).strip() not in ['', 'nan']:
        return str(status).strip()
    nights = int(row.get('Éjszakák Száma', 5))
    guest_type = row.get('Típus', 'Felnőtt')
    if guest_type != 'Külsős' and nights < 5:
        return 'Függőben'
    return 'Végleges'

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
    meals_str_clean = str(meals_str).strip()
    if meals_str_clean in ['NONE', 'none', 'Nincs', 'nincs']:
        return 0.0
    all_meals = ['T_D', 'W_B', 'W_L', 'W_D', 'Th_B', 'Th_L', 'Th_D', 'F_B', 'F_L', 'F_D', 'S_B', 'S_L', 'S_D', 'Su_BD', 'Su_L']
    if not meals_str or meals_str_clean == 'ALL' or meals_str_clean == 'nan':
        active_meals = all_meals
    else:
        active_meals = [m.strip() for m in str(meals_str).split(',') if m.strip()]
        
    is_child = (guest_type == 'Gyerek') or bool(row.get('Gyermekmenü', False))
    total = 0.0
    for m in active_meals:
        if m == 'T_D':
            total += 25.0 if is_child else 35.0
        elif m == 'Su_BD':
            total += 15.0 if is_child else 25.0
        elif m in ['W_BD', 'Th_BD', 'F_BD', 'S_BD']:
            total += 40.0 if is_child else 60.0
        elif m in ['W_B', 'Th_B', 'F_B', 'S_B']:
            total += 15.0 if is_child else 25.0
        elif m in ['W_D', 'Th_D', 'F_D', 'S_D']:
            total += 25.0 if is_child else 35.0
    return float(total)

def calculate_tribel_lunch(row):
    guest_type = row.get('Típus', 'Felnőtt')
    if guest_type == 'Kisgyerek':
        return 0.0
    meals_str = row.get('Étkezések', 'ALL')
    meals_str_clean = str(meals_str).strip()
    if meals_str_clean in ['NONE', 'none', 'Nincs', 'nincs']:
        return 0.0
    all_meals = ['T_D', 'W_B', 'W_L', 'W_D', 'Th_B', 'Th_L', 'Th_D', 'F_B', 'F_L', 'F_D', 'S_B', 'S_L', 'S_D', 'Su_BD', 'Su_L']
    if not meals_str or meals_str_clean == 'ALL' or meals_str_clean == 'nan':
        active_meals = all_meals
    else:
        active_meals = [m.strip() for m in str(meals_str).split(',') if m.strip()]
        
    is_child = (guest_type == 'Gyerek') or bool(row.get('Gyermekmenü', False))
    total = 0.0
    for m in active_meals:
        if m in ['W_L', 'Th_L', 'F_L', 'S_L', 'Su_L']:
            total += 30.0 if is_child else 50.0
    return float(total)

def parse_payments_history(row):
    """Returns a list of payment transaction dicts for a guest."""
    raw_history = str(row.get('Befizetések JSON', '') or '').strip()
    if raw_history and raw_history not in ['nan', 'None', '[]', '']:
        try:
            parsed = json.loads(raw_history)
            if isinstance(parsed, list) and len(parsed) > 0:
                for p in parsed:
                    if str(p.get('date', '')) in ['nan', 'None']:
                        p['date'] = ""
                return parsed
        except Exception:
            pass
            
    # Fallback to single payment legacy values if present
    paid = float(row.get('Fizetett előleg', 0.0) or 0.0)
    if paid > 0:
        method = str(row.get('Fizetési Mód', 'Készpénz') or 'Készpénz').strip()
        if method in ['nan', 'None', '']:
            method = 'Készpénz'
        date_val = str(row.get('Befizetés Dátuma', '') or '').strip()
        if date_val in ['nan', 'None']:
            date_val = ""
        return [{'amount': paid, 'method': method, 'date': date_val, 'note': 'Első befizetés'}]
    return []

def serialize_payments_history(transactions):
    """Serializes a list of payment transaction dicts to a JSON string."""
    clean_txs = []
    for tx in transactions:
        clean_txs.append({
            'amount': float(tx.get('amount', 0.0)),
            'method': str(tx.get('method', 'Utalás')),
            'date': str(tx.get('date', '')),
            'note': str(tx.get('note', ''))
        })
    return json.dumps(clean_txs, ensure_ascii=False)

def get_meal_summary_text(row_or_str):
    """Helper to return a clean, human-readable summary of guest meals in Hungarian."""
    if isinstance(row_or_str, str):
        meals_val = row_or_str.strip()
        t = 'Felnőtt'
        name = ''
        note = ''
        row = {}
    elif isinstance(row_or_str, dict) or hasattr(row_or_str, 'get'):
        row = row_or_str
        t = str(row.get('Típus', ''))
        name = str(row.get('Név', ''))
        note = str(row.get('Megjegyzés', ''))
        meals_val = str(row.get('Étkezések', 'ALL')).strip()
    else:
        return 'Teljes ellátás'
        
    if t == 'Külsős':
        r = int(row.get('Külsős Reggelik Száma', 0) or 0)
        e = int(row.get('Külsős Ebédek Száma', 0) or 0)
        v = int(row.get('Külsős Vacsorák Száma', 0) or 0)
        parts = []
        if r > 0: parts.append(f'Reggeli: {r}')
        if e > 0: parts.append(f'Ebéd: {e}')
        if v > 0: parts.append(f'Vacsora: {v}')
        return 'Külsős (' + ', '.join(parts) + ')' if parts else 'Külsős (Nincs étkezés)'
        
    if 'Kisgyerek' in t:
        return 'Kisgyerek (Ingyenes)'
        
    if meals_val.upper() in ['NONE', 'NINCS', 'SAJÁT', 'SAJAT', '0'] or '(S)' in name or 'saját' in note.lower() or 'nincs étkezés' in note.lower():
        return 'Nincs étkezés (Saját étel)'
        
    if not meals_val or meals_val.upper() in ['ALL', 'NAN', '']:
        return 'Teljes ellátás'
        
    active_codes = [m.strip() for m in meals_val.split(',') if m.strip()]
    if not active_codes:
        return 'Nincs étkezés'
        
    legacy_all = {'T_D', 'W_BD', 'W_L', 'Th_BD', 'Th_L', 'F_BD', 'F_L', 'S_BD', 'S_L', 'Su_BD', 'Su_L'}
    new_all = {'T_D', 'W_B', 'W_L', 'W_D', 'Th_B', 'Th_L', 'Th_D', 'F_B', 'F_L', 'F_D', 'S_B', 'S_L', 'S_D', 'Su_BD', 'Su_L'}
    
    active_set = set(active_codes)
    if active_set >= legacy_all or active_set >= new_all or len(active_codes) >= 15:
        return 'Teljes ellátás'
        
    has_b_or_d = any('_B' in m or '_D' in m or '_BD' in m or 'T_D' in m for m in active_codes)
    has_l = any('_L' in m for m in active_codes)
    num_l = len([m for m in active_codes if '_L' in m])
    
    if has_l and not has_b_or_d:
        return f'Csak Ebéd ({num_l} nap)'
        
    if has_b_or_d and not has_l:
        if ('W_D' in active_codes or 'W_BD' in active_codes) and 'W_B' not in active_codes and 'T_D' not in active_codes:
            return 'Szerda vacsorától (Reggeli & Vacsora)'
        return 'Csak Reggeli & Vacsora'
        
    if ('W_D' in active_codes or 'W_BD' in active_codes) and 'W_B' not in active_codes and 'T_D' not in active_codes:
        if has_l:
            return 'Szerda vacsorától (Teljes ellátás)'
        return 'Szerda vacsorától'
        
    meal_names = {
        'T_D': 'Kedd vacsora',
        'W_B': 'Sze reggeli', 'W_BD': 'Sze regg+vac', 'W_L': 'Sze ebéd', 'W_D': 'Sze vacsora',
        'Th_B': 'Csü reggeli', 'Th_BD': 'Csü regg+vac', 'Th_L': 'Csü ebéd', 'Th_D': 'Csü vacsora',
        'F_B': 'Pé reggeli', 'F_BD': 'Pé regg+vac', 'F_L': 'Pé ebéd', 'F_D': 'Pé vacsora',
        'S_B': 'Szo reggeli', 'S_BD': 'Szo regg+vac', 'S_L': 'Szo ebéd', 'S_D': 'Szo vacsora',
        'Su_BD': 'Vas reggeli', 'Su_L': 'Vas ebéd'
    }
    
    if len(active_codes) <= 4:
        translated = [meal_names.get(c, c) for c in active_codes]
        return 'Kért étkezések: ' + ', '.join(translated)
        
    return f'Egyedi kért étkezések ({len(active_codes)} alkalom)'

def recalculate_dataframe(df):
    """Calculates all dynamic columns for the entire guest DataFrame."""
    if df.empty:
        return pd.DataFrame(columns=[
            'Név', 'Típus', 'Szállás', 'Éjszakák Száma', 
            'Két család egy szobában', 'Kedvezmény (%)', 'Fizetett előleg', 'Befizetés Dátuma', 'Fizetési Mód', 'Befizetések JSON', 'Státusz', 
            'Külsős Reggelik Száma', 'Külsős Ebédek Száma', 'Külsős Vacsorák Száma',
            'Megjegyzés', 'Étkezések', 'Gyermekmenü', 'Összköltség', 
            'Előleg Státusz', 'Bedő Laci Kaja', 'Tribel Ebéd'
        ])
    
    df['Szállás'] = df['Szállás'].replace({'Attila Ház': 'Attila Ház 1'})
    df['Éjszakák Száma'] = df['Éjszakák Száma'].fillna(5).astype(int)
    if 'Befizetések JSON' not in df.columns:
        df['Befizetések JSON'] = '[]'
        
    def sync_payment_totals(row):
        txs = parse_payments_history(row)
        if txs:
            tot = sum(float(t['amount']) for t in txs)
            latest_date = txs[-1]['date'] if txs[-1]['date'] else ''
            latest_method = txs[-1]['method'] if txs[-1]['method'] else 'Utalás'
            json_str = serialize_payments_history(txs)
            return pd.Series([tot, latest_date, latest_method, json_str])
        else:
            return pd.Series([0.0, '', 'Utalás', '[]'])

    df[['Fizetett előleg', 'Befizetés Dátuma', 'Fizetési Mód', 'Befizetések JSON']] = df.apply(sync_payment_totals, axis=1)
    df['Két család egy szobában'] = df['Két család egy szobában'].fillna(False).astype(bool)
    df['Gyermekmenü'] = df.get('Gyermekmenü', False)
    df['Gyermekmenü'] = df['Gyermekmenü'].fillna(False).astype(bool)
    df['Kedvezmény (%)'] = df.get('Kedvezmény (%)', 0.0)
    df['Kedvezmény (%)'] = pd.to_numeric(df['Kedvezmény (%)'], errors='coerce').fillna(0.0).astype(float)
    df['Étkezések'] = df.get('Étkezések', 'ALL')
    df['Étkezések'] = df['Étkezések'].fillna('ALL').astype(str)
    
    def count_breakfasts(row):
        m_str = str(row.get('Étkezések', 'ALL')).strip()
        if m_str in ['NONE', 'none', 'Nincs', 'nincs']:
            return 0
        if m_str == 'ALL':
            return 5
        meals = [m.strip() for m in m_str.split(',') if m.strip()]
        return sum(1 for m in meals if m in ['W_BD', 'Th_BD', 'F_BD', 'S_BD', 'Su_BD'])

    def count_lunches(row):
        m_str = str(row.get('Étkezések', 'ALL')).strip()
        if m_str in ['NONE', 'none', 'Nincs', 'nincs']:
            return 0
        if m_str == 'ALL':
            return 5
        meals = [m.strip() for m in m_str.split(',') if m.strip()]
        return sum(1 for m in meals if m in ['W_L', 'Th_L', 'F_L', 'S_L', 'Su_L'])

    def count_dinners(row):
        m_str = str(row.get('Étkezések', 'ALL')).strip()
        if m_str in ['NONE', 'none', 'Nincs', 'nincs']:
            return 0
        if m_str == 'ALL':
            return 5
        meals = [m.strip() for m in m_str.split(',') if m.strip()]
        return sum(1 for m in meals if m in ['T_D', 'W_BD', 'Th_BD', 'F_BD', 'S_BD'])

    df['Külsős Reggelik Száma'] = df.apply(lambda r: count_breakfasts(r) if r['Típus'] == 'Külsős' else 0, axis=1)
    df['Külsős Ebédek Száma'] = df.apply(lambda r: count_lunches(r) if r['Típus'] == 'Külsős' else 0, axis=1)
    df['Külsős Vacsorák Száma'] = df.apply(lambda r: count_dinners(r) if r['Típus'] == 'Külsős' else 0, axis=1)
    
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
def save_positions_to_gsheets(positions_dict):
    try:
        client = get_gspread_client()
        if client:
            sheet_name = st.secrets.get("google_sheet_name", "Tabor_Vendeglista")
            sh = client.open(sheet_name)
            try:
                ws = sh.worksheet("Poziciok")
            except Exception:
                ws = sh.add_worksheet(title="Poziciok", rows="30", cols="5")
            
            data = [["bid", "x", "y"]]
            for bid, p in positions_dict.items():
                data.append([str(bid), str(p['x']), str(p['y'])])
            ws.clear()
            ws.update('A1', data)
    except Exception:
        pass

def load_positions_from_gsheets():
    try:
        client = get_gspread_client()
        if client:
            sheet_name = st.secrets.get("google_sheet_name", "Tabor_Vendeglista")
            sh = client.open(sheet_name)
            try:
                ws = sh.worksheet("Poziciok")
                rows = ws.get_all_values()
                if len(rows) > 1:
                    pos_dict = {}
                    for r in rows[1:]:
                        if len(r) >= 3:
                            pos_dict[r[0]] = {'x': float(r[1]), 'y': float(r[2])}
                    return pos_dict
            except Exception:
                pass
    except Exception:
        pass
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
                    if 'Külsős Reggelik Száma' in df.columns:
                        df['Külsős Reggelik Száma'] = pd.to_numeric(df['Külsős Reggelik Száma'], errors='coerce').fillna(0).astype(int)
                    if 'Külsős Ebédek Száma' in df.columns:
                        df['Külsős Ebédek Száma'] = pd.to_numeric(df['Külsős Ebédek Száma'], errors='coerce').fillna(0).astype(int)
                    if 'Külsős Vacsorák Száma' in df.columns:
                        df['Külsős Vacsorák Száma'] = pd.to_numeric(df['Külsős Vacsorák Száma'], errors='coerce').fillna(0).astype(int)
                    
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
            df['Külsős Reggelik Száma'] = df['Külsős Reggelik Száma'].fillna(0).astype(int) if 'Külsős Reggelik Száma' in df.columns else 0
            df['Külsős Ebédek Száma'] = df['Külsős Ebédek Száma'].fillna(0).astype(int) if 'Külsős Ebédek Száma' in df.columns else 0
            df['Külsős Vacsorák Száma'] = df['Külsős Vacsorák Száma'].fillna(0).astype(int) if 'Külsős Vacsorák Száma' in df.columns else 0
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
if 'guests_df' not in st.session_state or not all(col in st.session_state.guests_df.columns for col in ['Külsős Reggelik Száma', 'Külsős Vacsorák Száma']):
    st.session_state.guests_df = load_data()
if 'active_building' not in st.session_state:
    st.session_state['active_building'] = None
if 'admin_unlocked' not in st.session_state:
    st.session_state['admin_unlocked'] = False


# -----------------------------------------------------------------------------
# 3b. PDF GENERATION HELPER
# -----------------------------------------------------------------------------
def generate_guest_pdf(df):
    """Generál egy részletes PDF vendégnévsort házakra és szobákra bontva, ellátási kérésekkel (pénzügyi adatok, konyhai összesítő és megjegyzések nélkül)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=25,
        rightMargin=25,
        topMargin=25,
        bottomMargin=25
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Title'], fontSize=16, leading=20, textColor=colors.HexColor('#0f172a'), alignment=0)
    sub_style = ParagraphStyle('DocSub', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#475569'))
    bldg_title_style = ParagraphStyle('BldgTitle', parent=styles['Heading2'], fontSize=11, leading=14, textColor=colors.HexColor('#1e3a8a'), spaceBefore=8, spaceAfter=4, keepWithNext=True)
    
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor('#0f172a'))
    cell_bold = ParagraphStyle('CellB', parent=cell_style, fontName='Helvetica-Bold')
    cell_hdr = ParagraphStyle('CellHdr', parent=cell_style, fontName='Helvetica-Bold', textColor=colors.white)

    # Accent cleaning function for ReportLab Helvetica compatibility
    def c(text):
        if not text:
            return ""
        s = str(text)
        rep = {'ő': 'ö', 'Ő': 'Ö', 'ű': 'ü', 'Ű': 'Ü'}
        for k, v in rep.items():
            s = s.replace(k, v)
        return s

    story = []
    
    # Header Metadata
    story.append(Paragraph(c('Nyári Tábor 2026 — Vendégnévsor & Ellátási Nyilvántartás'), title_style))
    from datetime import datetime
    today_str = datetime.now().strftime('%Y.%m.%d.')
    total_count = len(df)
    internal_count = len(df[df['Típus'] != 'Külsős'])
    external_count = len(df[df['Típus'] == 'Külsős'])
    
    sub_text = c(f'Kiállítva: {today_str} | Összes résztvevő: <b>{total_count} fő</b> (Belső szálláson: <b>{internal_count} fő</b> | Külsős vendég: <b>{external_count} fő</b>)')
    story.append(Paragraph(sub_text, sub_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#cbd5e1'), spaceBefore=2, spaceAfter=6))

    def get_meal_desc(row):
        t = str(row.get('Típus', ''))
        name = str(row.get('Név', ''))
        note = str(row.get('Megjegyzés', ''))
        meals_val = str(row.get('Étkezések', 'ALL')).strip()
        
        # 1. Külsős vendég
        if t == 'Külsős':
            r = int(row.get('Külsős Reggelik Száma', 0))
            e = int(row.get('Külsős Ebédek Száma', 0))
            v = int(row.get('Külsős Vacsorák Száma', 0))
            parts = []
            if r > 0: parts.append(f'Reggeli: {r} nap')
            if e > 0: parts.append(f'Ebéd: {e} nap')
            if v > 0: parts.append(f'Vacsora: {v} nap')
            if parts:
                return c('Külsős étkezés (' + ', '.join(parts) + ')')
            else:
                return c('Külsős (Csak belépő / Nincs étkezés)')
                
        # 2. Kisgyerek
        if 'Kisgyerek' in t:
            return c('Kisgyerek (Ingyenes szállás és ellátás)')
            
        # 3. Explicit No-Meal detection (Saját étel / NONE)
        has_no_meal_tag = (
            meals_val.upper() in ['NONE', 'NINCS', 'SAJÁT', 'SAJAT', '0'] or
            '(S)' in name or '(s)' in name or
            'saját' in note.lower() or 'sajat' in note.lower() or
            'nincs étkezés' in note.lower() or 'nincs etkezes' in note.lower() or
            'étel nélkül' in note.lower() or 'etel nelkul' in note.lower() or
            'saját' in meals_val.lower() or 'sajat' in meals_val.lower()
        )
        if has_no_meal_tag:
            return c('Nincs étkezés (Saját étel)')
            
        # 4. Explicit Lunch-Only (Csak ebéd) detection from note/name/meals_val
        is_only_lunch = (
            'csak ebéd' in note.lower() or 'csak ebed' in note.lower() or
            'ebédet kér' in note.lower() or 'ebedet ker' in note.lower() or
            'ebéd' in note.lower() or 'ebed' in note.lower() or
            'csak ebéd' in meals_val.lower() or 'csak ebed' in meals_val.lower() or
            'csak ebéd' in name.lower() or 'csak ebed' in name.lower()
        )
        
        # 5. Parse meals_val codes if custom codes are present
        all_meal_codes = ['T_D', 'W_BD', 'W_L', 'Th_BD', 'Th_L', 'F_BD', 'F_L', 'S_BD', 'S_L', 'Su_BD', 'Su_L']
        if meals_val and meals_val.upper() not in ['ALL', 'NAN', 'NONE', 'NINCS', '']:
            active_codes = [m.strip() for m in meals_val.split(',') if m.strip()]
            if active_codes:
                has_bd = any('_BD' in m or 'T_D' in m for m in active_codes)
                has_l = any('_L' in m for m in active_codes)
                if has_l and not has_bd:
                    num_l = len([m for m in active_codes if '_L' in m])
                    return c(f'Csak ebéd ({num_l} nap)')
                elif has_bd and not has_l:
                    return c('Reggeli & Vacsora (Ebéd nélkül)')
                elif len(active_codes) < len(all_meal_codes):
                    return c('Kért étkezések (' + f'{len(active_codes)} étkezés' + ')')
                    
        if is_only_lunch and 'teljes' not in note.lower():
            child_menu = bool(row.get('Gyermekmenü', False))
            menu_str = c(' — Gyermekmenü') if child_menu else ''
            return c(f'Csak Ebéd (Ebéd a táborban){menu_str}')

        # 6. Default full board for internal guests
        child_menu = bool(row.get('Gyermekmenü', False))
        menu_str = c(' — Gyermekmenü') if child_menu else ''
        return c(f'Teljes ellátás (Reggeli, Ebéd, Vacsora){menu_str}')

    # Headers without Megjegyzés column
    headers = [
        Paragraph(c('Szállás / Szoba'), cell_hdr),
        Paragraph(c('Vendég Neve'), cell_hdr),
        Paragraph(c('Vendég Típusa'), cell_hdr),
        Paragraph(c('Éjszakák'), cell_hdr),
        Paragraph(c('Igényelt Ellátás'), cell_hdr)
    ]
    
    col_widths = [150, 180, 120, 80, 250]

    def natural_sort_key(s):
        import re
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

    def get_building_category(room_name):
        rn = str(room_name)
        if 'VIP' in rn: return 'VIP Ház'
        if 'Rubin' in rn: return 'Nagyház (Rubin)'
        if 'Attila' in rn: return 'Attila Ház'
        if 'Béla' in rn: return 'Béla Ház'
        if 'Vadász' in rn: return 'Vadász Ház'
        if 'Füzi' in rn: return 'Füzi Ház'
        if 'Fa' in rn: return 'Fa Ház'
        if 'Aurum' in rn: return 'Aurum Ház'
        if 'Nóra' in rn: return 'Nóra Ház'
        if 'Ágnes' in rn: return 'Ágnes Ház'
        if 'Sátor' in rn: return 'Sátrak'
        if 'Külsős' in rn: return 'Külsős Vendégek'
        return 'Egyéb'

    df_copy = df.copy()
    df_copy['Building'] = df_copy['Szállás'].apply(get_building_category)

    bldg_order = ['Vadász Ház', 'Füzi Ház', 'Fa Ház', 'Nagyház (Rubin)', 'Aurum Ház', 'Nóra Ház', 'Ágnes Ház', 'Béla Ház', 'VIP Ház', 'Attila Ház', 'Sátrak', 'Külsős Vendégek', 'Egyéb']
    
    grouped_bldgs = df_copy.groupby('Building')
    
    for bldg in bldg_order:
        if bldg not in grouped_bldgs.groups:
            continue
        group_df = grouped_bldgs.get_group(bldg)
        group_df = group_df.sort_values(by='Szállás', key=lambda col: col.map(natural_sort_key))
        
        bldg_count = len(group_df)
        bldg_para = Paragraph(c(f'<b>■ {bldg}</b> ({bldg_count} fő)'), bldg_title_style)
        
        table_data = [headers]
        for idx, row in group_df.iterrows():
            room_str = c(str(row['Szállás']))
            name_str = c(str(row['Név']))
            type_str = c(str(row['Típus']))
            nights_str = c(f"{int(row['Éjszakák Száma'])} éj")
            meal_str = get_meal_desc(row)
            
            table_data.append([
                Paragraph(room_str, cell_bold),
                Paragraph(name_str, cell_style),
                Paragraph(type_str, cell_style),
                Paragraph(nights_str, cell_style),
                Paragraph(meal_str, cell_style)
            ])
            
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        
        story.append(KeepTogether([bldg_para, t]))
        story.append(Spacer(1, 6))

    doc.build(story)
    return buffer.getvalue()


# -----------------------------------------------------------------------------
# 3c. MAP HELPER FUNCTIONS
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
    
    all_camp_rooms = [r['Név'] for r in accommodations] + ["Külsős (Nincs)", "Külsős (Sátor)", "Külsős (Lakókocsi)"]
    cap_lookup = {r['Név']: r['Kapacitás'] for r in accommodations}
    
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
                    col_g_info, col_g_edit, col_g_move = st.columns([4.2, 0.9, 0.9])
                    
                    paid = g.get('Fizetett előleg', 0.0)
                    total = g.get('Összköltség', 0.0)
                    status_text = "🟢 Véglegesítve" if g['Státusz'] == "Végleges" else "🟡 Függőben"
                    status_color = "#4caf50" if g['Státusz'] == "Végleges" else "#ffb300"
                    
                    menu_badge = ""
                    if g.get('Gyermekmenü', False):
                        menu_badge = '<span style="font-size: 0.7em; background-color: #0288d1; color: #ffffff; padding: 1.5px 4px; border-radius: 4px; margin-left: 5px; font-weight: bold;">👶 Gyermekmenü</span>'
                    
                    pm_val = g.get('Fizetési Mód', 'Utalás')
                    pay_badge = ""
                    if paid > 0:
                        if pm_val == 'Vakációs Voucher':
                            pay_badge = '<span style="font-size: 0.7em; background-color: #7e22ce; color: #ffffff; padding: 1.5px 4px; border-radius: 4px; margin-left: 5px; font-weight: bold;">🎟️ Voucher</span>'
                        elif pm_val == 'Készpénz':
                            pay_badge = '<span style="font-size: 0.7em; background-color: #15803d; color: #ffffff; padding: 1.5px 4px; border-radius: 4px; margin-left: 5px; font-weight: bold;">💵 Készpénz</span>'
                        else:
                            pay_badge = '<span style="font-size: 0.7em; background-color: #1e3a8a; color: #ffffff; padding: 1.5px 4px; border-radius: 4px; margin-left: 5px; font-weight: bold;">🏦 Utalás</span>'
                    
                    room_val = g.get('Szállás', 'Külsős (Nincs)')
                    label_map = {
                        'Külsős (Nincs)': "🍽️ Csak Étkezés",
                        'Külsős (Sátor)': "⛺ Sátorhely",
                        'Külsős (Lakókocsi)': "🚐 Lakókocsi hely"
                    }
                    acc_label = label_map.get(room_val, room_val)
                    acc_badge = f'<span style="font-size: 0.7em; background-color: #2196f3; color: #ffffff; padding: 1.5px 4px; border-radius: 4px; margin-left: 5px; font-weight: bold;">{acc_label}</span>'
                    
                    note_html = ""
                    if g.get('Megjegyzés'):
                        note_html = f'<div style="font-size: 0.8em; color: #a5a5a5; margin-top: 4px; font-style: italic;">💬 {g["Megjegyzés"]}</div>'
                        
                    unpaid = max(0.0, total - paid)
                    unpaid_str = f" | Hátralék: <strong style='color: #ff5252;'>{unpaid:.0f} RON</strong>" if unpaid > 0 else " | ✨ Rendezte"
                    
                    meals_val = g.get('Étkezések', 'ALL')
                    meals_html = render_meal_badges(meals_val)
                    
                    txs = parse_payments_history(g)
                    tx_detail_str = ""
                    if len(txs) > 1:
                        tx_parts = []
                        for tx in txs:
                            m_icon = "💵" if tx['method'] == 'Készpénz' else ("🎟️" if tx['method'] == 'Vakációs Voucher' else "🏦")
                            tx_parts.append(f"{tx['amount']:.0f} RON {m_icon}")
                        tx_detail_str = f" <span style='font-size: 0.8em; color: #a5a5a5;'>({' + '.join(tx_parts)})</span>"
                        
                    guest_html = f"""
                    <div style="background-color: #222530; border-radius: 6px; padding: 8px 12px; margin-bottom: 8px; border-left: 4px solid {status_color}; display: flex; flex-direction: column; justify-content: space-between; font-size: 0.9em;">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div>
                                <strong style="color: #ffffff; font-size: 1.05em;">{g['Név']}</strong>
                                <span style="font-size: 0.75em; background-color: #3b3f54; color: #d1d5db; padding: 1.5px 5px; border-radius: 4px; margin-left: 5px;">{g['Típus']}</span>
                                {acc_badge}
                                {menu_badge}
                                {pay_badge}
                            </div>
                            <div style="text-align: right; font-size: 0.85em;">
                                <span style="color: {status_color}; font-weight: bold;">{status_text}</span>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px; border-top: 1px dashed #2d3142; padding-top: 4px; font-size: 0.85em; color: #a5a5a5;">
                            <div>
                                Befizetett előleg: <strong style="color: #4caf50;">{paid:.0f} RON</strong>{tx_detail_str} / Összesen: <strong style="color: #ffffff;">{total:.0f} RON</strong>{unpaid_str}
                            </div>
                            <div style="font-size: 0.85em; color: #888;">
                                {g.get('Éjszakák Száma', 5)} nap
                            </div>
                        </div>
                        {note_html}
                        <div style="margin-top: 4px; border-top: 1px dashed #2d3142; padding-top: 4px;">
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
                        
                    with col_g_move.popover("🚚", help=f"{g['Név']} átköltöztetése másik szobába/házba"):
                        st.markdown(f"**🚚 {g['Név']} költöztetése**")
                        st.caption(f"Jelenlegi szállás: `{g['Szállás']}`")
                        
                        target_room_ext = st.selectbox(
                            "Új szálláshely:",
                            options=all_camp_rooms,
                            index=all_camp_rooms.index(g['Szállás']) if g['Szállás'] in all_camp_rooms else 0,
                            format_func=lambda r: f"{r} ({len(df[df['Szállás']==r])}/{cap_lookup.get(r, '∞')} fő)",
                            key=f"pop_move_ext_sel_{idx_g}"
                        )
                        
                        if st.button("🟢 Költöztetés mentése", key=f"pop_btn_move_ext_save_{idx_g}", use_container_width=True):
                            df.loc[idx_g, 'Szállás'] = target_room_ext
                            st.session_state.guests_df = recalculate_dataframe(df)
                            save_data(st.session_state.guests_df)
                            st.session_state['map_success_msg'] = f"✅ {g['Név']} sikeresen átköltöztetve ide: {target_room_ext}!"
                            st.rerun()
            st.markdown("---")
        else:
            st.subheader("📋 Jelenlegi szobabeosztás")
            cap_lookup = {r['Név']: r['Kapacitás'] for r in accommodations}
            for room in rooms:
                room_guests = building_guests[building_guests['Szállás'] == room]
                occ = len(room_guests)
                cap = cap_lookup.get(room, 4)
                badge_color = "🟢" if occ < cap else "🔴"
                
                exp_label = f"🚪 Szoba: {room} — {badge_color} {occ}/{cap} fő"
                with st.expander(exp_label, expanded=True):
                    col_room_add_lbl, col_room_add_btn = st.columns([4, 1.2])
                    col_room_add_lbl.markdown("*(Új vendég regisztrálása a szobába)*")
                    if col_room_add_btn.button("➕ Új vendég", key=f"btn_add_{room}", use_container_width=True):
                        st.session_state['booking_edit_mode'] = True
                        st.session_state['preset_room'] = room
                        st.session_state['edit_guest_idx'] = None
                        st.rerun()
                    
                    st.markdown(" ")
                    if room_guests.empty:
                        st.caption("*(Ebben a szobában még nincs foglalás)*")
                    else:
                        for idx_g, g in room_guests.iterrows():
                            col_g_info, col_g_edit, col_g_move = st.columns([4.2, 0.9, 0.9])
                            
                            paid = g.get('Fizetett előleg', 0.0)
                            total = g.get('Összköltség', 0.0)
                            status_text = "🟢 Véglegesítve" if g['Státusz'] == "Végleges" else "🟡 Függőben"
                            status_color = "#4caf50" if g['Státusz'] == "Végleges" else "#ffb300"
                            
                            menu_badge = ""
                            if g.get('Gyermekmenü', False):
                                menu_badge = '<span style="font-size: 0.7em; background-color: #0288d1; color: #ffffff; padding: 1.5px 4px; border-radius: 4px; margin-left: 5px; font-weight: bold;">👶 Gyermekmenü</span>'
                            
                            pm_val = g.get('Fizetési Mód', 'Utalás')
                            pay_badge = ""
                            if paid > 0:
                                if pm_val == 'Vakációs Voucher':
                                    pay_badge = '<span style="font-size: 0.7em; background-color: #7e22ce; color: #ffffff; padding: 1.5px 4px; border-radius: 4px; margin-left: 5px; font-weight: bold;">🎟️ Voucher</span>'
                                elif pm_val == 'Készpénz':
                                    pay_badge = '<span style="font-size: 0.7em; background-color: #15803d; color: #ffffff; padding: 1.5px 4px; border-radius: 4px; margin-left: 5px; font-weight: bold;">💵 Készpénz</span>'
                                else:
                                    pay_badge = '<span style="font-size: 0.7em; background-color: #1e3a8a; color: #ffffff; padding: 1.5px 4px; border-radius: 4px; margin-left: 5px; font-weight: bold;">🏦 Utalás</span>'
                            
                            note_html = ""
                            if g.get('Megjegyzés'):
                                note_html = f'<div style="font-size: 0.8em; color: #a5a5a5; margin-top: 4px; font-style: italic;">💬 {g["Megjegyzés"]}</div>'
                                
                            # Calculate unpaid
                            unpaid = max(0.0, total - paid)
                            unpaid_str = f" | Hátralék: <strong style='color: #ff5252;'>{unpaid:.0f} RON</strong>" if unpaid > 0 else " | ✨ Rendezte"
                            
                            meals_val = g.get('Étkezések', 'ALL')
                            meals_html = render_meal_badges(meals_val)
                            
                            txs = parse_payments_history(g)
                            tx_detail_str = ""
                            if len(txs) > 1:
                                tx_parts = []
                                for tx in txs:
                                    m_icon = "💵" if tx['method'] == 'Készpénz' else ("🎟️" if tx['method'] == 'Vakációs Voucher' else "🏦")
                                    tx_parts.append(f"{tx['amount']:.0f} RON {m_icon}")
                                tx_detail_str = f" <span style='font-size: 0.8em; color: #a5a5a5;'>({' + '.join(tx_parts)})</span>"
                                
                            guest_html = f"""
                            <div style="background-color: #222530; border-radius: 6px; padding: 8px 12px; margin-bottom: 8px; border-left: 4px solid {status_color}; display: flex; flex-direction: column; justify-content: space-between; font-size: 0.9em;">
                                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                                    <div>
                                        <strong style="color: #ffffff; font-size: 1.05em;">{g['Név']}</strong>
                                        <span style="font-size: 0.75em; background-color: #3b3f54; color: #d1d5db; padding: 1.5px 5px; border-radius: 4px; margin-left: 5px;">{g['Típus']}</span>
                                        {menu_badge}
                                        {pay_badge}
                                    </div>
                                    <div style="text-align: right; font-size: 0.85em;">
                                        <span style="color: {status_color}; font-weight: bold;">{status_text}</span>
                                    </div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px; border-top: 1px dashed #2d3142; padding-top: 4px; font-size: 0.85em; color: #a5a5a5;">
                                    <div>
                                        Befizetett előleg: <strong style="color: #4caf50;">{paid:.0f} RON</strong>{tx_detail_str} / Összesen: <strong style="color: #ffffff;">{total:.0f} RON</strong>{unpaid_str}
                                    </div>
                                    <div style="font-size: 0.85em; color: #888;">
                                        {g.get('Éjszakák Száma', 5)} éjszaka
                                    </div>
                                </div>
                                {note_html}
                                <div style="margin-top: 4px; border-top: 1px dashed #2d3142; padding-top: 4px;">
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
                                
                            with col_g_move.popover("🚚", help=f"{g['Név']} átköltöztetése másik szobába/házba"):
                                st.markdown(f"**🚚 {g['Név']} költöztetése**")
                                st.caption(f"Jelenlegi szállás: `{g['Szállás']}`")
                                
                                target_room = st.selectbox(
                                    "Új szálláshely:",
                                    options=all_camp_rooms,
                                    index=all_camp_rooms.index(g['Szállás']) if g['Szállás'] in all_camp_rooms else 0,
                                    format_func=lambda r: f"{r} ({len(df[df['Szállás']==r])}/{cap_lookup.get(r, '∞')} fő)",
                                    key=f"pop_move_sel_{idx_g}"
                                )
                                
                                if st.button("🟢 Költöztetés mentése", key=f"pop_btn_move_save_{idx_g}", use_container_width=True):
                                    df.loc[idx_g, 'Szállás'] = target_room
                                    st.session_state.guests_df = recalculate_dataframe(df)
                                    save_data(st.session_state.guests_df)
                                    st.session_state['map_success_msg'] = f"✅ {g['Név']} sikeresen átköltöztetve ide: {target_room}!"
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
                cat_display_opts = list(CAT_DISPLAY_MAP.values())
                selected_cat_display = col2.selectbox(
                    "Kategória", 
                    cat_display_opts, 
                    index=cat_display_opts.index(CAT_DISPLAY_MAP.get(g['Típus'], "Felnőtt (alapár)")) if g['Típus'] in CAT_DISPLAY_MAP else 0
                )
                g_type = CAT_REVERSE_MAP[selected_cat_display]
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
                    g_room = col3.selectbox(
                        "Szálláshely / Szoba",
                        options=all_camp_rooms,
                        index=all_camp_rooms.index(g['Szállás']) if g['Szállás'] in all_camp_rooms else 0,
                        format_func=lambda r: f"{r} ({len(df[df['Szállás']==r])}/{cap_lookup.get(r, '∞')} fő)"
                    )
                g_child_menu = col3b.checkbox("Gyermekmenü?", value=bool(g.get('Gyermekmenü', False)))
                
                col4, col5b, col6 = st.columns([1, 1, 1])
                g_nights = col4.slider("Éjszakák", min_value=1, max_value=5, value=int(g['Éjszakák Száma']))
                g_discount = col5b.number_input("Kedvezmény (%)", min_value=0.0, max_value=100.0, value=float(g.get('Kedvezmény (%)', 0.0)), step=5.0)
                g_status_bool = col6.checkbox("Véglegesített?", value=(g['Státusz'] == "Végleges"))
                g_status = "Végleges" if g_status_bool else "Függőben"
                
                g_note = st.text_input("Megjegyzés", value=g.get('Megjegyzés', ''))
                
                # Multi-installment payments block (Fully Inline Editable)
                st.markdown("---")
                st.markdown("##### 💳 Befizetések Részletezése (Minden tétel közvetlenül szerkeszthető & hozzáadható)")
                
                tx_session_key = f"edit_txs_{idx}"
                if tx_session_key not in st.session_state or st.session_state.get('last_edit_idx') != idx:
                    st.session_state[tx_session_key] = parse_payments_history(g)
                    st.session_state['last_edit_idx'] = idx

                edit_txs = st.session_state[tx_session_key]
                tx_to_remove = None

                if not edit_txs:
                    st.info("*(Még nincs befizetés rögzítve ehhez a vendéghez. KATTINTS A LENTI GOMBRA ÚJ BEREGISZTRÁLÁSÁHOZ!)*")
                else:
                    for i, tx in enumerate(edit_txs):
                        c_t1, c_t2, c_t3, c_t4, c_t5 = st.columns([1.5, 1.5, 1.3, 2, 0.5])
                        
                        amt_val = c_t1.number_input(
                            f"#{i+1}. Összeg (RON)",
                            min_value=0.0,
                            value=float(tx.get('amount', 0.0)),
                            step=50.0,
                            key=f"tx_amt_{idx}_{i}"
                        )
                        
                        m_opts = ["Utalás", "Vakációs Voucher", "Készpénz"]
                        cur_m = str(tx.get('method', 'Utalás'))
                        m_val = c_t2.selectbox(
                            "Fizetési Mód",
                            options=m_opts,
                            index=m_opts.index(cur_m) if cur_m in m_opts else 0,
                            key=f"tx_meth_{idx}_{i}"
                        )
                        
                        cur_d = str(tx.get('date', '') or '').strip()
                        parsed_d = None
                        if cur_d and cur_d not in ['nan', 'None']:
                            try:
                                parsed_d = datetime.strptime(cur_d, "%Y-%m-%d").date()
                            except Exception:
                                parsed_d = None

                        d_val = c_t3.date_input(
                            "Dátum (választó 📅)",
                            value=parsed_d,
                            format="YYYY-MM-DD",
                            key=f"tx_date_{idx}_{i}"
                        )
                        d_str = d_val.strftime("%Y-%m-%d") if d_val else ""
                        
                        note_val = c_t4.text_input(
                            "Megjegyzés",
                            value=str(tx.get('note', '')),
                            placeholder="Pl. Előleg / Utalás",
                            key=f"tx_note_{idx}_{i}"
                        )
                        
                        tx['amount'] = amt_val
                        tx['method'] = m_val
                        tx['date'] = d_str
                        tx['note'] = note_val.strip()
                        
                        if c_t5.button("🗑️", key=f"btn_del_tx_{idx}_{i}", help="Ezen tétel törlése"):
                            tx_to_remove = i

                if tx_to_remove is not None:
                    edit_txs.pop(tx_to_remove)
                    st.rerun()

                # Calculate current remaining unpaid balance
                cur_meals_str = str(g.get('Étkezések', 'ALL'))
                temp_acc_row = {
                    'Típus': g_type,
                    'Szállás': g_room,
                    'Két család egy szobában': bool(g.get('Két család egy szobában', False)),
                    'Éjszakák Száma': g_nights
                }
                est_acc_cost = calculate_accommodation_cost(temp_acc_row)
                est_meal_cost = calculate_meals_cost(cur_meals_str, g_type, g_child_menu)
                est_subtotal = est_acc_cost + est_meal_cost
                est_discount_val = est_subtotal * (g_discount / 100.0)
                est_total_cost = max(0.0, est_subtotal - est_discount_val)

                calc_paid = sum(float(t['amount']) for t in edit_txs)
                rem_unpaid = max(0.0, est_total_cost - calc_paid)

                if st.button("➕ Új befizetési részlet sor hozzáadása", key=f"btn_add_row_{idx}"):
                    edit_txs.append({
                        'amount': float(rem_unpaid),
                        'method': 'Utalás',
                        'date': '',
                        'note': ''
                    })
                    st.rerun()

                st.markdown(
                    f"💰 **Jelenleg rögzített befizetések összesen:** <span style='color: #4caf50; font-weight: bold; font-size: 1.1em;'>{calc_paid:.0f} RON</span> ({len(edit_txs)} részletben) &nbsp;|&nbsp; **Még kifizetetlen hátralék:** <span style='color: #ff5252; font-weight: bold; font-size: 1.1em;'>{rem_unpaid:.0f} RON</span>",
                    unsafe_allow_html=True
                )
                
                st.markdown("##### 🍽️ Igényelt étkezések:")
                m_cols = st.columns(6)
                
                cur_meals = str(g.get('Étkezések', 'ALL'))
                if cur_meals in ['ALL', 'all', 'nan', 'None', '']:
                    active_set = {'T_D', 'W_B', 'W_L', 'W_D', 'Th_B', 'Th_L', 'Th_D', 'F_B', 'F_L', 'F_D', 'S_B', 'S_L', 'S_D', 'Su_BD', 'Su_L', 'W_BD', 'Th_BD', 'F_BD', 'S_BD'}
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
                    w_b = st.checkbox("🥣 Reggeli", value=('W_B' in active_set or 'W_BD' in active_set), key="chk_wb")
                    w_l = st.checkbox("🍲 Ebéd", value=('W_L' in active_set), key="chk_wl")
                    w_d = st.checkbox("🌆 Vacsora", value=('W_D' in active_set or 'W_BD' in active_set), key="chk_wd")
                    if w_b: selected_meals.append('W_B')
                    if w_l: selected_meals.append('W_L')
                    if w_d: selected_meals.append('W_D')
                    
                # Thursday
                with m_cols[2]:
                    st.markdown("🟢 **Csütörtök**")
                    th_b = st.checkbox("🥣 Reggeli", value=('Th_B' in active_set or 'Th_BD' in active_set), key="chk_thb")
                    th_l = st.checkbox("🍲 Ebéd", value=('Th_L' in active_set), key="chk_thl")
                    th_d = st.checkbox("🌆 Vacsora", value=('Th_D' in active_set or 'Th_BD' in active_set), key="chk_thd")
                    if th_b: selected_meals.append('Th_B')
                    if th_l: selected_meals.append('Th_L')
                    if th_d: selected_meals.append('Th_D')
                    
                # Friday
                with m_cols[3]:
                    st.markdown("🔵 **Péntek**")
                    f_b = st.checkbox("🥣 Reggeli", value=('F_B' in active_set or 'F_BD' in active_set), key="chk_fb")
                    f_l = st.checkbox("🍲 Ebéd", value=('F_L' in active_set), key="chk_fl")
                    f_d = st.checkbox("🌆 Vacsora", value=('F_D' in active_set or 'F_BD' in active_set), key="chk_fd")
                    if f_b: selected_meals.append('F_B')
                    if f_l: selected_meals.append('F_L')
                    if f_d: selected_meals.append('F_D')
                    
                # Saturday
                with m_cols[4]:
                    st.markdown("🟣 **Szombat**")
                    s_b = st.checkbox("🥣 Reggeli", value=('S_B' in active_set or 'S_BD' in active_set), key="chk_sb")
                    s_l = st.checkbox("🍲 Ebéd", value=('S_L' in active_set), key="chk_sl")
                    s_d = st.checkbox("🌆 Vacsora", value=('S_D' in active_set or 'S_BD' in active_set), key="chk_sd")
                    if s_b: selected_meals.append('S_B')
                    if s_l: selected_meals.append('S_L')
                    if s_d: selected_meals.append('S_D')
                    
                # Sunday
                with m_cols[5]:
                    st.markdown("🟤 **Vasárnap**")
                    su_bd = st.checkbox("🥣 Reggeli", value=('Su_BD' in active_set), key="chk_subd")
                    su_l = st.checkbox("🍲 Ebéd", value=('Su_L' in active_set), key="chk_sul")
                    if su_bd: selected_meals.append('Su_BD')
                    if su_l: selected_meals.append('Su_L')
                    
                g_meals = ",".join(selected_meals) if selected_meals else "NONE"
                
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
                        st.session_state.pop(f"edit_txs_{idx}", None)
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

            # If discount warning is active for this guest
            if st.session_state.get('confirm_discount_edit_idx') == idx:
                st.warning(f"⚠️ **Figyelem! A vendég csak {g_nights} napra regisztrált (és/vagy {len(selected_meals)}/15 étkezésre), nem a tábor teljes idejére. Biztos vagy benne, hogy ennek ellenére kedvezményt adsz neki?**")
                col_c1, col_c2 = st.columns(2)
                if col_c1.button("🟢 Igen, mentés kedvezménnyel", type="primary", key="warn_edit_yes", use_container_width=True):
                    clean_txs = [t for t in st.session_state.get(f"edit_txs_{idx}", []) if float(t.get('amount', 0.0)) > 0]
                    df.loc[idx, 'Név'] = g_name
                    df.loc[idx, 'Típus'] = g_type
                    df.loc[idx, 'Szállás'] = g_room
                    df.loc[idx, 'Éjszakák Száma'] = g_nights
                    df.loc[idx, 'Gyermekmenü'] = g_child_menu
                    df.loc[idx, 'Kedvezmény (%)'] = g_discount
                    df.loc[idx, 'Befizetések JSON'] = serialize_payments_history(clean_txs)
                    df.loc[idx, 'Státusz'] = g_status
                    df.loc[idx, 'Megjegyzés'] = g_note
                    df.loc[idx, 'Étkezések'] = g_meals
                    st.session_state.guests_df = recalculate_dataframe(df)
                    save_data(st.session_state.guests_df)
                    st.session_state.pop(f"edit_txs_{idx}", None)
                    st.session_state['edit_guest_idx'] = None
                    st.session_state['booking_edit_mode'] = False
                    st.session_state['confirm_discount_edit_idx'] = None
                    st.rerun()
                if col_c2.button("🔴 Nem, ablak bezárása", key="warn_edit_no", use_container_width=True):
                    st.session_state.pop(f"edit_txs_{idx}", None)
                    st.session_state['edit_guest_idx'] = None
                    st.session_state['booking_edit_mode'] = False
                    st.session_state['confirm_discount_edit_idx'] = None
                    st.rerun()
            else:
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.button("💾 Mentés", type="primary", use_container_width=True):
                    if (g_nights < 5 or len(selected_meals) < 15) and g_discount > 0:
                        st.session_state['confirm_discount_edit_idx'] = idx
                        st.rerun()
                    else:
                        clean_txs = [t for t in st.session_state.get(f"edit_txs_{idx}", []) if float(t.get('amount', 0.0)) > 0]
                        df.loc[idx, 'Név'] = g_name
                        df.loc[idx, 'Típus'] = g_type
                        df.loc[idx, 'Szállás'] = g_room
                        df.loc[idx, 'Éjszakák Száma'] = g_nights
                        df.loc[idx, 'Gyermekmenü'] = g_child_menu
                        df.loc[idx, 'Kedvezmény (%)'] = g_discount
                        df.loc[idx, 'Befizetések JSON'] = serialize_payments_history(clean_txs)
                        df.loc[idx, 'Státusz'] = g_status
                        df.loc[idx, 'Megjegyzés'] = g_note
                        df.loc[idx, 'Étkezések'] = g_meals
                        st.session_state.guests_df = recalculate_dataframe(df)
                        save_data(st.session_state.guests_df)
                        st.session_state.pop(f"edit_txs_{idx}", None)
                        st.session_state['edit_guest_idx'] = None
                        st.session_state['booking_edit_mode'] = False
                        st.rerun()
                
                if col_btn2.button("Bezárás mentés nélkül", use_container_width=True):
                    st.session_state.pop(f"edit_txs_{idx}", None)
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
            new_cat_display_opts = list(CAT_DISPLAY_MAP.values())
            selected_new_cat_display = col_n2.selectbox(
                "Kategória:", 
                new_cat_display_opts, 
                index=4 if is_external_group else 0,
                key="new_g_type_display"
            )
            new_type = CAT_REVERSE_MAP[selected_new_cat_display]
            
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
                
            col_n4, col_n5, col_n5_meth, col_n5_date, col_n5b, col_n6 = st.columns([1, 1, 1.2, 1.1, 1, 1])
            new_nights = col_n4.slider("Éjszakák száma:", min_value=1, max_value=5, value=5, key="new_g_nights")
            new_paid = col_n5.number_input("Előleg (RON):", min_value=0.0, value=0.0, step=50.0, key="new_g_paid")
            new_pay_method = col_n5_meth.selectbox("Fizetési Mód:", options=["Utalás", "Vakációs Voucher", "Készpénz"], index=0, key="new_g_pay_method")
            new_pay_date_val = col_n5_date.date_input("Befizetés dátuma 📅:", value=datetime.now().date() if new_paid > 0 else None, format="YYYY-MM-DD", key="new_g_pay_date")
            new_pay_date = new_pay_date_val.strftime("%Y-%m-%d") if new_pay_date_val else ""
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
                new_w_b = st.checkbox("🥣 Reggeli", value=True, key="new_chk_wb")
                new_w_l = st.checkbox("🍲 Ebéd", value=True, key="new_chk_wl")
                new_w_d = st.checkbox("🌆 Vacsora", value=True, key="new_chk_wd")
                if new_w_b: new_selected_meals.append('W_B')
                if new_w_l: new_selected_meals.append('W_L')
                if new_w_d: new_selected_meals.append('W_D')
                
            # Thursday
            with m_cols_new[2]:
                st.markdown("🟢 **Csütörtök**")
                new_th_b = st.checkbox("🥣 Reggeli", value=True, key="new_chk_thb")
                new_th_l = st.checkbox("🍲 Ebéd", value=True, key="new_chk_thl")
                new_th_d = st.checkbox("🌆 Vacsora", value=True, key="new_chk_thd")
                if new_th_b: new_selected_meals.append('Th_B')
                if new_th_l: new_selected_meals.append('Th_L')
                if new_th_d: new_selected_meals.append('Th_D')
                
            # Friday
            with m_cols_new[3]:
                st.markdown("🔵 **Péntek**")
                new_f_b = st.checkbox("🥣 Reggeli", value=True, key="new_chk_fb")
                new_f_l = st.checkbox("🍲 Ebéd", value=True, key="new_chk_fl")
                new_f_d = st.checkbox("🌆 Vacsora", value=True, key="new_chk_fd")
                if new_f_b: new_selected_meals.append('F_B')
                if new_f_l: new_selected_meals.append('F_L')
                if new_f_d: new_selected_meals.append('F_D')
                
            # Saturday
            with m_cols_new[4]:
                st.markdown("🟣 **Szombat**")
                new_s_b = st.checkbox("🥣 Reggeli", value=True, key="new_chk_sb")
                new_s_l = st.checkbox("🍲 Ebéd", value=True, key="new_chk_sl")
                new_s_d = st.checkbox("🌆 Vacsora", value=True, key="new_chk_sd")
                if new_s_b: new_selected_meals.append('S_B')
                if new_s_l: new_selected_meals.append('S_L')
                if new_s_d: new_selected_meals.append('S_D')
                
            # Sunday
            with m_cols_new[5]:
                st.markdown("🟤 **Vasárnap**")
                new_su_bd = st.checkbox("🥣 Reggeli", value=True, key="new_chk_subd")
                new_su_l = st.checkbox("🍲 Ebéd", value=True, key="new_chk_sul")
                if new_su_bd: new_selected_meals.append('Su_BD')
                if new_su_l: new_selected_meals.append('Su_L')
                
            new_meals = ",".join(new_selected_meals) if new_selected_meals else "NONE"
            
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
            
        # If discount warning is active for new guest
        if st.session_state.get('confirm_discount_new_guest') is True:
            st.warning(f"⚠️ **Figyelem! A vendég csak {new_nights} napra regisztrált (és/vagy {len(new_selected_meals)}/11 étkezésre), nem a tábor teljes idejére. Biztos vagy benne, hogy ennek ellenére kedvezményt adsz neki?**")
            col_nc1, col_nc2 = st.columns(2)
            if col_nc1.button("🟢 Igen, mentés kedvezménnyel", type="primary", key="warn_new_yes", use_container_width=True):
                if new_name.strip():
                    new_tx_list = [{'amount': new_paid, 'method': new_pay_method, 'date': new_pay_date.strip() if new_pay_date.strip() else datetime.now().strftime("%Y-%m-%d"), 'note': 'Első befizetés'}] if new_paid > 0 else []
                    new_row = {
                        'Név': new_name.strip(),
                        'Típus': new_type,
                        'Szállás': new_room,
                        'Éjszakák Száma': new_nights,
                        'Két család egy szobában': False,
                        'Gyermekmenü': new_child_menu,
                        'Kedvezmény (%)': new_discount,
                        'Fizetett előleg': new_paid,
                        'Fizetési Mód': new_pay_method,
                        'Befizetés Dátuma': new_pay_date.strip() if (new_paid > 0 or new_pay_date.strip()) else "",
                        'Befizetések JSON': serialize_payments_history(new_tx_list),
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
                st.session_state['confirm_discount_new_guest'] = None
                st.rerun()
            if col_nc2.button("🔴 Nem, ablak bezárása", key="warn_new_no", use_container_width=True):
                st.session_state['preset_room'] = None
                st.session_state['booking_edit_mode'] = False
                st.session_state['confirm_discount_new_guest'] = None
                st.rerun()
        else:
            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.button("💾 Foglalás Mentése", type="primary", use_container_width=True):
                if new_name.strip():
                    if (new_nights < 5 or len(new_selected_meals) < 11) and new_discount > 0:
                        st.session_state['confirm_discount_new_guest'] = True
                        st.rerun()
                    else:
                        new_tx_list = [{'amount': new_paid, 'method': new_pay_method, 'date': new_pay_date.strip() if new_pay_date.strip() else datetime.now().strftime("%Y-%m-%d"), 'note': 'Első befizetés'}] if new_paid > 0 else []
                        new_row = {
                            'Név': new_name.strip(),
                            'Típus': new_type,
                            'Szállás': new_room,
                            'Éjszakák Száma': new_nights,
                            'Két család egy szobában': False,
                            'Gyermekmenü': new_child_menu,
                            'Kedvezmény (%)': new_discount,
                            'Fizetett előleg': new_paid,
                            'Fizetési Mód': new_pay_method,
                            'Befizetés Dátuma': new_pay_date.strip() if (new_paid > 0 or new_pay_date.strip()) else "",
                            'Befizetések JSON': serialize_payments_history(new_tx_list),
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
# 5.b MOBILE MAP & CAMPER APP VIEW ROUTER
# -----------------------------------------------------------------------------
query_params = st.query_params
is_mobile_view = (
    query_params.get("view") in ["map", "tabor", "app"] or
    query_params.get("mobile") in ["1", "true"] or
    query_params.get("app") in ["1", "true"] or
    st.session_state.get("mobile_mode") is True
)

if is_mobile_view:
    st.markdown("""
    <style>
        .block-container { padding-top: 0.4rem !important; padding-bottom: 1rem !important; padding-left: 0.4rem !important; padding-right: 0.4rem !important; }
        header { visibility: hidden; }
        footer { visibility: hidden; }
        #MainMenu { visibility: hidden; }
        .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
        
        .camper-card {
            background: rgba(30, 41, 59, 0.85);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 12px;
            color: #f8fafc;
        }
        .program-item {
            border-left: 3.5px solid #4fc3f7;
            background: rgba(15, 23, 42, 0.6);
            border-radius: 6px;
            padding: 8px 12px;
            margin-bottom: 8px;
        }
        .program-time {
            color: #4fc3f7;
            font-weight: bold;
            font-size: 0.9em;
        }
        .program-title {
            color: #ffffff;
            font-weight: 700;
            font-size: 1.02em;
        }
        .program-menu {
            color: #ffb74d;
            font-size: 0.88em;
            margin-top: 3px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    m_top1, m_top2 = st.columns([3, 1])
    with m_top1:
        st.markdown("<h3 style='margin:0; color:#4fc3f7;'>⛺ Fűzi Nyári Tábor 2026</h3>", unsafe_allow_html=True)
        st.caption("📱 Mobil Táborozó Alkalmazás & Információs Portál")
    with m_top2:
        if st.button("🖥️ Admin", key="btn_exit_mobile", help="Vissza az admin kezelőfelületre"):
            st.query_params.clear()
            st.session_state['mobile_mode'] = False
            st.rerun()

    camper_tab1, camper_tab2, camper_tab3, camper_tab4 = st.tabs([
        "🗺️ Térkép & Szállás",
        "📅 Tábori Program",
        "🤝 Szolgálatok",
        "📜 Házirend & Etikett"
    ])

    # -------------------------------------------------------------------------
    # CAMPER TAB 1: INTERACTIVE MAP & HOUSES
    # -------------------------------------------------------------------------
    with camper_tab1:
        st.caption("📱 **Fekvő (Landscape) nézet ajánlott!** Koppints a térképen lévő házakra a szobák és vendégek megtekintéséhez!")

        # Interactive Map Component
        if os.path.exists("tabor_muhold.jpg"):
            with open("tabor_muhold.jpg", "rb") as _f:
                _img_b64 = base64.b64encode(_f.read()).decode()
            _bstatus = build_building_status(st.session_state.guests_df, accommodations)
            
            if map_component:
                map_result = map_component(img_b64=_img_b64, status=_bstatus, edit_mode=False, key="mobile_map_widget")
                if map_result and map_result.get("action") == "click":
                    click_ts = map_result.get("ts")
                    if st.session_state.get("mobile_click_ts") != click_ts:
                        st.session_state["mobile_click_ts"] = click_ts
                        st.session_state["active_building"] = map_result.get("bid")
                        st.rerun()

        # Guest Search Box
        st.markdown("---")
        search_q = st.text_input("🔍 Keresés a táborozók vagy szobák között:", placeholder="Írj be egy nevet (pl. Kristály)...", key="mobile_search_guest")
        if search_q.strip():
            sq = search_q.strip().lower()
            df_g = st.session_state.guests_df
            matches = df_g[df_g['Név'].str.lower().str.contains(sq) | df_g['Szállás'].str.lower().str.contains(sq)]
            if matches.empty:
                st.info("Nincs találat erre a keresésre.")
            else:
                st.markdown(f"**Találatok ({len(matches)} fő):**")
                for _, mg in matches.iterrows():
                    m_meals = get_meal_summary_text(mg)
                    st.markdown(
                        f"👤 **{mg['Név']}** ({mg['Típus']}) &nbsp;|&nbsp; 🏠 **{mg['Szállás']}**<br/>"
                        f"<small style='color:#b0bec5;'>🍽️ {m_meals}</small>",
                        unsafe_allow_html=True
                    )
                    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # CAMPER TAB 2: DAILY SCHEDULE & MENUS
    # -------------------------------------------------------------------------
    with camper_tab2:
        st.markdown("### 📅 Tábori Részletes Program (08.18 - 08.23)")
        
        day_choice = st.radio(
            "Válassz napot:",
            options=["🔴 Kedd (08.18)", "🟡 Szerda (08.19)", "🟢 Csütörtök (08.20)", "🔵 Péntek (08.21)", "🟣 Szombat (08.22)", "🟤 Vasárnap (08.23)"],
            horizontal=True,
            key="camper_day_select"
        )
        
        if "Kedd" in day_choice:
            st.markdown("""
            <div class="program-item">
                <div class="program-time">16:00</div>
                <div class="program-title">🧳 Érkezés és regisztráció</div>
            </div>
            <div class="program-item">
                <div class="program-time">19:00</div>
                <div class="program-title">🌆 Vacsora</div>
            </div>
            <div class="program-item">
                <div class="program-time">19:30</div>
                <div class="program-title">🎬 Filmnézés</div>
            </div>
            <div class="program-item">
                <div class="program-time">21:00</div>
                <div class="program-title">🔥 Tábortűz</div>
            </div>
            """, unsafe_allow_html=True)
            
        elif "Szerda" in day_choice:
            st.markdown("""
            <div class="program-item"><div class="program-time">06:30 - 07:40</div><div class="program-title">🙏 Imaalkalom</div></div>
            <div class="program-item"><div class="program-time">07:40 - 07:55</div><div class="program-title">🏃 Reggeli torna</div></div>
            <div class="program-item"><div class="program-time">08:00 - 09:00</div><div class="program-title">🥣 Reggeli</div></div>
            <div class="program-item"><div class="program-time">09:30</div><div class="program-title">⛪ Istentisztelet</div></div>
            <div class="program-item">
                <div class="program-time">13:00 - 14:00</div>
                <div class="program-title">🍲 Ebéd</div>
                <div class="program-menu">🥗 <em>Menü: Radóczi csorba csirkemellel, zöldborsó főzelék, mészáros kolbász, kenyér, gyümölcs</em></div>
            </div>
            <div class="program-item"><div class="program-time">15:00 - 16:30</div><div class="program-title">🏓 Asztaltenisz bajnokság</div></div>
            <div class="program-item"><div class="program-time">16:30 - 17:00</div><div class="program-title">☕ Kávészünet</div></div>
            <div class="program-item">
                <div class="program-time">17:00 - 19:00</div>
                <div class="program-title">🎤 Előadás és fórum</div>
                <div style="font-size:0.9em; color:#90caf9;">Előadó: <strong>Mézes András</strong></div>
            </div>
            <div class="program-item"><div class="program-time">19:00 - 20:00</div><div class="program-title">🌆 Vacsora</div></div>
            <div class="program-item"><div class="program-time">21:00</div><div class="program-title">🔥 Tábortűz dicsérettel</div></div>
            """, unsafe_allow_html=True)
            
        elif "Csütörtök" in day_choice:
            st.markdown("""
            <div class="program-item"><div class="program-time">06:30 - 07:40</div><div class="program-title">🙏 Imaalkalom</div></div>
            <div class="program-item"><div class="program-time">07:40 - 07:55</div><div class="program-title">🏃 Reggeli torna</div></div>
            <div class="program-item"><div class="program-time">08:00 - 09:00</div><div class="program-title">🥣 Reggeli</div></div>
            <div class="program-item"><div class="program-time">09:30</div><div class="program-title">⛪ Istentisztelet</div></div>
            <div class="program-item">
                <div class="program-time">13:00 - 14:00</div>
                <div class="program-title">🍲 Ebéd</div>
                <div class="program-menu">🥗 <em>Menü: Tárkonyos krumpli leves, zöldséges rizs, kemencében sült egész csirkecomb, kenyér, gyümölcs</em></div>
            </div>
            <div class="program-item">
                <div class="program-time">15:00 - 16:30</div>
                <div class="program-title">👥 Ifjúsági fórum (12-25 év)</div>
                <div style="font-size:0.9em; color:#90caf9;">Előadó: <strong>Mézes András</strong></div>
            </div>
            <div class="program-item"><div class="program-time">16:30 - 17:00</div><div class="program-title">☕ Kávészünet</div></div>
            <div class="program-item">
                <div class="program-time">17:00 - 19:00</div>
                <div class="program-title">🎤 Előadás és fórum: Kihívások hálójában</div>
                <div style="font-size:0.9em; color:#e0e0e0;"><em>Hogyan maradjunk tudatos szülők a mindennapok zűrzavarában?</em></div>
                <div style="font-size:0.9em; color:#90caf9;">Előadó: <strong>Filip Mária</strong> &nbsp;|&nbsp; 👨‍👦 Apa-gyermek program</div>
            </div>
            <div class="program-item"><div class="program-time">19:00 - 20:00</div><div class="program-title">🌆 Vacsora</div></div>
            <div class="program-item"><div class="program-time">20:30</div><div class="program-title">📖 Biblia Kvíz</div></div>
            <div class="program-item"><div class="program-time">21:30</div><div class="program-title">🔥 Tábortűz dicsérettel</div></div>
            """, unsafe_allow_html=True)
            
        elif "Péntek" in day_choice:
            st.markdown("""
            <div class="program-item"><div class="program-time">06:30 - 07:40</div><div class="program-title">🙏 Imaalkalom</div></div>
            <div class="program-item"><div class="program-time">07:40 - 07:55</div><div class="program-title">🏃 Reggeli torna</div></div>
            <div class="program-item"><div class="program-time">08:00 - 09:00</div><div class="program-title">🥣 Reggeli</div></div>
            <div class="program-item"><div class="program-time">09:30</div><div class="program-title">⛪ Istentisztelet</div></div>
            <div class="program-item">
                <div class="program-time">13:00 - 14:00</div>
                <div class="program-title">🍲 Ebéd</div>
                <div class="program-menu">🥗 <em>Menü: Brokkoli krémleves, levesgyöngy, krumplipüré, csirkemell csíkok, crispy szósz, kenyér, gyümölcs</em></div>
            </div>
            <div class="program-item"><div class="program-time">15:00 - 16:00</div><div class="program-title">👩 Női alkalom (+12 év)</div></div>
            <div class="program-item">
                <div class="program-time">17:00 - 18:30</div>
                <div class="program-title">👨 Alkalom férfiaknak - fórum</div>
                <div style="font-size:0.9em; color:#81c784;">🏊 Fürdés nőknek és gyerekeknek</div>
            </div>
            <div class="program-item"><div class="program-time">19:00 - 20:00</div><div class="program-title">🌆 Vacsora</div></div>
            <div class="program-item"><div class="program-time">21:00</div><div class="program-title">🎵 Dicséret-est</div></div>
            """, unsafe_allow_html=True)
            
        elif "Szombat" in day_choice:
            st.markdown("""
            <div class="program-item"><div class="program-time">06:30 - 07:40</div><div class="program-title">🙏 Imaalkalom</div></div>
            <div class="program-item"><div class="program-time">07:40 - 07:55</div><div class="program-title">🏃 Reggeli torna</div></div>
            <div class="program-item"><div class="program-time">08:00 - 09:00</div><div class="program-title">🥣 Reggeli</div></div>
            <div class="program-item"><div class="program-time">09:30</div><div class="program-title">⛪ Istentisztelet</div></div>
            <div class="program-item">
                <div class="program-time">13:00 - 14:00</div>
                <div class="program-title">🍲 Ebéd</div>
                <div class="program-menu">🥗 <em>Menü: Húsleves cérna laskával, sült nyakas karaj, párolt káposzta, parasztkrumpli, ecetes uborka, kenyér, desszert</em></div>
            </div>
            <div class="program-item">
                <div class="program-time">15:00 - 16:30</div>
                <div class="program-title">👩 Női alkalom - fórum (Mézes Csilla & Nagy Éva)</div>
                <div style="font-size:0.9em; color:#4fc3f7;">⚽ Futball bajnokság</div>
            </div>
            <div class="program-item">
                <div class="program-time">17:00 - 19:00</div>
                <div class="program-title">🎤 Előadás és fórum</div>
                <div style="font-size:0.9em; color:#90caf9;">Előadó: <strong>Mézes András</strong></div>
            </div>
            <div class="program-item"><div class="program-time">19:00 - 20:00</div><div class="program-title">🌆 Vacsora</div></div>
            <div class="program-item"><div class="program-time">21:00</div><div class="program-title">🔥 Tábortűz dicsérettel</div></div>
            """, unsafe_allow_html=True)
            
        elif "Vasárnap" in day_choice:
            st.markdown("""
            <div class="program-item"><div class="program-time">06:30 - 07:40</div><div class="program-title">🙏 Imaalkalom</div></div>
            <div class="program-item"><div class="program-time">07:40 - 07:55</div><div class="program-title">🏃 Reggeli torna</div></div>
            <div class="program-item"><div class="program-time">08:00 - 09:00</div><div class="program-title">🥣 Reggeli</div></div>
            <div class="program-item"><div class="program-time">09:30</div><div class="program-title">⛪ Istentisztelet</div></div>
            <div class="program-item">
                <div class="program-time">13:00</div>
                <div class="program-title">🍲 Ebéd</div>
                <div class="program-menu">🥗 <em>Menü: Palócleves disznóhússal, sajtos lasagne, paradicsomszósz, kenyér, desszert, doboz</em></div>
            </div>
            <div class="program-item"><div class="program-time">14:00</div><div class="program-title">🧹 Táborbontás & Hazautazás</div></div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # CAMPER TAB 3: SERVICES & COMMUNITY
    # -------------------------------------------------------------------------
    with camper_tab3:
        st.markdown("### 🤝 Szolgálatok & Közösségi Élet")
        
        st.markdown("""
        <div class="camper-card">
            <h4 style="color:#ffb74d; margin-top:0;">🙌 Önkéntes Szolgálat</h4>
            <p>A rendezvény minőségi lebonyolításához és a tábor költségeinek minimalizálásához elengedhetetlenül szükséges a résztvevők <strong>aktív részvétele különböző szolgálati és önkéntes feladatokban</strong>.</p>
        </div>
        
        <div class="camper-card">
            <h4 style="color:#4fc3f7; margin-top:0;">⏰ Pontosság</h4>
            <p>A gördülékeny működés érdekében elvárt, hogy minden résztvevő <strong>pontosan megjelenjen</strong> az előre megkapott szolgálati beosztásában jelzett területen, és a munkáját a szolgálatvezető útmutatásai szerint elvégezze.</p>
        </div>
        
        <div class="camper-card">
            <h4 style="color:#81c784; margin-top:0;">👶 Gyermekvigyázás</h4>
            <p>Gyermekvigyázást az <strong>istentiszteletek alatt</strong> lehet igénybe venni. Az előadások alatt a szülők oldják meg a gyerekeik felvigyázását, ha erre szükség van.</p>
        </div>
        
        <div class="camper-card" style="border-left: 4px solid #ba68c8;">
            <h4 style="color:#ba68c8; margin-top:0;">📖 Igei Útmutató</h4>
            <p>A résztvevők és szolgálók közötti kommunikációban a <strong>kölcsönös tiszteletadás és a testvéri szeretet</strong> tanúsítása az irányadó:</p>
            <ul>
                <li><em>"Egymás iránti gyengéd szeretettel, a tiszteletadásban egymást megelőzve."</em> (Róma 12:10)</li>
                <li><em>"Minden emberrel békességben éljetek."</em> (Róma 12:18)</li>
                <li><em>"Szeressétek egymást: ahogyan én szerettelek titeket."</em> (János 13:34)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # CAMPER TAB 4: HOUSE RULES & ETIQUETTE
    # -------------------------------------------------------------------------
    with camper_tab4:
        st.markdown("### 📜 Tábori Házirend & Etikett")
        
        st.markdown("""
        <div class="camper-card">
            <h4 style="color:#4caf50; margin-top:0;">⛪ Istentiszteletek & Előadások</h4>
            <ul>
                <li>A táborhely területén tartózkodók számára az <strong>istentiszteleteken való részvétel kötelező</strong>.</li>
                <li>Az istentiszteletek közben más tevékenység (sportolás, büfézés, étkezés) <strong>nem végezhető</strong>. Kivételt képeznek a szolgálati tevékenységek.</li>
                <li>A tanításokról, dicséretről, imaalkalmakról kép- és hangfelvételt készíteni <strong>tilos</strong> (hacsak erre a szervezők külön engedélyt nem adnak).</li>
            </ul>
        </div>

        <div class="camper-card">
            <h4 style="color:#ff9800; margin-top:0;">👔 Etikett & Öltözködés</h4>
            <ul>
                <li>Tiszteltel kérünk mindenkit, hogy a rendezvény teljes ideje alatt csak a <strong>keresztény erkölcsnek megfelelő</strong>, mások szabadságát nem korlátozó ruházatot viseljenek (1. Kor. 14).</li>
                <li>A tábor területén <strong>tilos fürdőruhában vagy azt törölközővel eltakarva járkálni</strong>! Kérjük a medence melletti öltözők használatát fürdés előtt és után.</li>
            </ul>
        </div>

        <div class="camper-card">
            <h4 style="color:#ef5350; margin-top:0;">🚫 Szigorú Tilalmak</h4>
            <ul>
                <li><strong>Alkohol fogyasztása, dohánytermékek és kábítószer használata szigorúan tilos.</strong></li>
                <li>Világi szórakozóhelyek látogatása a tábor időtartama alatt nem megengedett.</li>
                <li>Nyílt láng használata és tűzrakás tilos (kivételt képez az esti közös tábortűz).</li>
            </ul>
        </div>

        <div class="camper-card">
            <h4 style="color:#2196f3; margin-top:0;">🏊 Medence & Éjszakai Pihenő</h4>
            <ul>
                <li>A medence használata a programban feltüntetett időpontokon kívül <strong>tilos</strong>!</li>
                <li>Kérjük, hogy az éjszakát mindenki <strong>pihenéssel töltse</strong> a szálláshelyén, hogy a másnapi alkalmakat frissen tudja követni.</li>
            </ul>
        </div>

        <div class="camper-card">
            <h4 style="color:#ab47bc; margin-top:0;">📱 Mobiltelefon & Vezetés</h4>
            <ul>
                <li>A mobiltelefont korlátozottan használjuk. Publikus helyeken, közösségben csakis szükség esetén használható. Javasoljuk a <strong>telefonböjtöt</strong>.</li>
                <li>A területen elővigyázatosan vezessünk, a sebességkorlátozásokat betartva. Parkolás a külső parkolóban.</li>
            </ul>
        </div>

        <div class="camper-card" style="border-left: 4px solid #26a69a;">
            <h4 style="color:#26a69a; margin-top:0;">🏥 Egészségügy & Elsősegély</h4>
            <p style="margin-bottom: 12px;">Egészségügyi probléma, sérülés vagy rosszullét esetén azonnal hívd a kijelölt elsősegélynyújtókat (koppints a híváshoz):</p>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <a href="tel:+40745437184" style="display: flex; align-items: center; justify-content: space-between; background: rgba(38, 166, 154, 0.15); border: 1px solid #26a69a; color: #ffffff; padding: 10px 14px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 0.95em;">
                    <span>👩‍⚕️ Bencze Angéla</span>
                    <span style="color: #4db6ac; font-size: 1.05em;">📞 +40 745 437 184</span>
                </a>
                <a href="tel:+40746906753" style="display: flex; align-items: center; justify-content: space-between; background: rgba(38, 166, 154, 0.15); border: 1px solid #26a69a; color: #ffffff; padding: 10px 14px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 0.95em;">
                    <span>👩‍⚕️ Rozsondai Emőke</span>
                    <span style="color: #4db6ac; font-size: 1.05em;">📞 +40 746 906 753</span>
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# -----------------------------------------------------------------------------
# 6. MAIN PANEL - DASHBOARD
# -----------------------------------------------------------------------------
col_title1, col_title2 = st.columns([3, 1])
with col_title1:
    st.title("⛺ Nyári Tábor Kezelő Szoftver - 2026")
with col_title2:
    if st.button("📱 Mobil Táborozó App", key="btn_switch_to_mobile", help="Váltás a táborozók számára készült mobil alkalmazásra"):
        st.query_params["view"] = "tabor"
        st.session_state['mobile_mode'] = True
        st.rerun()

st.markdown("---")

# 4 KPI Cards at the top (Operational / Non-financial metrics for public dashboard)
registered_guests = len(df[df['Típus'] != 'Külsős'])
confirmed_guests = len(df[(df['Típus'] != 'Külsős') & (df['Státusz'] == 'Végleges')])
pending_guests = len(df[(df['Típus'] != 'Külsős') & (df['Státusz'] == 'Függőben')])
external_guests_count = len(df[df['Típus'] == 'Külsős'])

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
        <div class="kpi-title">Véglegesített Foglalások</div>
        <div class="kpi-value">{confirmed_guests} fő</div>
        <div class="kpi-sub">Jóváhagyott belső szállások</div>
    </div>
    <!-- Card 3 -->
    <div class="kpi-card" style="background: linear-gradient(135deg, #f12711 0%, #f5af19 100%);">
        <div class="kpi-title">Függőben Lévő Foglalások</div>
        <div class="kpi-value">{pending_guests} fő</div>
        <div class="kpi-sub">Bírálatra / helyre váró</div>
    </div>
    <!-- Card 4 -->
    <div class="kpi-card" style="background: linear-gradient(135deg, #8a2387 0%, #e94057 50%, #f27121 100%);">
        <div class="kpi-title">Külsős Vendégek</div>
        <div class="kpi-value">{external_guests_count} fő</div>
        <div class="kpi-sub">Napijegyesek / külsősök</div>
    </div>
</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)


# Warnings Section
has_pending_short = df[(df['Státusz'] == 'Függőben') & (df['Éjszakák Száma'] < 5) & (df['Típus'] != 'Külsős')]
if not has_pending_short.empty:
    st.warning("⚠️ **Figyelem:** Van olyan vendég, aki **csak pár napra** (kevesebb mint 5 éjszaka) jelentkezett! Státuszuk kötelezően **Függőben** marad. *Csak akkor véglegesíthető, ha marad hely a táborban!*")

# Financial warnings only visible for admin
if st.session_state.get('admin_unlocked'):
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
    st.info("📱 **Mobiltelefonról használnád?** Nyisd meg a kifejezetten mobilra optimált sub-linket: `https://fuzitabor.streamlit.app/?view=map` *(Vagy kattints a jobb felső **📱 Mobil Térkép Sub-link** gombra!)*")

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
                            save_positions_to_gsheets(BUILDING_GROUPS)
                            st.session_state['map_success_msg'] = "✅ Pozíciók sikeresen mentve (Google Táblázatba is)!"
                            st.rerun()

        if not _edit_mode:
            st.caption("💡 Kattints egy jelölőre a részletek megtekintéséhez, vagy új foglalás bejegyzéséhez.")
            
        # PDF Export Section directly below map
        st.markdown("---")
        pdf_col1, pdf_col2 = st.columns([3, 1])
        with pdf_col1:
            st.markdown("### 📄 Vendégnévsor & Ellátási Nyilvántartás (PDF)")
            st.caption("Töltsd le a tábor hivatalos vendég- és ellátás-nyilvántartását házakra és szobákra bontva (pénzügyi adatok nélkül).")
        with pdf_col2:
            if HAS_REPORTLAB:
                pdf_bytes = generate_guest_pdf(st.session_state.guests_df)
                if pdf_bytes:
                    st.download_button(
                        label="📄 PDF Letöltése",
                        data=pdf_bytes,
                        file_name="Tabor_Vendeglista_Es_Ellatas_2026.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.info("⌛ PDF modul felkészítése...")
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
            if row['Státusz'] == 'Függőben':
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
            st.info("Béla Ház: Max 8 fő. | Attila Ház: Max 8 fő (előfoglalt Ruzsáék).")
            
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
    external_guests = df[df['Típus'] == 'Külsős'].copy()
    if not external_guests.empty:
        for col in ['Külsős Reggelik Száma', 'Külsős Ebédek Száma', 'Külsős Vacsorák Száma']:
            if col not in external_guests.columns:
                external_guests[col] = 0
        st.subheader("🍽️ Külsős Étkezést Igénylők (Nem szállásosak)")
        st.dataframe(
            external_guests[['Név', 'Típus', 'Külsős Reggelik Száma', 'Külsős Ebédek Száma', 'Külsős Vacsorák Száma', 'Összköltség', 'Fizetett előleg', 'Előleg Státusz', 'Megjegyzés']],
            use_container_width=True,
            column_config={
                "Külsős Reggelik Száma": "Reggelik",
                "Külsős Ebédek Száma": "Ebédek",
                "Külsős Vacsorák Száma": "Vacsorák",
                "Összköltség": "Összköltség (RON)",
                "Fizetett előleg": "Fizetett előleg (RON)",
                "Előleg Státusz": "Előleg Ellenőrzés"
            }
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
                "Külsős Reggelik Száma": "Külsős Reggelik",
                "Külsős Ebédek Száma": "Külsős Ebédek",
                "Külsős Vacsorák Száma": "Külsős Vacsorák",
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
                "Fizetési Mód": st.column_config.SelectboxColumn("Fizetési Mód", options=["Utalás", "Vakációs Voucher", "Készpénz"], required=True),
                "Befizetés Dátuma": st.column_config.TextColumn("Befizetés Dátuma (ÉÉÉÉ-HH-NN)", help="A befizetés rögzítésének dátuma"),
                "Státusz": st.column_config.SelectboxColumn("Foglalás Státusza", options=["Végleges", "Függőben"], required=True),
                "Külsős Reggelik Száma": st.column_config.NumberColumn("Külsős Reggelik", min_value=0, max_value=10, step=1, default=0),
                "Külsős Ebédek Száma": st.column_config.NumberColumn("Külsős Ebédek", min_value=0, max_value=10, step=1, default=0),
                "Külsős Vacsorák Száma": st.column_config.NumberColumn("Külsős Vacsorák", min_value=0, max_value=10, step=1, default=0),
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
        
        # Financial KPI Cards inside Admin Panel
        fin_kpi_html = f"""
        <div class="kpi-container">
            <div class="kpi-card" style="background: linear-gradient(135deg, #3a7bd5 0%, #3a6073 100%);">
                <div class="kpi-title">Várható Tábori Bevétel</div>
                <div class="kpi-value">{total_income:,.0f} RON</div>
                <div class="kpi-sub">Összesített tábori részvételi díjak</div>
            </div>
            <div class="kpi-card" style="background: linear-gradient(135deg, #f12711 0%, #f5af19 100%);">
                <div class="kpi-title">Befizetett Előlegek</div>
                <div class="kpi-value">{total_collected:,.0f} RON</div>
                <div class="kpi-sub">Begyűjtött előlegek / összegek</div>
            </div>
            <div class="kpi-card" style="background: linear-gradient(135deg, #8a2387 0%, #e94057 50%, #f27121 100%);">
                <div class="kpi-title">Nettó Tábori Profit</div>
                <div class="kpi-value">{net_profit:,.0f} RON</div>
                <div class="kpi-sub">Bevétel - Kiadások (Bedő Laci + Tribel)</div>
            </div>
        </div>
        """
        st.markdown(fin_kpi_html, unsafe_allow_html=True)
        
        # Payment Method Breakdown KPI cards
        st.markdown("##### 💳 Befizetések Fizetési Módok Szerinti Bontásban")
        pay_transfer = 0.0
        pay_voucher = 0.0
        pay_cash = 0.0
        cnt_transfer = 0
        cnt_voucher = 0
        cnt_cash = 0
        
        all_tx_rows = []
        for idx_g, g in df.iterrows():
            txs = parse_payments_history(g)
            for i, tx in enumerate(txs):
                amt = float(tx.get('amount', 0.0))
                m = str(tx.get('method', 'Utalás'))
                if m == 'Készpénz':
                    pay_cash += amt
                    cnt_cash += 1
                elif m == 'Vakációs Voucher':
                    pay_voucher += amt
                    cnt_voucher += 1
                else:
                    pay_transfer += amt
                    cnt_transfer += 1
                    
                all_tx_rows.append({
                    'Vendég Neve': g['Név'],
                    'Szállás': g['Szállás'],
                    'Részlet #': f"#{i+1}",
                    'Befizetett Összeg (RON)': amt,
                    'Fizetési Mód': m,
                    'Befizetés Dátuma': tx.get('date', ''),
                    'Megjegyzés': tx.get('note', '')
                })

        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("🏦 Banki Utalás", f"{pay_transfer:,.0f} RON", delta=f"{cnt_transfer} részlet/tétel")
        m_col2.metric("🎟️ Vakációs Voucher", f"{pay_voucher:,.0f} RON", delta=f"{cnt_voucher} részlet/tétel")
        m_col3.metric("💵 Készpénz", f"{pay_cash:,.0f} RON", delta=f"{cnt_cash} részlet/tétel")

        # Payment Log / Date Register Section
        st.markdown("---")
        st.subheader("💳 Egyedi Befizetési Tételek Dátum Szerinti Jegyzéke")
        if all_tx_rows:
            tx_df = pd.DataFrame(all_tx_rows)
            tx_df = tx_df.sort_values(by='Befizetés Dátuma', ascending=False)
            st.dataframe(tx_df, use_container_width=True)
        else:
            st.info("Még nem történt előleg/befizetés bejegyzés a rendszerben.")
        st.markdown("---")
        
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
                "Összeg": [
                    f"{total_income:,.0f} RON",
                    f"{gross_payout_laci:,.0f} RON",
                    f"{total_tribel_lunch_cost:,.0f} RON",
                    f"{(gross_payout_laci + total_tribel_lunch_cost):,.0f} RON",
                    f"{net_profit:,.0f} RON"
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
        
        all_meals = ['T_D', 'W_B', 'W_L', 'W_D', 'Th_B', 'Th_L', 'Th_D', 'F_B', 'F_L', 'F_D', 'S_B', 'S_L', 'S_D', 'Su_BD', 'Su_L']
        
        for _, r in df.iterrows():
            g_type = r.get('Típus', 'Felnőtt')
            if g_type == 'Kisgyerek':
                continue
                
            is_child = (g_type == 'Gyerek') or bool(r.get('Gyermekmenü', False))
            suffix = '_K' if is_child else '_A'
            
            meals_str = r.get('Étkezések', 'ALL')
            meals_str_clean = str(meals_str).strip()
            if meals_str_clean in ['NONE', 'none', 'Nincs', 'nincs']:
                active = []
            elif not meals_str or meals_str_clean == 'ALL' or meals_str_clean == 'nan':
                active = all_meals
            else:
                active = [m.strip() for m in str(meals_str).split(',') if m.strip()]
                
            for m in active:
                if m == 'T_D':
                    days_data['Kedd (08.18)']['V' + suffix] += 1
                elif m == 'W_BD':
                    days_data['Szerda (08.19)']['R' + suffix] += 1
                    days_data['Szerda (08.19)']['V' + suffix] += 1
                elif m == 'W_B':
                    days_data['Szerda (08.19)']['R' + suffix] += 1
                elif m == 'W_D':
                    days_data['Szerda (08.19)']['V' + suffix] += 1
                elif m == 'W_L':
                    days_data['Szerda (08.19)']['E' + suffix] += 1
                elif m == 'Th_BD':
                    days_data['Csütörtök (08.20)']['R' + suffix] += 1
                    days_data['Csütörtök (08.20)']['V' + suffix] += 1
                elif m == 'Th_B':
                    days_data['Csütörtök (08.20)']['R' + suffix] += 1
                elif m == 'Th_D':
                    days_data['Csütörtök (08.20)']['V' + suffix] += 1
                elif m == 'Th_L':
                    days_data['Csütörtök (08.20)']['E' + suffix] += 1
                elif m == 'F_BD':
                    days_data['Péntek (08.21)']['R' + suffix] += 1
                    days_data['Péntek (08.21)']['V' + suffix] += 1
                elif m == 'F_B':
                    days_data['Péntek (08.21)']['R' + suffix] += 1
                elif m == 'F_D':
                    days_data['Péntek (08.21)']['V' + suffix] += 1
                elif m == 'F_L':
                    days_data['Péntek (08.21)']['E' + suffix] += 1
                elif m == 'S_BD':
                    days_data['Szombat (08.22)']['R' + suffix] += 1
                    days_data['Szombat (08.22)']['V' + suffix] += 1
                elif m == 'S_B':
                    days_data['Szombat (08.22)']['R' + suffix] += 1
                elif m == 'S_D':
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
