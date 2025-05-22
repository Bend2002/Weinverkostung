# main.py – Einstiegspunkt & Navigation mit URL-Login
import streamlit as st
import os
import sqlite3

from auth import auth_page, team_page
from station import station_page
from admin import admin_page
from leaderboard import leaderboard_page

st.set_page_config(page_title="WanderWinzer", page_icon="🍷", layout="centered")

DB_NAME = os.path.join(os.getcwd(), "wander.db")

def init_users():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                team TEXT
            )
        """)

init_users()

# Login per URL (?user=name)
query = st.query_params
if "user" in query:
    user = query["user"]
    st.session_state["user"] = user
else:
    auth_page()
    st.stop()

# Team auslesen
user = st.session_state["user"]
with sqlite3.connect(DB_NAME) as conn:
    row = conn.execute("SELECT team FROM users WHERE username = ?", (user,)).fetchone()
    team = row[0] if row else None

# Wenn noch kein Team vergeben → Teamseite zeigen
if not team:
    team_page(user)
    st.stop()

# Sidebar Navigation
with st.sidebar:
    st.markdown(f"👤 **{user}**\n🏷️ Team: `{team}`")
    menu = st.radio("Navigation", ["Wein-Bewertung", "Ranking"] + (["Admin"] if user == "admin" else []))
    if st.button("Logout"):
        st.query_params.clear()
        st.rerun()

# Navigation weiterleiten
if menu == "Wein-Bewertung":
    station_page()
elif menu == "Ranking":
    leaderboard_page()
elif menu == "Admin" and user == "admin":
    admin_page()
