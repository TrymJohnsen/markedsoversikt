import streamlit as st
import plotly.graph_objects as go

from plotly.subplots import make_subplots

from src.providers.yahoo import get_snapshot, get_price_history, get_fundamentals

st.set_page_config(page_title="Markedsoversikt", layout="wide")

st.title("Markedsoversikt")
st.caption("Søk ticker → se siste pris, fundamentals og enkel prisgraf.")

# minnet til appen
if "data" not in st.session_state:
    st.session_state["data"] = None #her lagres snapshot og prisdata for siste søkte ticker

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
if  submitted:
    snap = get_snapshot(ticker)
    hist = get_price_history(ticker, period=days, interval=interval)
    st.session_state["data"] = {"snap": snap, "hist": hist}

# fetch når knappen trykkes
if st.session_state["data"] is None:
    st.info("Søk på en ticker og trykk 'Hent data'.")
else:
    try:
        snap = st.session_state["data"]["snap"]
        hist = st.session_state["data"]["hist"]  # forventer DataFrame med Date-index + Close/Adj Close

        # --- Snapshot KPIs ---
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Siste pris", snap.get("last_price"))
        k2.metric("Valuta", snap.get("currency"))
        k3.metric("Markedsverdi", snap.get("market_cap"))
        k4.metric("Navn", snap.get("name", ""))

        st.divider()

        # --- chart types ---

        chart_type = st.radio("Graf", ["Linje", "Candlestick"], horizontal=True)

        # --- Chart ---
        st.subheader("Prisgraf")

        df = hist.copy().sort_index()  # sørg for at data er sortert etter dato
        df.index = df.index.tz_localize(None) if getattr(df.index, 'tz', None) else df.index  # fjern timezone hvis den finnes

        if len(df) == 0:
            st.warning("Ingen prisdata tilgjengelig for denne ticker/perioden.")
        else:
            fig = go.Figure()

            har_volum = "Volume" in df.columns

            rows = 2 if har_volum else 1
            row_heights = [0.75, 0.25] if har_volum else [1]

            fig = make_subplots(
                rows = rows,
                cols = 1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=row_heights,
            )
            
            if chart_type == "Candlestick":
                required = {"Open", "High", "Low", "Close"}
                if required.issubset(df.columns):
                    fig.add_trace(go.Candlestick(
                        x=df.index,
                        open = df["Open"],
                        high = df["High"],
                        low = df["Low"],
                        close = df["Close"],
                        name="OHLC" #OHLC = Open-High-Low-Close
                    ), row=1, col=1
                    )
                else: 
                    st.warning("Candlestick-graf krever at data inneholder Open, High, Low og Close. Viser linjegraf i stedet.")
                    price_col = "Adj Close" if "Adj Close" in df.columns else "Close"
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df[price_col],
                            mode="lines",
                            name=price_col,
                        ),
                        row=1, col=1
                    )
            else: # Linje
                price_col = "Adj Close" if "Adj Close" in df.columns else "Close"
                fig.add_trace(go.Scatter(
                    x = df.index,
                    y = df[price_col],
                    mode = "lines",
                    name = price_col,
                ), row=1, col=1
                )
            
            # -- volum trace (rad 2)--
            if har_volum:
                fig.add_trace(
                    go.Bar(
                        x=df.index,
                        y=df["Volume"],
                        marker=dict(color="rgba(150,150,150,0.25)"),
                        opacity=0.3,
                        name="Volum",
                        hovertemplate="Dato=%{x}<br>Volum=%{y:,}<extra></extra>",
                    ), row = 2, col=1
                )

        fig.update_layout(
            height=600 if har_volum else 500,
            xaxis_title="Dato",
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=True
        )
        
        # horisontal divider mellom pris og volum
        fig.add_shape(
            type = "line",
            x0 = 0,
            x1 = 1,
            y0 = 0.25,
            y1 = 0.25,
            xref = "paper",
            yref = "paper",
            line = dict(color="gray", width=1, dash="dash")
        )

        #aksetitler
        fig.update_yaxes(title_text=f"Pris ({snap.get('currency', '')})", row=1, col=1)
        if har_volum:
            fig.update_yaxes(title_text="Volum", row=2, col=1)

        st.plotly_chart(fig,use_container_width=True)


    except Exception as e:
        st.error(f"Feil ved henting for {ticker}: {e}")
        st.exception(e) 
        st.info("Tips: prøv f.eks. AAPL, MSFT, TSLA, NHY.OL, EQNR.OL")