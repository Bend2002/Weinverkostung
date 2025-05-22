# leaderboard.py – Auswertung nach allen Weinen
import streamlit as st
import sqlite3
import os

DB = os.path.join(os.getcwd(), "wander.db")

# Teamdurchschnitt berechnen
def get_team_scores():
    with sqlite3.connect(DB) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                team TEXT
            )""")

        c.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                user TEXT, station_id INT,
                geschmack INT, alkohol REAL, preis REAL,
                land TEXT, rebsorte TEXT, aromen TEXT,
                kommentar TEXT,
                PRIMARY KEY(user, station_id))""")

        # Hole alle Nutzer mit Team
        users = dict(c.execute("SELECT username, team FROM users").fetchall())

        # Alle Bewertungen
        ratings = c.execute("SELECT user, station_id, geschmack FROM ratings").fetchall()

        # Scores aufsummieren pro Team
        team_scores = {}
        team_counts = {}
        for user, station, geschmack in ratings:
            team = users.get(user, "?")
            team_scores[team] = team_scores.get(team, 0) + geschmack
            team_counts[team] = team_counts.get(team, 0) + 1

        # Durchschnitt berechnen
        results = [(team, round(team_scores[team]/team_counts[team], 2)) for team in team_scores]
        return sorted(results, key=lambda x: -x[1])

def leaderboard_page():
    st.title("🏆 Team-Ranking")
    results = get_team_scores()
    if results:
        for i, (team, score) in enumerate(results, 1):
            st.markdown(f"**{i}. {team}** – Ø Geschmack: `{score}`")
    else:
        st.info("Noch keine Bewertungen vorhanden.")
