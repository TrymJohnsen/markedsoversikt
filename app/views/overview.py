import streamlit as st
import plotly.graph_objects as go

from plotly.subplots import make_subplots

def render_overview(active):
    snap = active.get("snap")
    hist = active.get("hist")

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
        showlegend=False
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

  
