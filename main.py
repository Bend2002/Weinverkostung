# main.py – Navigation & Einstieg
import streamlit as st
import os
import sqlite3

from auth import auth_page
from station import station_page
from admin import admin_page

st.set_page_config(page_title="WanderWinzer", page_icon="🍷", layout="centered")

DB_NAME = os.path.join(os.getcwd(), "wander.db")

# DB-Init für Nutzer
with sqlite3.connect(DB_NAME) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            team TEXT
        )
    """)

# Wenn nicht eingeloggt → Login anzeigen
if "user" not in st.session_state:
    auth_page()
    st.stop()

# User & Team abrufen
user = st.session_state["user"]
with sqlite3.connect(DB_NAME) as conn:
    row = conn.execute("SELECT team FROM users WHERE username = ?", (user,)).fetchone()
    team = row[0] if row else "Unbekannt"

# Sidebar anzeigen
with st.sidebar:
    st.markdown(f"👤 **{user}**\n🏷️ Team: `{team}`")
    if st.button("Logout"):
        del st.session_state["user"]
        st.experimental_rerun()

# Weiterleitung zur richtigen Seite
if user == "admin":
    admin_page()
else:
    station_page()
