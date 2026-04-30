import streamlit as st
import plotly.graph_objects as go

from src.providers.yahoo import get_fundamentals


def _fmt_pct(value):
    if value is None:
        return "-"
    return f"{round(value * 100, 1)}%"


def _fmt_num(value, decimals=1):
    if value is None:
        return "-"
    return f"{round(float(value), decimals)}"


def _fmt_financial(value):
    if value is None:
        return "-"
    v = float(value)
    if abs(v) >= 1e12:
        return f"${v/1e12:.2f}T"
    if abs(v) >= 1e9:
        return f"${v/1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"${v/1e6:.2f}M"
    return f"${v:,.0f}"


def _metric_with_tooltip(col, label, value, tooltip):
    with col:
        st.metric(label, value)
        st.caption(f"ℹ️ {tooltip}")


def render_fundamentals(active):
    snap = active.get("snap")
    ticker = snap.get("ticker")

    st.subheader(f"Fundamentals — {snap.get('name', '')} ({ticker})")
    st.caption("Her finner du de viktigste tallene for å vurdere et selskap som langsiktig investor.")

    # --- Verdsettelse ---
    st.markdown("### Verdsettelse")
    st.caption("Hva betaler du for selskapet relativt til hva det tjener?")
    v1, v2, v3 = st.columns(3)
    _metric_with_tooltip(v1, "P/E (pris/inntjening)", _fmt_num(snap.get("pe_ratio")),
        "Hvor mye du betaler per krone selskapet tjener. P/E 20 betyr du betaler 20x årsoverskuddet. "
        "Lavere er billigere, men høy P/E kan være OK for vekstselskaper.")
    _metric_with_tooltip(v2, "P/S (pris/salg)", _fmt_num(snap.get("ps_ratio")),
        "Pris relativt til inntekter. Nyttig for selskaper som ennå ikke er lønnsomme. "
        "P/S under 5 regnes som rimelig for de fleste bransjer.")
    _metric_with_tooltip(v3, "P/B (pris/bokverdi)", _fmt_num(snap.get("pb_ratio")),
        "Pris relativt til selskapets bokførte verdi (eiendeler minus gjeld). "
        "P/B under 1 betyr du kjøper selskapet under bokverdi — sjelden for teknologiselskaper.")

    st.divider()

    # --- Vekst og lønnsomhet ---
    st.markdown("### Vekst og lønnsomhet")
    g1, g2, g3, g4 = st.columns(4)
    _metric_with_tooltip(g1, "Inntektsvekst (YoY)", _fmt_pct(snap.get("revenue_growth")),
        "Prosentvis vekst i inntekter sammenlignet med samme periode i fjor. "
        "Over 15% er sterk vekst for et etablert selskap.")
    _metric_with_tooltip(g2, "Bruttomargin", _fmt_pct(snap.get("gross_margins")),
        "Hvor mye som er igjen etter produksjonskostnader. Høy bruttomargin betyr selskapet "
        "har god prismakt — vanlig for programvare (70-80%).")
    _metric_with_tooltip(g3, "Nettomarginen", _fmt_pct(snap.get("profit_margins")),
        "Andel av inntektene som ender som overskudd etter ALLE kostnader. "
        "Over 10% er solid. Negativ betyr selskapet går med tap.")
    _metric_with_tooltip(g4, "ROE (egenkapitalrentabilitet)", _fmt_pct(snap.get("return_on_equity")),
        "Hvor mye overskudd selskapet genererer per krone investert av aksjonærene. "
        "Over 15% regnes som bra. Warren Buffett ser etter selskaper med konsistent høy ROE.")

    st.divider()

    # --- Soliditet ---
    st.markdown("### Soliditet og kontantstrøm")
    s1, s2, s3 = st.columns(3)
    _metric_with_tooltip(s1, "Gjeld/egenkapital (D/E)", _fmt_num(snap.get("debt_to_equity")),
        "Gjeld relativt til egenkapital. Under 100 er trygt, over 200 er høyt. "
        "Merk: yfinance rapporterer dette som prosent (100 = 1x).")
    _metric_with_tooltip(s2, "Current Ratio", _fmt_num(snap.get("current_ratio")),
        "Kortsiktige eiendeler delt på kortsiktig gjeld. Over 1.5 betyr selskapet "
        "komfortabelt kan betale regningene sine det neste året.")
    _metric_with_tooltip(s3, "Fri kontantstrøm", _fmt_financial(snap.get("free_cashflow")),
        "Penger selskapet faktisk genererer etter investeringer i drift og anlegg. "
        "Positiv FCF er et av de sterkeste tegnene på et sunt selskap.")

    st.divider()

    # --- KI-relevant ---
    rd = snap.get("rd_expenses")
    total_rev = snap.get("total_revenue")
    if rd is not None:
        st.markdown("### KI og innovasjon")
        r1, r2 = st.columns(2)
        _metric_with_tooltip(r1, "F&U-utgifter", _fmt_financial(rd),
            "Forskning og utvikling (R&D). Selskaper som investerer mye i R&D "
            "bygger fremtidig konkurransefortrinn — spesielt viktig i KI-sektoren.")
        if total_rev and total_rev > 0:
            rd_pct = rd / total_rev
            _metric_with_tooltip(r2, "F&U som % av inntekter", _fmt_pct(rd_pct),
                "Hvor stor andel av inntektene som går til innovasjon. "
                "KI-selskaper bruker typisk 10-20% eller mer på F&U.")
        st.divider()

    # --- Historisk inntektsgraf ---
    st.markdown("### Historisk inntektsutvikling")
    if active.get("fundamentals") is None:
        with st.spinner("Henter historiske inntektstall..."):
            try:
                active["fundamentals"] = get_fundamentals(ticker)
            except Exception as e:
                st.warning(f"Kunne ikke hente historiske inntektstall: {e}")
                active["fundamentals"] = {}

    fund = active.get("fundamentals") or {}
    revenue_series = fund.get("revenue")
    net_income_series = fund.get("net_income")

    if revenue_series is not None and not revenue_series.empty:
        fig = go.Figure()
        cols = sorted(revenue_series.index, reverse=True)[:4]
        years = [str(c.year) if hasattr(c, "year") else str(c) for c in cols]
        rev_vals = [revenue_series[c] / 1e9 for c in cols]

        fig.add_trace(go.Bar(name="Inntekter ($B)", x=years, y=rev_vals,
                             marker_color="#4a90e2"))

        if net_income_series is not None and not net_income_series.empty:
            ni_vals = [net_income_series.get(c, None) for c in cols]
            ni_vals_b = [v / 1e9 if v is not None else None for v in ni_vals]
            fig.add_trace(go.Bar(name="Nettoresultat ($B)", x=years, y=ni_vals_b,
                                 marker_color="#00cc66"))

        fig.update_layout(
            template="plotly_dark",
            barmode="group",
            title="Inntekter og nettoresultat (siste 4 år, i milliarder USD)",
            xaxis_title="År",
            yaxis_title="Milliarder USD",
            height=350,
            margin=dict(t=40, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Historiske inntektstall ikke tilgjengelig for denne ticker.")
