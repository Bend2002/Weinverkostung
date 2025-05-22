# leaderboard.py – Punktwertung pro Station + Gesamtschnitt
import streamlit as st
import sqlite3, os
from station import STATIONS, get_app_state

DB = os.path.join(os.getcwd(), "wander.db")

# ----- Scoring‑Funktion -------------------------------------

def score_rating(rating_row, wine):
    """Berechne Punkte für einen Rating‑Datensatz.
    rating_row = (user, station_id, geschmack, alkohol, preis, land, rebsorte, aromen, kommentar)
    """
    _, _, _, _, preis_tipp, land_tipp, rs_tipp, aromen_tipp, _ = rating_row
    score = 0

    # Land, Rebsorte, Farbe, Jahrgang
    if land_tipp == wine["herkunft"]:      # 1 Punkt
        score += 1
    if rs_tipp == wine["rebsorte"]:
        score += 1
    # Farbe und Jahrgang optional im UI – falls später ergänzt
    if str(wine.get("farbe")) and str(wine.get("farbe")) in land_tipp:
        score += 0  # Platzhalter – Farbe derzeit nicht abgefragt
    # Jahrgang nicht getippt -> 0 Punkte

    # Aromen – jeder Treffer 1 Punkt
    if aromen_tipp:
        guessed = {a.strip() for a in aromen_tipp.split(",") if a.strip()}
        true_set = {a.strip() for a in wine.get("aromen", "").split(",")}
        score += len(guessed & true_set)

    # Preis ±1 €
    if preis_tipp is not None and abs(preis_tipp - wine["preis"]) <= 1:
        score += 1

    return score

# ----- Team‑Scores ------------------------------------------

def calc_scores():
    with sqlite3.connect(DB) as c:
        users = dict(c.execute("SELECT username, team FROM users").fetchall())
        ratings = c.execute("SELECT * FROM ratings").fetchall()

    # Aktueller Spielstand
    state = get_app_state()
    current_sid = state.get("current_station", 0)

    team_current = {}
    team_total   = {}
    team_cnt_cur = {}
    team_cnt_tot = {}

    for row in ratings:
        user, sid = row[0], row[1]
        team = users.get(user, "?")
        wine = next((w for w in STATIONS if w["id"] == sid), None)
        if not wine:
            continue
        pts = score_rating(row, wine)

        # Gesamt
        team_total[team] = team_total.get(team, 0) + pts
        team_cnt_tot[team] = team_cnt_tot.get(team, 0) + 1

        # Aktuelle Station
        if sid == current_sid:
            team_current[team] = team_current.get(team, 0) + pts
            team_cnt_cur[team] = team_cnt_cur.get(team, 0) + 1

    leaderboard = []
    for team in team_total:
        avg_total = round(team_total[team]/team_cnt_tot[team], 2)
        avg_cur   = (round(team_current[team]/team_cnt_cur[team], 2)
                     if team in team_current else 0)
        leaderboard.append((team, avg_cur, avg_total))

    # Sortierung: erst aktuelle Station, dann Gesamt
    return sorted(leaderboard, key=lambda x: (-x[1], -x[2]))

# ----- Streamlit‑Seite --------------------------------------

def leaderboard_page():
    st.title("🏆 Team‑Punkte")

    data = calc_scores()
    if not data:
        st.info("Noch keine Bewertungen vorliegend.")
        return

    st.markdown("| Rang | Team | Punkte aktuell | Gesamt‑Ø |\n|-----|-----|---------------|-----------|")
    for idx, (team, cur, ges) in enumerate(data, 1):
        st.markdown(f"| {idx} | {team} | {cur} | {ges} |")

    if st.button("🔄 Aktualisieren"):
        st.rerun()
