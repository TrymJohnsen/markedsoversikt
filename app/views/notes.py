import streamlit as st


def render_notes(active):
    snap = active.get("snap")
    ticker = snap.get("ticker", "")

    st.subheader("Notater og Watchlist")

    # --- Watchlist ---
    st.markdown("### Watchlist")
    st.caption("Lagre tickers du følger med på. Klikk på en for å laste den inn.")

    watchlist = st.session_state.get("watchlist", [])

    col_input, col_add = st.columns([3, 1])
    with col_input:
        new_ticker = st.text_input("Legg til ticker", placeholder="F.eks. NVDA", key="wl_input",
                                   label_visibility="collapsed")
    with col_add:
        if st.button("Legg til", use_container_width=True):
            cleaned = new_ticker.strip().upper()
            if cleaned and cleaned not in watchlist:
                watchlist.append(cleaned)
                st.session_state["watchlist"] = watchlist
                st.rerun()

    if watchlist:
        cols = st.columns(min(len(watchlist), 6))
        for i, t in enumerate(watchlist):
            with cols[i % 6]:
                if st.button(t, key=f"wl_{t}", use_container_width=True):
                    st.session_state["search_ticker"] = t
                    st.info(f"Søk på '{t}' og trykk 'Hent data' for å laste inn.")
                if st.button("✕", key=f"wl_del_{t}", use_container_width=True):
                    watchlist.remove(t)
                    st.session_state["watchlist"] = watchlist
                    st.rerun()
    else:
        st.info("Ingen tickers i watchlisten ennå.")

    st.divider()

    # --- Notater per ticker ---
    st.markdown(f"### Notater for {ticker}")
    notes = st.session_state.get("notes", {})

    tese = notes.get(ticker, {}).get("tese", "")
    new_tese = st.text_area(
        "Min investeringstese",
        value=tese,
        placeholder=f"Hvorfor tror du på {ticker}? Hva er argumentet for å holde denne langsiktig? "
                    "F.eks: 'Dominerer KI-chip-markedet, ingen reell konkurrent de neste 3 årene...'",
        height=120,
        key=f"tese_{ticker}",
    )

    notat = notes.get(ticker, {}).get("notat", "")
    new_notat = st.text_area(
        "Generelle notater",
        value=notat,
        placeholder="Andre ting du vil huske: nøkkeldatoer, risikoer du har identifisert, spørsmål du vil undersøke...",
        height=100,
        key=f"notat_{ticker}",
    )

    if st.button("Lagre notater", type="primary"):
        if ticker not in notes:
            notes[ticker] = {}
        notes[ticker]["tese"] = new_tese
        notes[ticker]["notat"] = new_notat
        st.session_state["notes"] = notes
        st.success(f"Notater for {ticker} lagret.")

    # --- Vis lagrede notater for andre tickers ---
    other_notes = {t: n for t, n in notes.items() if t != ticker and (n.get("tese") or n.get("notat"))}
    if other_notes:
        st.divider()
        st.markdown("### Notater fra andre tickers")
        for t, n in other_notes.items():
            with st.expander(t):
                if n.get("tese"):
                    st.markdown(f"**Investeringstese:** {n['tese']}")
                if n.get("notat"):
                    st.markdown(f"**Notater:** {n['notat']}")
