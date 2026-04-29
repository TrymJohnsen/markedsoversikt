import streamlit as st
import plotly.graph_objects as go

from app.views.charts import build_price_fig
from src.analytics.indicators import (
    revenue_growth_signal,
    profitability_signal,
    debt_signal,
    cashflow_signal,
    valuation_signal,
    momentum_signal,
)

_SIGNAL_ICONS = {"green": "🟢", "orange": "🟡", "red": "🔴", "gray": "⚪"}
_SIGNAL_COLORS = {"green": "#1a472a", "orange": "#4a3800", "red": "#4a1a1a", "gray": "#2a2a2a"}


def _render_signal_card(sig: dict):
    icon = _SIGNAL_ICONS.get(sig["color"], "⚪")
    bg = _SIGNAL_COLORS.get(sig["color"], "#2a2a2a")
    st.markdown(
        f"""<div style="background:{bg};padding:12px 16px;border-radius:8px;margin-bottom:8px">
        <span style="font-size:1.1em">{icon} <strong>{sig['label']}</strong></span>
        </div>""",
        unsafe_allow_html=True,
    )
    with st.expander("Hva betyr dette?"):
        st.write(sig["explanation"])


def render_technical(active):
    snap = active.get("snap")
    hist = active.get("hist")
    hist_extended = active.get("extended_hist")

    st.subheader(f"Signaler — {snap.get('name', '')} ({snap.get('ticker', '')})")
    st.caption("Disse 6 signalene er de viktigste å forstå som langsiktig investor. "
               "Grønt er bra, gult er nøytralt, rødt er et advarselstegn.")

    signals = [
        ("Inntektsvekst", revenue_growth_signal(snap)),
        ("Lønnsomhet", profitability_signal(snap)),
        ("Gjeld / soliditet", debt_signal(snap)),
        ("Kontantstrøm", cashflow_signal(snap)),
        ("Verdsettelse (P/E)", valuation_signal(snap)),
        ("Momentum (SMA200)", momentum_signal(hist, hist_extended)),
    ]

    col1, col2 = st.columns(2)
    for i, (title, sig) in enumerate(signals):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"**{title}**")
            _render_signal_card(sig)

    st.divider()
    with st.expander("Hvorfor er akkurat disse signalene viktige for langsiktige investorer?"):
        st.markdown("""
**Inntektsvekst** — Et selskap som vokser øker verdien over tid. Uten vekst stagnerer aksjen.

**Lønnsomhet** — Selskapet må til slutt tjene penger. Mange vekstselskaper er ikke lønnsomme ennå, men sjekk trenden.

**Gjeld** — Høy gjeld er risikabelt i perioder med høye renter. Lav gjeld gir selskapet handlefrihet.

**Kontantstrøm** — Overskudd kan manipuleres regnskapsmessig. Fri kontantstrøm er ekte penger — vanskelig å jukse med.

**Verdsettelse (P/E)** — Du betaler alltid for fremtiden. Høy P/E krever at selskapet leverer. Sjekk alltid hva du betaler for.

**Momentum (SMA200)** — Ikke for timing, men som en pekepinn på om markedet tror på selskapet akkurat nå.
        """)

    st.divider()
    st.markdown("**Prisgraf med bevegelige snitt**")

    fig, df, meta = build_price_fig(hist, snap.get("currency"), chart_type="Line", show_volume=False, show_legend=True)

    if fig is None:
        st.warning("Ingen prisdata tilgjengelig for denne ticker/perioden.")
        return

    price_col = meta.get("price_col")
    source_for_sma = hist_extended if hist_extended is not None else hist
    df_sma = source_for_sma.copy().sort_index()
    df_sma.index = df_sma.index.tz_localize(None) if getattr(df_sma.index, "tz", None) else df_sma.index

    if price_col in df_sma.columns:
        col1, col2 = st.columns(2)
        show_sma50 = col1.checkbox("Vis SMA 50", value=True)
        show_sma200 = col2.checkbox("Vis SMA 200", value=True)

        sma50 = df_sma[price_col].rolling(50, min_periods=50).mean().reindex(df.index)
        if show_sma50 and sma50.notna().any():
            fig.add_trace(go.Scatter(x=df.index, y=sma50, mode="lines", name="SMA 50",
                                     line=dict(color="purple", width=2)), row=1, col=1)

        sma200 = df_sma[price_col].rolling(200, min_periods=200).mean().reindex(df.index)
        if show_sma200 and sma200.notna().any():
            fig.add_trace(go.Scatter(x=df.index, y=sma200, mode="lines", name="SMA 200",
                                     line=dict(color="#00cc66", width=2)), row=1, col=1)

    st.plotly_chart(fig, use_container_width=True)
