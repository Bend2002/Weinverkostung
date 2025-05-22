# main.py – Steuerung der App
import streamlit as st
import os
import sqlite3

from auth import auth_page, team_page
from station import station_page
from leaderboard import leaderboard_page
from admin import admin_page

DB_FILE = os.path.join(os.getcwd(), "wander.db")

st.set_page_config("WanderWinzer", "🍷", layout="centered")

# Datenbank vorbereiten
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        team TEXT
    )
""")
c.execute("""
    CREATE TABLE IF NOT EXISTS ratings (
        user TEXT, station_id INT,
        geschmack INT, alkohol REAL, preis REAL,
        land TEXT, rebsorte TEXT, aromen TEXT,
        kommentar TEXT,
        PRIMARY KEY(user, station_id)
    )
""")
conn.commit()
conn.close()

# Benutzername aus URL (z. B. /?user=max)
query_params = st.query_params
if "user" in query_params:
    st.session_state["user"] = query_params["user"]

# Authentifizierung
if "user" not in st.session_state:
    auth_page()
    st.stop()

# Benutzername ermitteln
user = st.session_state["user"]

# Team auslesen
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
row = c.execute("SELECT team FROM users WHERE username = ?", (user,)).fetchone()
conn.close()
if row is None:
    team_page()
    st.stop()
team = row[0]

# Navigation
st.sidebar.success(f"Eingeloggt als {user} | Team: {team}")
if st.sidebar.button("Logout"):
    del st.session_state["user"]
    st.query_params.clear()
    st.experimental_rerun()

# Seitenwahl
if user == "admin":
    admin_page()
elif st.sidebar.button("Leaderboard"):
    leaderboard_page()
else:
    station_page()
