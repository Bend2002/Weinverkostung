# leaderboard.py – Auswertung nach allen Weinen (Gesamt & aktuelle Station)
import streamlit as st
import sqlite3
import os
from station import STATIONS

DB = os.path.join(os.getcwd(), "wander.db")

# Punktevergabe: pro korrektes Feld 1 Punkt
FELDER = ["herkunft", "rebsorte", "jahrgang"]

# Aromen zählen als Einzeltreffer

# Preis ±1€ gibt einen Punkt

def score_rating(row, wine):
    _, _, _, _, preis, land, rs, aromen, jahrgang, _ = row
    score = 0
    if land == wine["herkunft"]:
        score += 1
    if rs == wine["rebsorte"]:
        score += 1
    if jahrgang == wine["jahrgang"]:
        score += 1

    # Preis ±1
    if abs(preis - wine["preis"]) <= 1:
        score += 1

    # Aromen (jede richtige +1)
    echte = {a.strip() for a in wine["geschmack"].split(",")}
    getippt = {a.strip() for a in aromen.split(",")}
    score += len(echte & getippt)

    return score

def get_scores(for_station=None):
    with sqlite3.connect(DB) as c:
        c.row_factory = sqlite3.Row
        users = dict(c.execute("SELECT username, team FROM users").fetchall())
        query = "SELECT * FROM ratings"
        if for_station:
            query += f" WHERE station_id = {for_station}"
        ratings = c.execute(query).fetchall()

        scores = {}
        counts = {}

        for row in ratings:
            user = row["user"]
            team = users.get(user, "?")
            station_id = row["station_id"]
            wine = next((s for s in STATIONS if s["id"] == station_id), None)
            if not wine:
                continue
            punkte = score_rating(row, wine)
            scores[team] = scores.get(team, 0) + punkte
            counts[team] = counts.get(team, 0) + 1

        results = [(team, round(scores[team]/counts[team], 2)) for team in scores]
        return sorted(results, key=lambda x: -x[1])

def leaderboard_page():
    st.title("🏅 Team-Leaderboard")

    st.subheader("Aktuelle Station")
    current = STATIONS[-1]["id"] if STATIONS else None
    current_results = get_scores(for_station=current)
    if current_results:
        for i, (team, score) in enumerate(current_results, 1):
            st.markdown(f"**{i}. {team}** – Ø Punkte: `{score}`")
    else:
        st.info("Noch keine Bewertungen für diese Station.")

    st.subheader("Gesamtwertung")
    total_results = get_scores()
    if total_results:
        for i, (team, score) in enumerate(total_results, 1):
            st.markdown(f"**{i}. {team}** – Ø Punkte: `{score}`")
    else:
        st.info("Noch keine Bewertungen vorhanden.")
