# main.py – Einstieg + Navigation (Auto-Login via ?user=NAME)
import streamlit as st
import sqlite3, os

from auth import auth_page, team_page
from station import station_page
from admin import admin_page
from leaderboard import leaderboard_page

st.set_page_config("WanderWinzer", "🍷", layout="centered")

DB = os.path.join(os.getcwd(), "wander.db")


# ---------- User aus URL ─ Auto-Login ----------
qp = st.query_params
if "user" in qp:
    # Immer in Session spiegeln
    st.session_state["user"] = qp["user"]

# ---------- Wenn kein User → Login-Maske ----------
if "user" not in st.session_state:
    auth_page()
    st.stop()

user = st.session_state["user"]

# ---------- Team prüfen ----------
with sqlite3.connect(DB) as c:
    row = c.execute(
        "SELECT team FROM users WHERE username=?", (user,)
    ).fetchone()
team = row[0] if row else None

if not team:
    team_page()       # noch kein Team → Auswahlseite
    st.stop()

# ---------- Sidebar ----------
with st.sidebar:
    st.success(f"👤 {user}\n🏷️ Team: {team}")
    nav = st.radio(
        "Navigation",
        ["Wein-Bewertung", "Ranking"] + (["Admin"] if user == "admin" else [])
    )
    if st.button("Logout"):
        st.query_params.clear()  # entfernt ?user=... aus URL
        del st.session_state["user"]
        st.rerun()

# ---------- Routing ----------
if nav == "Wein-Bewertung":
    station_page()
elif nav == "Ranking":
    leaderboard_page()
elif nav == "Admin":
    admin_page()
