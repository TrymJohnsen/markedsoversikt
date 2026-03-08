import streamlit as st
import plotly.graph_objects as go

from plotly.subplots import make_subplots

from src.providers.yahoo import get_snapshot, get_price_history, get_fundamentals
from app.views.overview import render_overview
from app.views.technical import render_technical
# from app.views.fundamentals import render_fundamentals
# from app.views.notes import render_notes

st.set_page_config(page_title="Markedsoversikt", layout="wide")

st.title("Markedsoversikt")
st.caption("Søk ticker → se siste pris, fundamentals og enkel prisgraf.")

# minnet til appen
if "active" not in st.session_state:
    st.session_state["active"] = None #aktiv skal senere holde alt som er hentet for en ticker, slik at det kan brukes på tvers av faner uten å måtte hente på nytt
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = [] #enkel watchlist som kan brukes til å lagre tick feks ["AAPL", "MSFT"] 
if "notes" not in st.session_state:
    st.session_state["notes"] = {} #enkel struktur for å lagre notater per ticker, feks {"AAPL": "Dette er Apple..."}

view = st.sidebar.radio("Analyse", ["Oversikt", "Teknisk", "Fundamentals", "Notater/watchlist"])

# --- Input ---
with st.form("search_form"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        ticker = st.text_input("Ticker", value="AAPL").strip().upper()
    with col2:
        days = st.selectbox("Historikk", options=["5y","3y","1y", "6mo", "3mo", "1mo"], index=2)
    with col3:
        interval = st.selectbox("Interval", options=["1d", "1wk", "1mo"], index=1)

    submitted = st.form_submit_button("Hent data")

#når jeg trykker hent data, så hentes snapshot og prisdata og legges i session_state. Dette gjør at dataen er tilgjengelig for andre deler av appen uten å måtte hente på nytt.

if submitted:
    try:
        snap = get_snapshot(ticker)
        hist,hist_sma, meta = get_price_history(ticker, period=days, interval=interval)
        st.session_state["active"] = {
            "ticker": ticker,
            "days": days,
            "interval": interval,
            "snap": snap,
            "hist": hist,
            "meta": meta,
            "extended_hist": hist_sma, #inkluderer ekstra data for opp til SMA 200"
            "fundamentals": None,  # lazy-load
            "events": None,        # lazy-load
        }
    except Exception as e:
        st.error(f"Feil ved henting for {ticker}: {e}")
        st.exception(e) 
        st.info("Tips: prøv f.eks. AAPL, MSFT, TSLA, NHY.OL, EQNR.OL")
        st.stop()

if st.session_state["active"] is None:
    st.info("Søk på en ticker og trykk 'Hent data'.")
    st.stop()

active = st.session_state["active"]

if view == "Oversikt":
    render_overview(active)
elif view == "Teknisk":
    render_technical(active)
elif view == "Fundamentals":
    render_fundamentals(active)
elif view == "Notater/Watchlist":
    render_notes(active)
