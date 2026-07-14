import re

with open(r'c:\Users\Nagy H Lajos\.gemini\antigravity\TABOR\app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

# 1. Add components import at the top
if 'import streamlit.components.v1 as components' not in app_code:
    app_code = app_code.replace('import streamlit as st', 'import streamlit as st\nimport streamlit.components.v1 as components')

# 2. Define the map component
component_definition = """
# -----------------------------------------------------------------------------
# MAP COMPONENT DEFINITION
# -----------------------------------------------------------------------------
try:
    map_component = components.declare_component("map_component", path="tabor_map_component")
except Exception:
    map_component = None
"""
if 'MAP COMPONENT DEFINITION' not in app_code:
    app_code = app_code.replace('# 3. BUSINESS LOGIC & PRICING ENGINE', component_definition + '\n# 3. BUSINESS LOGIC & PRICING ENGINE')

# 3. Remove generate_map_html entirely (it's between 510 and 1060 approximately)
app_code = re.sub(r'def generate_map_html.*?return \(\n        \'<!DOCTYPE html>.*?</html>\'\n    \)', '', app_code, flags=re.DOTALL)

# 4. Remove the old query params handler
old_query_params = r"""# -----------------------------------------------------------------------------
# 3c\. QUERY PARAMS HANDLER
# -----------------------------------------------------------------------------.*?st\.query_params\.clear\(\)"""
app_code = re.sub(old_query_params, '', app_code, flags=re.DOTALL)

# 5. Fix the edit_booking dialog (we can remove it entirely since it's redundant with manage_building_bookings)
old_edit_booking = r"""@st\.dialog\("🏡 Foglalás Módosítása"\)\ndef edit_booking.*?st\.rerun\(\)"""
app_code = re.sub(old_edit_booking, '', app_code, flags=re.DOTALL)

# 6. Fix manage_building_bookings
# Remove the old if 'tabor_selected_building' in st.query_params at the end of the map render
old_map_render = r"""        _map_html = generate_map_html\(_img_b64, _bstatus, edit_mode=_edit_mode, base_url=_base_url\)
        st\.components\.v1\.html\(_map_html, height=560 if _edit_mode else 520, scrolling=False\)

        if 'tabor_selected_building' in st\.query_params:
            selected_bid = st\.query_params\.get\('tabor_selected_building', ''\)
            if selected_bid in BUILDING_GROUPS:
                manage_building_bookings\(selected_bid\)"""

new_map_render = """        # Use custom map component
        if map_component:
            map_result = map_component(img_b64=_img_b64, status=_bstatus, edit_mode=_edit_mode, key="tabor_map_widget")
            if map_result:
                if map_result.get("action") == "click":
                    manage_building_bookings(map_result.get("bid"))
                elif map_result.get("action") == "save_positions":
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
                        st.rerun()"""

app_code = app_code.replace(old_map_render, new_map_render)

# 7. Remove save_positions_callback (redundant now)
save_pos_callback_regex = r'        def save_positions_callback\(\):.*?st\.session_state\[\'map_error_msg\'\] = f"Hiba a pozíciók mentése során: \{e\}"'
app_code = re.sub(save_pos_callback_regex, '', app_code, flags=re.DOTALL)

# 8. Update edit mode button
app_code = app_code.replace('st.button("💾 Végleges Pozíciók Mentése", type="primary", on_click=save_positions_callback)', '')
app_code = app_code.replace('st.info("✋ **Szerkesztési mód aktív.** Húzd a jelölőket a térképen a helyükre, majd kattints az alábbi gombra!")', 'st.info("✋ **Szerkesztési mód aktív.** Húzd a jelölőket a térképen a helyükre, majd a térkép alatti Mentés gombbal mentsd!")')

# 9. Clean up manage_building_bookings: remove st.query_params references
app_code = app_code.replace('st.query_params.clear()', '')

with open(r'c:\Users\Nagy H Lajos\.gemini\antigravity\TABOR\app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("Updates applied to app.py")
