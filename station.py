# station.py – Bewertung & Auflösung
import streamlit as st
import sqlite3
import os

DB = os.path.join(os.getcwd(), "wander.db")

# Weinliste (Beispiel – erweiterbar)
STATIONS = [
    {"id": 1, "name": "Lenotti Custoza", "jahrgang": 2023, "herkunft": "Italien", "rebsorte": "Cuvée", "farbe": "Weiß", "alkohol": 12.0, "preis": 6.95, "aromen": "Apfel, Limette, Mineral"},
    {"id": 2, "name": "Rio Lindo Syrah", "jahrgang": 2023, "herkunft": "Spanien", "rebsorte": "Syrah", "farbe": "Rot", "alkohol": 13.5, "preis": 6.95, "aromen": "Brombeere, Pflaume, Würze"}
]

LÄNDER = sorted({w["herkunft"] for w in STATIONS})
REBSORT = sorted({w["rebsorte"] for w in STATIONS})
AROMEN = sorted({a.strip() for w in STATIONS for a in w.get("aromen", "").split(",") if a.strip()})

FLAG = {"Italien": "🇮🇹", "Spanien": "🇪🇸"}

# DB-Funktionen

def _conn():
    return sqlite3.connect(DB, check_same_thread=False)

def get_state():
    with _conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS app_state (key TEXT PRIMARY KEY, value TEXT)")
        return {k: (int(v) if str(v).isdigit() else v) for k, v in c.execute("SELECT key,value FROM app_state")}

def set_state(**kw):
    with _conn() as c:
        for k, v in kw.items():
            c.execute("INSERT OR REPLACE INTO app_state VALUES (?,?)", (k, str(v)))
        c.commit()

get_app_state = get_state
set_app_state = set_state

def save_rating(user, sid, g, a, p, land, rs, aromen, note):
    with _conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS ratings (
            user TEXT, station_id INT,
            geschmack INT, alkohol REAL, preis REAL,
            land TEXT, rebsorte TEXT, aromen TEXT,
            kommentar TEXT,
            PRIMARY KEY(user, station_id))""")
        c.execute("INSERT OR REPLACE INTO ratings VALUES (?,?,?,?,?,?,?,?,?)",
                  (user, sid, g, a, p, land, rs, aromen, note))
        c.commit()

def get_rating(user, sid):
    with _conn() as c:
        return c.execute("SELECT * FROM ratings WHERE user=? AND station_id=?", (user, sid)).fetchone()

# Hauptseite

def station_page():
    user = st.session_state["user"]
    state = get_state()
    sid = state.get("current_station", 0)
    mode = state.get("mode", "idle")

    if sid == 0:
        st.info("Noch keine Station freigegeben.")
        return

    wine = next((w for w in STATIONS if w["id"] == sid), None)
    if not wine:
        st.error("Station nicht gefunden.")
        return

    st.header(f"🍷 Station {sid}" + ("" if mode == "vote" else f": {wine['name']}"))

    if mode == "vote":
        g = st.slider("Geschmack (0 = Plörre, 10 = Göttlich)", 0, 10, 5)
        a = st.slider("Alkohol %", 0.0, 16.0, 12.0, step=0.1)
        p = st.slider("Preis‑Tipp (€)", 0.0, 35.0, 10.0, step=0.5)
        land = st.selectbox("Land", [f"{FLAG.get(x, '')} {x}" for x in LÄNDER])
        rs = st.selectbox("Rebsorte", REBSORT)
        aromen_sel = st.multiselect("Aromen", AROMEN)
        note = st.text_area("Kommentar")

        if st.button("Speichern"):
            save_rating(user, sid, g, a, p, land.split(" ", 1)[-1], rs, ", ".join(aromen_sel), note)
            st.success("Gespeichert!")

    elif mode == "reveal":
        row = get_rating(user, sid)
        if not row:
            st.warning("Du hast nichts abgegeben.")
            return

        st.subheader("🔍 Auflösung")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Echter Wein")
            st.write(f"**Name:** {wine['name']}")
            st.write(f"**Jahrgang:** {wine.get('jahrgang', '-')}")
            st.write(f"**Herkunft:** {wine.get('herkunft', '-')}")
            st.write(f"**Rebsorte:** {wine.get('rebsorte', '-')}")
            st.write(f"**Farbe:** {wine.get('farbe', '-')}")
            st.write(f"**Alkohol:** {wine.get('alkohol', '-')} %")
            st.write(f"**Preis:** {wine.get('preis', '-')} €")
            if wine.get("aromen"):
                st.write(f"**Aromen:** {wine['aromen']}")

        with col2:
            st.markdown("### Dein Tipp")
            st.write(f"**Geschmack:** {row[2]} / 10")
            st.write(f"**Alkohol getippt:** {row[3]} %")
            st.write(f"**Preis getippt:** {row[4]} €")
            st.write(f"**Land:** {row[5]}")
            st.write(f"**Rebsorte:** {row[6]}")
            if row[7]:
                st.write(f"**Aromen:** {row[7]}")
            if row[8]:
                st.write(f"**Kommentar:** {row[8]}")

    else:
        st.info("Warte, bis der Admin das Voting startet.")
