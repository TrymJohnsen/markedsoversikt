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
        "sector": info.get("sector"),
        "currency": info.get("currency"),
        "exchange": info.get("exchange"),
        "market_cap": info.get("marketCap"),
    }

def get_price_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    gets historical price data as a dataframe with date index
    typiske kolonner: open, high, low, close, adj close, volume (og evt dividends/splits)
    """
    t = yf.Ticker(ticker)
    df = t.history(period=period, interval=interval)

    if df is None or df.empty:
        raise ValueError(f"Ingen prisdata returnert for {ticker} (period={period}, interval={interval})")
    
    return df