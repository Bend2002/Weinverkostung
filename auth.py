# auth.py – Login & Registrierung
import streamlit as st
import sqlite3, os

DB = os.path.join(os.getcwd(), "wander.db")

# ───── DB Init ─────
def _conn():
    return sqlite3.connect(DB, check_same_thread=False)

def create_user_table():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                team TEXT
            )
        """)

# ───── Auth Logic ─────
def register_user(username, password, team):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO users (username, password, team) VALUES (?, ?, ?)", (username, password, team))
        c.commit()

def login_user(username, password):
    with _conn() as c:
        res = c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        return res is not None

def auth_page():
    create_user_table()
    st.title("🔐 Login / Registrierung")

    mode = st.radio("Was möchtest du tun?", ["Einloggen", "Registrieren"])
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort (nur Zahlen, min. 3)", type="password")

    if mode == "Registrieren":
        team = st.text_input("Teamname")
        if st.button("Registrieren"):
            if len(password) < 3 or not password.isdigit():
                st.error("Bitte ein Passwort mit mindestens 3 Ziffern eingeben.")
            elif not username or not team:
                st.error("Bitte Benutzername und Team angeben.")
            else:
                register_user(username, password, team)
                st.success("Registrierung erfolgreich. Bitte einloggen.")

    else:  # Einloggen
        if st.button("Einloggen"):
            if login_user(username, password):
                st.session_state["user"] = username
                st.success("Login erfolgreich.")
                st.experimental_rerun()
            else:
                st.error("Login fehlgeschlagen. Bitte prüfen.")
