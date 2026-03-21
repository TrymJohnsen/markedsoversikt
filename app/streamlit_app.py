import streamlit as st

from src.providers.yahoo import get_fundamentals, get_price_history, get_snapshot
from app.views.overview import render_overview
from app.views.technical import render_technical
# from app.views.fundamentals import render_fundamentals
# from app.views.notes import render_notes

PERIOD_OPTIONS = ["max", "5y", "3y", "1y", "6mo", "3mo", "1mo"]
INTERVAL_OPTIONS = ["1d", "1wk", "1mo"]
SHORT_RANGE_PERIODS = {"1mo", "3mo"}
LONG_RANGE_PERIODS = {"5y", "max"}


def default_interval_for_period(period: str) -> str:
    if period in SHORT_RANGE_PERIODS:
        return "1d"
    elif period in LONG_RANGE_PERIODS:
        return "1mo"
    else:
        return "1wk"


def sync_interval_to_period():
    st.session_state["search_interval"] = default_interval_for_period(st.session_state["search_days"])


st.set_page_config(page_title="Markedsoversikt", layout="wide")

st.title("Markedsoversikt")
st.caption("Søk på ticker og se siste pris, fundamentals og enkel prisgraf.")

# minnet til appen
if "active" not in st.session_state:
    st.session_state["active"] = None #aktiv skal senere holde alt som er hentet for en ticker, slik at det kan brukes pÃ¥ tvers av faner uten Ã¥ mÃ¥tte hente pÃ¥ nytt
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = [] #enkel watchlist som kan brukes til Ã¥ lagre tick feks ["AAPL", "MSFT"]
if "notes" not in st.session_state:
    st.session_state["notes"] = {} #enkel struktur for Ã¥ lagre notater per ticker, feks {"AAPL": "Dette er Apple..."}
if "search_ticker" not in st.session_state:
    st.session_state["search_ticker"] = "AAPL"
if "search_days" not in st.session_state:
    st.session_state["search_days"] = "1y"
if "search_interval" not in st.session_state:
    st.session_state["search_interval"] = default_interval_for_period(st.session_state["search_days"])

view = st.sidebar.radio("Analyse", ["Oversikt", "Teknisk", "Fundamentals", "Notater/Watchlist"])

# --- Input ---
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    st.text_input("Ticker", key="search_ticker")
with col2:
    st.selectbox("Historikk", options=PERIOD_OPTIONS, key="search_days", on_change=sync_interval_to_period)
with col3:
    st.selectbox("Interval", options=INTERVAL_OPTIONS, key="search_interval")
with col4:
    st.write("")
    st.write("")
    submitted = st.button("Hent data", use_container_width=True)

#nÃ¥r jeg trykker hent data, sÃ¥ hentes snapshot og prisdata og legges i session_state. Dette gjÃ¸r at dataen er tilgjengelig for andre deler av appen uten Ã¥ mÃ¥tte hente pÃ¥ nytt.

if submitted:
    try:
        ticker = st.session_state["search_ticker"].strip().upper()
        days = st.session_state["search_days"]
        interval = st.session_state["search_interval"]
        st.session_state["search_ticker"] = ticker

        snap = get_snapshot(ticker)
        hist, hist_sma, meta = get_price_history(ticker, period=days, interval=interval)
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
        st.info("Tips: Prøv f.eks. AAPL, MSFT, TSLA, NHY.OL, EQNR.OL")
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
