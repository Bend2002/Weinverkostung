# station.py – Bewertung & Auflösung
import streamlit as st
import sqlite3
import os

DB = os.path.join(os.getcwd(), "wander.db")

# station.py – direkte Einfügestelle
STATIONS = [
    {"id": 1,  "name": "Lenotti Custoza",                          "jahrgang": 2023, "herkunft": "Italien",     "rebsorte": "Garganega / Trebbiano / Cortese",           "farbe": "Weiß", "preis": 6.95, "alkohol": 12.0, "aromen": "Apfel, Melone, Limette, Mineral"},
    {"id": 2,  "name": "Rio Lindo Syrah",                          "jahrgang": 2023, "herkunft": "Spanien",     "rebsorte": "Syrah",                                     "farbe": "Rot",  "preis": 6.95, "alkohol": None, "aromen": "Brombeere, Pflaume, Würze"},
    {"id": 3,  "name": "Trebbiano d’Abruzzo Bio (Cantina Tollo)",  "jahrgang": 2024, "herkunft": "Italien",     "rebsorte": "Trebbiano",                                 "farbe": "Weiß", "preis": 8.00, "alkohol": None, "aromen": "Apfel, Zitrus, Mandel"},
    {"id": 4,  "name": "Mario Collina Primitivo Rosato",           "jahrgang": 2023, "herkunft": "Italien",     "rebsorte": "Primitivo",                                 "farbe": "Rosé", "preis": 2.29, "alkohol": None, "aromen": "Erdbeere, Kirsche, Himbeere"},
    {"id": 5,  "name": "Alegrete Vinho Verde",                     "jahrgang": 2023, "herkunft": "Portugal",    "rebsorte": "Loureiro / Trajadura / Arinto",             "farbe": "Weiß", "preis": 2.95, "alkohol": None, "aromen": "Zitrone, Ananas, Mango, Mineral"},
    {"id": 6,  "name": "Pierre Amadieu Ventoux “La Claretière”",   "jahrgang": 2021, "herkunft": "Frankreich",  "rebsorte": "Grenache / Syrah",                          "farbe": "Rot",  "preis": 8.95, "alkohol": 14.0, "aromen": "Kirsche, schwarze Johannisbeere, Kräuter, Pfeffer"},
    {"id": 7,  "name": "Margarethenhof Saar Riesling",             "jahrgang": 2022, "herkunft": "Deutschland", "rebsorte": "Riesling",                                 "farbe": "Weiß", "preis": 9.95, "alkohol": 11.0, "aromen": "Grüner Apfel, Pfirsich, Schiefer"},
    {"id": 8,  "name": "Kühling-Gillot “Hase” Sauvignon Blanc",    "jahrgang": 2023, "herkunft": "Deutschland", "rebsorte": "Sauvignon Blanc",                           "farbe": "Weiß", "preis": 8.95, "alkohol": 11.5, "aromen": "Stachelbeere, Johannisbeere, frisches Gras"},
    {"id": 9,  "name": "Château La Genestière Côtes du Rhône blanc","jahrgang": 2022,"herkunft": "Frankreich",  "rebsorte": "Grenache Blanc / Viognier / Clairette",     "farbe": "Weiß", "preis": 6.95, "alkohol": 13.5, "aromen": "Steinobst, weiße Blüten, Honig"},
    {"id": 10, "name": "Vino Blanco de España (Bag-in-Box)",       "jahrgang": 2022, "herkunft": "Spanien",     "rebsorte": "Blend (Airén / Macabeo …)",                 "farbe": "Weiß", "preis": 1.25, "alkohol": None, "aromen": "Zitrus, Apfel"}
]

LÄNDER = sorted({w["herkunft"] for w in STATIONS})
REBSORT = sorted({w["rebsorte"] for w in STATIONS})
AROMEN = sorted({a.strip() for w in STATIONS for a in w.get("aromen", "").split(",") if a.strip()})

FLAG = {"Deutschland":"🇩🇪","Frankreich":"🇫🇷","Italien":"🇮🇹","Spanien":"🇪🇸","Portugal":"🇵🇹","Niederlande":"🇳🇱","Chile":"🇨🇱"}

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
