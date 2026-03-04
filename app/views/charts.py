import plotly.graph_objects as go
from plotly.subplots import make_subplots

def build_price_fig(hist, currency, chart_type: str, show_volume=True, show_legend=True):
    df = hist.copy().sort_index()  # sørg for at data er sortert etter dato
    df.index = df.index.tz_localize(None) if getattr(df.index, 'tz', None) else df.index  # fjern timezone hvis den finnes

    if df.empty:
        return None, df, {"has_volume": False, "price_col": None} # Returner tom figur og info hvis ingen data
    
    price_col = "Adj Close" if "Adj Close" in df.columns else "Close"

    volum_col = "Volume" if "Volume" in df.columns else None 
    if show_volume and volum_col is not None:
        has_volume = True
        rows = 2
        row_heights = [0.75, 0.25]   
    else:
        has_volume = False
        rows = 1
        row_heights = [1]

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
    )   

    if chart_type == "Candlestick":
        required = {"Open", "High", "Low", "Close"}
        if required.issubset(df.columns):
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="OHLC"
            ), row=1, col=1)
        else:
            st.warning("Candlestick-graf krever at data inneholder Open, High, Low og Close. Viser linjegraf i stedet.")
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[price_col],
                mode="lines",
                name=price_col,
            ), row=1, col=1)

    else:  # Linje
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[price_col],
            mode="lines",
            name=price_col,
        ), row=1, col=1)

    if show_volume and volum_col is not None:
        fig.add_trace(go.Bar(
            x=df.index,
            y=df[volum_col],
            name="Volume",
            marker_color="rgba(200, 200, 200, 0.5)",
        ), row=2, col=1)
        
    fig.update_layout(
        height=600 if show_volume and volum_col is not None else 500,
        xaxis_title="Dato",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=show_legend
    )

    fig.update_yaxes(title_text=f"Pris ({currency})", row=1, col=1)

    if has_volume and volum_col is not None:
        fig.update_yaxes(title_text="Volum", row=2, col=1)
        #divider mellom pris og volum
        fig.add_shape(
            type="line",
            x0=0, x1=1,
            y0=0.25, y1=0.25,
            xref="paper", yref="paper",
            line=dict(color="rgba(150,150,150,0.5)", width=1, dash="dash")
        )

    meta = {"has_volume": show_volume and volum_col is not None, "price_col": price_col}
    return fig, df, meta