import streamlit as st
import plotly.graph_objects as go

from app.views.charts import build_price_fig

def render_technical(active):
    snap = active.get("snap")
    hist = active.get("hist")
    hist_extended = active.get("extended_hist")
    
    st.subheader(f"Teknisk analyse for {snap.get('name', '')} ({snap.get('ticker', '')})")

    fig,df,meta = build_price_fig(hist, snap.get("currency"), chart_type="Line", show_volume=False, show_legend=True)

    if fig is None:
        st.warning("Ingen prisdata tilgjengelig for denne ticker/perioden.")
        return
    
    price_col = meta.get("price_col")
    source_for_sma = hist_extended if hist_extended is not None else hist
    df_sma = source_for_sma.copy().sort_index()
    df_sma.index = df_sma.index.tz_localize(None) if getattr(df_sma.index, "tz", None) else df_sma.index

    if price_col not in df_sma.columns:
        st.warning(f"Kan ikke beregne SMA fordi kolonnen '{price_col}' mangler i historikken.")
        st.plotly_chart(fig, use_container_width=True)
        return

    #--- SMA toggle ---
    col1, col2 = st.columns([1,1]) 
    with col1:
        show_sma50 = st.checkbox("Vis SMA 50", value=True)
    with col2:
        show_sma200 = st.checkbox("Vis SMA 200", value=True)

    sma50_visible = df_sma[price_col].rolling(window=50, min_periods=50).mean().reindex(df.index)
    if show_sma50 and sma50_visible.notna().any():
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=sma50_visible,
                mode="lines",
                name="SMA 50", 
                line=dict(color="purple", width=2)
            ), row=1, col=1   
        )
    elif show_sma50:
        st.info("Ikke nok data for å beregne SMA 50.")

    sma200_visible = df_sma[price_col].rolling(window=200, min_periods=200).mean().reindex(df.index)
    if show_sma200 and sma200_visible.notna().any():
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=sma200_visible,
                mode="lines",
                name="SMA 200", 
                line=dict(color="green", width=2)
            ), row=1, col=1   
        )
    elif show_sma200:
        st.info("Ikke nok data for å beregne SMA 200.")
    
    st.plotly_chart(fig,use_container_width=True)
