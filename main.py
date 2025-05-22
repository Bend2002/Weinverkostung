# main.py – Auto-Login & Teamwahl separat
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

# Auto-Login über URL ?user=NAME
if "user" not in st.session_state:
    qp = st.query_params
    if "user" in qp:
        st.session_state["user"] = qp["user"]
        st.experimental_rerun()
    else:
        auth_page()
        st.stop()

user = st.session_state["user"]

# Team abfragen
with sqlite3.connect(DB_NAME) as conn:
    row = conn.execute("SELECT team FROM users WHERE username = ?", (user,)).fetchone()
    team = row[0] if row else None

# Wenn kein Team → Teamwahl anzeigen
if not team:
    team_page(user)
    st.stop()

# Sidebar & Navigation
with st.sidebar:
    st.markdown(f"👤 **{user}**\n🏷️ Team: `{team}`")
    menu = st.radio("Navigation", ["Wein-Bewertung", "Ranking"] + (["Admin"] if user == "admin" else []))
    if st.button("Logout"):
        del st.session_state["user"]
        st.experimental_rerun()

if menu == "Wein-Bewertung":
    station_page()
elif menu == "Ranking":
    leaderboard_page()
elif menu == "Admin" and user == "admin":
    admin_page()
