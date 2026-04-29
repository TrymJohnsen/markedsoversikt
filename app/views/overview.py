import streamlit as st

from app.views.charts import build_price_fig
from src.analytics.indicators import (
    revenue_growth_signal,
    profitability_signal,
    debt_signal,
)

_AI_BADGE_COLORS = {
    "KI-kjernespiller": ("🟢", "#1a472a"),
    "KI-bruker": ("🔵", "#1a3a5c"),
    "Indirekte eksponering": ("🟡", "#4a3800"),
    "Ikke KI-relevant": ("⚪", "#333333"),
}

_SIGNAL_ICONS = {"green": "🟢", "orange": "🟡", "red": "🔴", "gray": "⚪"}


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
    return f"{value:.0f}"


def render_overview(active):
    snap = active.get("snap")
    hist = active.get("hist")

    # --- Navn og KI-badge ---
    ai_label = snap.get("ai_exposure", "Ikke KI-relevant")
    icon, _ = _AI_BADGE_COLORS.get(ai_label, ("⚪", "#333333"))

    col_name, col_badge = st.columns([3, 1])
    with col_name:
        st.subheader(snap.get("name", snap.get("ticker", "")))
        sector = snap.get("sector")
        industry = snap.get("industry")
        if sector or industry:
            st.caption(f"{sector or ''}{' / ' + industry if industry else ''}")
    with col_badge:
        st.markdown(f"### {icon} {ai_label}")

    # --- KPIs ---
    k1, k2, k3 = st.columns(3)
    k1.metric("Siste pris", snap.get("last_price"))
    k2.metric("Markedsverdi", format_financial(snap.get("market_cap")))
    k3.metric("Valuta", snap.get("currency"))

    # --- Helseoppsummering (3 trafikklysindikatorer) ---
    st.divider()
    st.markdown("**Rask helseoversikt**")
    sig_vekst = revenue_growth_signal(snap)
    sig_lønnsomhet = profitability_signal(snap)
    sig_gjeld = debt_signal(snap)

    h1, h2, h3 = st.columns(3)
    with h1:
        icon = _SIGNAL_ICONS.get(sig_vekst["color"], "⚪")
        st.markdown(f"{icon} **Vekst**")
        st.caption(sig_vekst["label"])
    with h2:
        icon = _SIGNAL_ICONS.get(sig_lønnsomhet["color"], "⚪")
        st.markdown(f"{icon} **Lønnsomhet**")
        st.caption(sig_lønnsomhet["label"])
    with h3:
        icon = _SIGNAL_ICONS.get(sig_gjeld["color"], "⚪")
        st.markdown(f"{icon} **Soliditet**")
        st.caption(sig_gjeld["label"])

    # --- Selskapsbeskrivelse ---
    description = snap.get("description")
    if description:
        with st.expander("Om selskapet"):
            st.write(description)

    st.divider()

    # --- Prisgraf ---
    chart_type = st.radio("Graf", ["Linje", "Candlestick"], horizontal=True)
    fig, df, meta = build_price_fig(hist, snap.get("currency"), chart_type, show_volume=True, show_legend=True)

    if fig is None:
        st.warning("Ingen prisdata tilgjengelig for denne ticker/perioden.")
        return

    st.plotly_chart(fig, use_container_width=True)
