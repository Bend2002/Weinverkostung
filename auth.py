# auth.py – Login & Teamzuweisung getrennt
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
def register_user(username, password):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO users (username, password, team) VALUES (?, ?, '')", (username, password))
        c.commit()

def login_user(username, password):
    with _conn() as c:
        res = c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        return res is not None

def set_team(username, team):
    with _conn() as c:
        c.execute("UPDATE users SET team=? WHERE username=?", (team, username))
        c.commit()

def get_existing_teams():
    with _conn() as c:
        teams = [r[0] for r in c.execute("SELECT DISTINCT team FROM users WHERE team != ''")]
        return sorted(teams)

# ───── Streamlit Pages ─────
def auth_page():
    create_user_table()
    st.title("🔐 Login / Registrierung")

    mode = st.radio("Was möchtest du tun?", ["Einloggen", "Registrieren"])
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort (min. 3 Ziffern)", type="password")

    if mode == "Registrieren":
        if st.button("Registrieren"):
            if len(password) < 3 or not password.isdigit():
                st.error("Bitte ein Passwort mit mindestens 3 Ziffern eingeben.")
            elif not username:
                st.error("Bitte Benutzernamen angeben.")
            else:
                register_user(username, password)
                st.success("Registriert. Jetzt einloggen.")

    else:
        if st.button("Einloggen"):
            if login_user(username, password):
                st.session_state["user"] = username
                st.experimental_rerun()
            else:
                st.error("Login fehlgeschlagen.")

def team_page(user):
    st.title("👥 Team beitreten oder erstellen")

    existing = get_existing_teams()
    col1, col2 = st.columns(2)
    with col1:
        choice = st.selectbox("Bestehendem Team beitreten", existing)
        if st.button("Beitreten"):
            set_team(user, choice)
            st.experimental_rerun()

    with col2:
        new_team = st.text_input("Neues Team erstellen")
        if st.button("Erstellen") and new_team:
            set_team(user, new_team.strip())
            st.experimental_rerun()
