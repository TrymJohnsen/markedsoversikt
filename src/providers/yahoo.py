import pandas as pd
import yfinance as yf


def get_ai_exposure_label(sector: str | None, industry: str | None) -> str:
    sector = (sector or "").lower()
    industry = (industry or "").lower()

    ai_core = {"semiconductors", "semiconductor", "hardware"}
    ai_user = {"software", "cloud", "internet", "artificial intelligence", "machine learning", "data"}
    ai_indirect = {"utilities", "real estate", "infrastructure", "electric"}

    if any(k in industry for k in ai_core) or any(k in sector for k in ai_core):
        return "KI-kjernespiller"
    if any(k in industry for k in ai_user) or any(k in sector for k in ai_user) or "technology" in sector:
        return "KI-bruker"
    if any(k in industry for k in ai_indirect) or any(k in sector for k in ai_indirect):
        return "Indirekte eksponering"
    return "Ikke KI-relevant"


def get_snapshot(ticker: str) -> dict:
    """
    Return a snapshot with key info and fundamentals for signal calculations.
    Yahoo is not always consistent, so .get is used to avoid KeyErrors.
    """
    t = yf.Ticker(ticker)
    info = t.info or {}

    sector = info.get("sector")
    industry = info.get("industry")

    return {
        "ticker": ticker,
        "name": info.get("shortName") or info.get("longName"),
        "description": info.get("longBusinessSummary"),
        "last_price": info.get("previousClose") or info.get("regularMarketPrice"),
        "sector": sector,
        "industry": industry,
        "currency": info.get("currency"),
        "exchange": info.get("exchange"),
        "market_cap": info.get("marketCap"),
        "ai_exposure": get_ai_exposure_label(sector, industry),
        # Verdsettelse
        "pe_ratio": info.get("trailingPE"),
        "ps_ratio": info.get("priceToSalesTrailing12Months"),
        "pb_ratio": info.get("priceToBook"),
        # Vekst og lønnsomhet
        "revenue_growth": info.get("revenueGrowth"),
        "gross_margins": info.get("grossMargins"),
        "profit_margins": info.get("profitMargins"),
        "return_on_equity": info.get("returnOnEquity"),
        # Soliditet
        "debt_to_equity": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),
        "free_cashflow": info.get("freeCashflow"),
        # KI-relevant
        "rd_expenses": info.get("researchAndDevelopment"),
        "total_revenue": info.get("totalRevenue"),
    }


def period_to_offset(period: str):
    """
    Convert UI period values to a pandas offset.
    Return None for "max" so the caller can fetch all available history.
    """
    period = period.strip().lower()

    if period == "max":
        return None
    if period.endswith("d"):
        return pd.DateOffset(days=int(period[:-1]))
    if period.endswith("mo"):
        return pd.DateOffset(months=int(period[:-2]))
    if period.endswith("y"):
        return pd.DateOffset(years=int(period[:-1]))
    raise ValueError(f"Ugyldig periodeformat: {period}")


def buffer_offset(interval: str, buffer_points: int):
    """
    Add a warmup buffer so long SMAs can be calculated before the visible range.
    """
    interval = interval.strip().lower()

    if interval == "1d":
        return pd.tseries.offsets.BDay(buffer_points + 30)
    if interval == "1wk":
        return pd.DateOffset(weeks=buffer_points + 4)
    if interval == "1mo":
        return pd.DateOffset(months=buffer_points + 2)
    raise ValueError(f"Ugyldig interval: {interval}")


def get_price_history(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
    sma_windows: tuple[int, ...] = (50, 200),
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Return:
    df_plot: visible range used in the UI
    df_full: extended range with warmup data for SMA calculations
    meta: helpful fetch metadata
    """

    end_display = pd.Timestamp.now(tz=None)
    display_offset = period_to_offset(period)
    start_display = None if display_offset is None else end_display - display_offset

    valid_windows = [w for w in sma_windows if isinstance(w, int) and w > 0]
    warmup_points = max(valid_windows) - 1 if valid_windows else 0

    ticker_obj = yf.Ticker(ticker)
    if period.strip().lower() == "max":
        start_fetch = None
        df_full = ticker_obj.history(period="max", interval=interval)
    else:
        start_fetch = start_display - buffer_offset(interval, warmup_points)
        df_full = ticker_obj.history(start=start_fetch, end=end_display, interval=interval)

    if df_full is None or df_full.empty:
        raise ValueError(
            f"Ingen prisdata returnert for {ticker} (start={start_fetch}, end={end_display}, interval={interval})"
        )

    if isinstance(df_full.index, pd.DatetimeIndex) and df_full.index.tz is not None:
        df_full.index = df_full.index.tz_localize(None)

    if start_display is None:
        df_plot = df_full.copy()
    else:
        df_plot = df_full.loc[start_display:end_display].copy()

    meta = {
        "start_fetch": start_fetch,
        "start_display": start_display,
        "end_display": end_display,
        "warmup_points": warmup_points,
        "display_points": len(df_plot),
        "fetched_points": len(df_full),
        "interval": interval,
        "period": period,
        "sma_windows": tuple(valid_windows),
    }

    return df_plot, df_full, meta


def get_fundamentals(ticker: str) -> dict:
    """
    Get a few key fundamental values from the income statement.
    """

    t = yf.Ticker(ticker)
    income = t.financials

    if income is None or income.empty:
        raise ValueError(f"Ingen fundamentaldata returnert for {ticker}")

    return {
        "revenue": income.loc["Total Revenue"] if "Total Revenue" in income.index else None,
        "ebitda": income.loc["EBITDA"] if "EBITDA" in income.index else None,
        "net_income": income.loc["Net Income"] if "Net Income" in income.index else None,
    }
