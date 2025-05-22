# auth.py – Login / Registrierung + Team-Auswahl + Auto-URL-Login
import streamlit as st
import sqlite3, os

DB = os.path.join(os.getcwd(), "wander.db")


# ---------- DB-Hilfen ----------
def _conn():
    return sqlite3.connect(DB, check_same_thread=False)


def ensure_tables():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                team     TEXT
            )
        """)
ensure_tables()


# ---------- User-Funktionen ----------
def login_user(name, pw):
    with _conn() as c:
        row = c.execute(
            "SELECT 1 FROM users WHERE username=? AND password=?",
            (name, pw)
        ).fetchone()
        return row is not None


def register_user(name, pw):
    try:
        with _conn() as c:
            c.execute(
                "INSERT INTO users (username, password, team) VALUES (?,?, '')",
                (name, pw)
            )
        return True
    except sqlite3.IntegrityError:
        return False


def set_team(name, team):
    with _conn() as c:
        c.execute("UPDATE users SET team=? WHERE username=?", (team, name))
        c.commit()


def existing_teams():
    with _conn() as c:
        return sorted(
            t for (t,) in c.execute(
                "SELECT DISTINCT team FROM users WHERE team!=''"
            ).fetchall()
        )


# ---------- Pages ----------
def auth_page():
    """Login-/Registrierungs-Maske.

    • Bei Erfolg → ?user=NAME in die URL schreiben, damit Auto-Login greift
    """
    st.title("🔐 Login / Registrierung")

    mode = st.radio("Was möchtest du tun?", ["Einloggen", "Registrieren"])
    name = st.text_input("Benutzername")
    pw   = st.text_input("Passwort (≥3 Ziffern)", type="password")

    if st.button(mode):
        if len(pw) < 3 or not pw.isdigit():
            st.error("Passwort muss aus mind. 3 Ziffern bestehen.")
            return

        if mode == "Registrieren":
            if register_user(name, pw):
                st.query_params["user"] = name
                st.rerun()
            else:
                st.error("Benutzername existiert bereits.")
        else:  # Einloggen
            if login_user(name, pw):
                st.query_params["user"] = name
                st.rerun()
            else:
                st.error("Login fehlgeschlagen.")


def team_page():
    """Wird angezeigt, wenn user eingeloggt, aber noch keinem Team zugeordnet."""
    st.title("👥 Team auswählen / erstellen")

    name = st.session_state["user"]
    teams = existing_teams()

    st.subheader("Bestehendem Team beitreten")
    team_sel = st.selectbox("Teams", teams) if teams else None
    if st.button("➡️ Beitreten") and team_sel:
        set_team(name, team_sel)
        st.rerun()

    st.subheader("Neues Team anlegen")
    new_team = st.text_input("Teamname")
    if st.button("✨ Team erstellen") and new_team:
        set_team(name, new_team.strip())
        st.rerun()
