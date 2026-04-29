import pandas as pd


def _signal(label: str, color: str, value, explanation: str) -> dict:
    return {"label": label, "color": color, "value": value, "explanation": explanation}


def revenue_growth_signal(snap: dict) -> dict:
    v = snap.get("revenue_growth")
    if v is None:
        return _signal("Ukjent", "gray", None,
            "Inntektsvekst viser hvor mye mer selskapet tjener sammenlignet med året før. "
            "Høy vekst er et godt tegn, spesielt for KI-selskaper.")
    pct = round(v * 100, 1)
    if v >= 0.15:
        return _signal(f"+{pct}% vekst", "green", pct,
            f"Inntektene vokser med {pct}% år over år — sterk vekst. "
            "For langsiktige investorer er jevn inntektsvekst et av de viktigste tegnene på et sunt selskap.")
    if v >= 0.0:
        return _signal(f"+{pct}% vekst", "orange", pct,
            f"Inntektene vokser med {pct}% — moderat vekst. "
            "Selskapet beveger seg fremover, men ikke raskt. Se etter hva som bremser.")
    return _signal(f"{pct}% vekst", "red", pct,
        f"Inntektene faller med {abs(pct)}%. Dette kan være et advarselstegn. "
        "Undersøk hvorfor inntektene synker før du investerer.")


def profitability_signal(snap: dict) -> dict:
    v = snap.get("profit_margins")
    if v is None:
        return _signal("Ukjent", "gray", None,
            "Nettomarginen viser hvor mye av inntektene som blir igjen som overskudd etter alle kostnader.")
    pct = round(v * 100, 1)
    if v >= 0.1:
        return _signal(f"{pct}% margin", "green", pct,
            f"Selskapet beholder {pct}% av inntektene som overskudd — solid lønnsomhet. "
            "En høy margin betyr at selskapet ikke trenger å selge enormt mye for å tjene penger.")
    if v >= 0.0:
        return _signal(f"{pct}% margin", "orange", pct,
            f"Selskapet er lønnsomt, men med tynn margin på {pct}%. "
            "Det betyr at kostnader spiser mye av inntektene — kan være greit i vekstfasen.")
    return _signal(f"{pct}% margin", "red", pct,
        f"Selskapet går med tap ({pct}% margin). Mange vekstselskaper gjør dette bevisst, "
        "men sjekk at de har nok cash til å overleve til lønnsomhet.")


def debt_signal(snap: dict) -> dict:
    v = snap.get("debt_to_equity")
    if v is None:
        return _signal("Ukjent", "gray", None,
            "Gjeld/egenkapital (D/E) viser hvor mye gjeld selskapet har relativt til hva det eier selv. "
            "Lavt tall = solid økonomi.")
    if v <= 50:
        return _signal(f"D/E: {round(v, 0)}", "green", v,
            f"Lav gjeld (D/E {round(v,0)}). Selskapet er finansielt solid og tåler nedgangstider godt. "
            "For langsiktige investorer er lav gjeld trygghet.")
    if v <= 150:
        return _signal(f"D/E: {round(v, 0)}", "orange", v,
            f"Moderat gjeld (D/E {round(v,0)}). Ikke alarmerande, men følg med på rentekostnader "
            "og om gjelden øker over tid.")
    return _signal(f"D/E: {round(v, 0)}", "red", v,
        f"Høy gjeld (D/E {round(v,0)}). Selskapet er avhengig av lånt kapital. "
        "Høy gjeld øker risikoen, spesielt i perioder med høye renter.")


def cashflow_signal(snap: dict) -> dict:
    v = snap.get("free_cashflow")
    if v is None:
        return _signal("Ukjent", "gray", None,
            "Fri kontantstrøm (FCF) er penger selskapet faktisk genererer etter investeringer. "
            "Positiv FCF er et sterkt tegn — selskapet trenger ikke stadig hente ny kapital.")
    billions = round(v / 1e9, 2)
    if v > 0:
        return _signal(f"FCF: ${billions}B", "green", v,
            f"Positiv fri kontantstrøm (${billions}B). Selskapet genererer ekte penger — "
            "ikke bare regnskapsmessig overskudd. Dette er et av de beste tegnene for langsiktige investorer.")
    return _signal(f"FCF: ${billions}B", "red", v,
        f"Negativ fri kontantstrøm (${billions}B). Selskapet bruker mer cash enn det genererer. "
        "Kan være OK i vekstfasen, men sjekk om det er en trend eller engangshendelse.")


def valuation_signal(snap: dict) -> dict:
    pe = snap.get("pe_ratio")
    if pe is None:
        return _signal("Ukjent P/E", "gray", None,
            "P/E (pris/inntjening) viser hvor mye du betaler for én krone av selskapets overskudd. "
            "Lavt P/E kan bety billig aksje, høyt P/E kan bety høye forventninger.")
    pe = round(pe, 1)
    if pe <= 0:
        return _signal(f"P/E: {pe}", "red", pe,
            "Negativ P/E betyr at selskapet går med tap. Ingen inntjening å måle mot.")
    if pe <= 20:
        return _signal(f"P/E: {pe}", "green", pe,
            f"P/E på {pe} er relativt lavt — aksjen kan være rimelig priset. "
            "Husk at lavt P/E ikke alltid er en kjøpssignal: sjekk alltid hvorfor.")
    if pe <= 40:
        return _signal(f"P/E: {pe}", "orange", pe,
            f"P/E på {pe} er moderat høyt. Markedet forventer god vekst fremover. "
            "Mange KI-selskaper handler til høy P/E fordi vekstforventningene er store.")
    return _signal(f"P/E: {pe}", "red", pe,
        f"P/E på {pe} er høyt. Du betaler mye for fremtidig vekst. "
        "Høy P/E fungerer bare hvis selskapet faktisk leverer — stor nedsiderisiko hvis de skuffer.")


def momentum_signal(hist: pd.DataFrame, extended_hist: pd.DataFrame) -> dict:
    if extended_hist is None or extended_hist.empty or len(extended_hist) < 200:
        if hist is None or hist.empty:
            return _signal("Ukjent", "gray", None,
                "Momentum viser om aksjen er i en opptrend. Vi sjekker om prisen er over 200-dagers snitt (SMA200).")
        sma_data = hist
    else:
        sma_data = extended_hist

    sma200 = sma_data["Close"].rolling(200).mean().iloc[-1]
    last_price = sma_data["Close"].iloc[-1]

    if pd.isna(sma200):
        return _signal("Ukjent", "gray", None,
            "Ikke nok historikk til å beregne 200-dagers glidende snitt (SMA200).")

    pct_above = round((last_price / sma200 - 1) * 100, 1)
    if last_price >= sma200:
        return _signal(f"+{pct_above}% over SMA200", "green", pct_above,
            f"Aksjen handler {pct_above}% over sitt 200-dagers glidende snitt. "
            "Dette betyr at trenden er opp — mange investorer ser SMA200 som grensen mellom "
            "bull og bear marked for en aksje.")
    return _signal(f"{pct_above}% under SMA200", "red", pct_above,
        f"Aksjen handler {abs(pct_above)}% under sitt 200-dagers glidende snitt. "
        "Trenden er ned. Det betyr ikke at det ikke kan snu, men det er et forsiktighetsmerke.")
