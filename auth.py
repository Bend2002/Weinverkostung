# auth.py – Login & Registrierung mit URL-Login-Link
import streamlit as st
import sqlite3, os

DB = os.path.join(os.getcwd(), "wander.db")

def ensure_user_table():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                team TEXT
            )""")

def login_user(username, password):
    with sqlite3.connect(DB) as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                          (username, password)).fetchone()
        return row is not None

def register_user(username, password):
    with sqlite3.connect(DB) as conn:
        try:
            conn.execute("INSERT INTO users (username, password, team) VALUES (?, ?, '')",
                         (username, password))
            return True
        except sqlite3.IntegrityError:
            return False

def auth_page():
    ensure_user_table()
    st.title("🔐 Login / Registrierung")

    query = st.query_params
    if "user" in query:
        st.session_state["user"] = query["user"]
        return

    mode = st.radio("Was möchtest du tun?", ["Einloggen", "Registrieren"])
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort (min. 3 Ziffern)", type="password")

    if st.button(mode):
        if len(password) < 3:
            st.warning("Passwort zu kurz.")
            return

        if mode == "Registrieren":
            if register_user(username, password):
                st.query_params["user"] = username
                st.rerun()
            else:
                st.error("Benutzername existiert bereits.")

        elif mode == "Einloggen":
            if login_user(username, password):
                st.query_params["user"] = username
                st.rerun()
            else:
                st.error("Login fehlgeschlagen.")
