import streamlit as st
import plotly.graph_objects as go

from app.views.charts import build_price_fig

def render_technical(active):
    snap = active.get("snap")
    hist = active.get("hist")
    
    st.subheader(f"Teknisk analyse for {snap.get('name', '')} ({snap.get('ticker', '')})")

    fig,df,meta = build_price_fig(hist, snap.get("currency"), chart_type="Line", show_volume=False, show_legend=True)

    if fig is None:
        st.warning("Ingen prisdata tilgjengelig for denne ticker/perioden.")
        return
    
    price_col = meta.get("price_col")

    #--- SMA toggle ---
    col1, col2 = st.columns([1,1]) 
    with col1:
        show_sma50 = st.checkbox("Vis SMA 50", value=True)
    with col2:
        show_sma200 = st.checkbox("Vis SMA 200", value=True)

    if show_sma50 and len(df) >= 50:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[price_col].rolling(window=50).mean(),
                mode="lines",
                name="SMA 50", 
            ), row=1, col=1   
        )
    elif show_sma50:
        st.info("Ikke nok data for å beregne SMA 50.")

    if show_sma200 and len(df) >= 200:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[price_col].rolling(window=200).mean(),
                mode="lines",
                name="SMA 200", 
            ), row=1, col=1   
        )
    elif show_sma200:
        st.info("Ikke nok data for å beregne SMA 200.")
    
    st.plotly_chart(fig,use_container_width=True)