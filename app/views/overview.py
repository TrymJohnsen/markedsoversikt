import streamlit as st
import plotly.graph_objects as go

from app.views.charts import build_price_fig

def render_overview(active):
    snap = active.get("snap")
    hist = active.get("hist")

    def format_financial(value):
        if value is None:
            return "-"

        value = float(value)

        if abs(value) >= 1_000_000_000_000:
            return f"{value / 1_000_000_000_000:.2f}T"
        elif abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif abs(value) >= 1_000:
            return f"{value / 1_000:.2f}K"
        else:
            return f"{value:.0f}"
        
    # --- Snapshot KPIs ---
    k4, k3, k2, k1 = st.columns(4)
    k4.metric("Navn", snap.get("name", ""))
    k3.metric("Markedsverdi", f"{format_financial(snap.get('market_cap'))}")
    k2.metric("Valuta", snap.get("currency"))
    k1.metric("Siste pris", snap.get("last_price"))
    
    st.divider()

    # --- chart types ---

    chart_type = st.radio("Graf", ["Linje", "Candlestick"], horizontal=True)

    fig,df,meta = build_price_fig(hist, snap.get("currency"), chart_type, show_volume=True, show_legend=True)

    if fig is None:
        st.warning("Ingen prisdata tilgjengelig for denne ticker/perioden.")
        return
    
    st.plotly_chart(fig,use_container_width=True)
