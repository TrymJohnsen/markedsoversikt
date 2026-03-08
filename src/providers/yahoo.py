import yfinance as yf
import pandas as pd

def get_snapshot(ticker: str) -> dict:
    """
    returns a small snapshot with key info
    Yahoo is not always consistent, so .get is used to avoid KeyErrors
    """
    t = yf.Ticker(ticker)
    info = t.info or {} #empty dict if no info

    return {
        "ticker": ticker,
        "name": info.get("shortName") or info.get("longName"),
        "last_price": info.get("previousClose") or info.get("regularMarketPrice"),
        "sector": info.get("sector"),
        "currency": info.get("currency"),
        "exchange": info.get("exchange"),
        "market_cap": info.get("marketCap"),
    }



def period_to_timedelta(period: str) -> pd.Timedelta:
    """
    Konverterer yfinance-perioder til en offset/timedelta for å finne start_display som brukes i sma beregning.
    Støtter typiske: 1mo, 3mo, 6mo, 1y, 3y, 5y, 1d, 5d
    """
    period = period.strip().lower()

    #dager
    if period.endswith("d"):
        n = int(period[:-1])
        return pd.Timedelta(days=n)
    #måneder
    elif period.endswith("mo"):
        n = int(period[:-2])
        return pd.Timedelta(months=n)  
    #år
    elif period.endswith("y"):
        n = int(period[:-1])
        return pd.Timedelta(year=n) 
    else:
        raise ValueError(f"Ugyldig periodeformat: {period}")
    
    
def buffer_offset(interval: str, buffer_points: int) -> pd.Timedelta:
    """
    Beregner en buffer for å sikre at vi har nok data for SMA-beregning, basert på intervallet.
    f.eks. for 1d interval og 200 SMA, trenger vi minst 200 datapunkter, så en buffer på 300 dager kan være fornuftig.
    """
    interval = interval.strip().lower()

    if interval == "1d":
        #business dager, så vi legger til ekstra for helger/ferier
        return pd.tseries.offsets.BDay(buffer_points)
    
    if interval == "1wk":
        return pd.DateOffset(weeks=buffer_points)
    
    if interval == "1mo":
        return pd.DateOffset(months=buffer_points)
    
    raise ValueError(f"Ugyldig interval: {interval}")

    
def get_price_history(ticker: str, period: str = "1y", interval: str = "1d", extra_points: int = 220) -> tuple[pd.DataFrame,pd.DataFrame,dict]:
    """
    Returnerer:
    df_plot: klippet til valgt period (det du viser)
    df_full: inneholder extra_points datapunkter før start (for SMA osv.)
    meta: nyttige tider/info
    """
    
    end_display = pd.Timestamp.now(tz=None)

    period_off = period_to_timedelta(period)
    start_display = end_display - period_off

    buffer_off = buffer_offset(interval, extra_points)
    start_fetch = start_display - buffer_off

    t = yf.Ticker(ticker)

    df_full = t.history(start = start_fetch, end = end_display, interval=interval)

    if df_full is None or df_full.empty:
        raise ValueError(f"Ingen prisdata returnert for {ticker} (start={start_fetch}, end={end_display}, interval={interval})")
    
    df_plot = df_full.loc[start_display:end_display].copy()

    meta = {
        "start_fetch": start_fetch,
        "start_display": start_display,
        "end_display": end_display,
        "extra_points": extra_points,
        "interval": interval,
        "period": period,
    }

    return df_plot, df_full, meta





def get_fundamentals(ticker: str) -> dict:
    """
    gets key fundamental data 
    """

    t = yf.Ticker(ticker)

    income = t.financials #income statement

    if income is None or income.empty:
        raise ValueError(f"Ingen fundamentaldata returnert for {ticker}")

    #income er ofte strukturert med rader = regnskapsposter
    # og kolonner = år/perioder

    fundamentals = {
        "revenue": income.loc["Total Revenue"] if "Total Revenue" in income.index else None,
        "ebitda": income.loc["EBITDA"] if "EBITDA" in income.index else None,
        "net_income": income.loc["Net Income"] if "Net Income" in income.index else None,
    }

    return fundamentals