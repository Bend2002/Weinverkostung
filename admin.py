# admin.py – Admin-Panel für Freigabe & Auswertung
import streamlit as st
from station import STATIONS, get_app_state, set_app_state

# Admin-Seite
def admin_page():
    st.title("🛠️ Admin – Steuerung")

    state = get_app_state()
    current = state.get("current_station", 0)
    mode = state.get("mode", "idle")

    st.markdown(f"**Aktuelle Station:** {current or '–'} | **Modus:** `{mode}`")

    station_options = [f"{w['id']}: {w['name']}" for w in STATIONS]
    sel = st.selectbox("Nächste Station auswählen", station_options, index=(current-1) if current else 0)
    sid = int(sel.split(":")[0])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚦 Voting starten"):
            set_app_state(current_station=sid, mode="vote")
            st.success(f"Station {sid} im Voting-Modus.")
            st.rerun()

    with col2:
        if st.button("🔍 Auflösung anzeigen"):
            if current == 0:
                st.warning("Es läuft keine Station.")
            else:
                set_app_state(mode="reveal")
                st.success("Auswertung aktiviert.")
                st.rerun()
