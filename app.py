import streamlit as st
from newsapi import NewsApiClient
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
newsapi = NewsApiClient(api_key="4ed6b5b4995a49f88d68dddc5faeeb14")
from ta.momentum import RSIIndicator

st.set_page_config(page_title="Stock Tracker", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Real-Time Stock Market Tracker")

st.sidebar.header("⚙️ Settings")

stock = st.sidebar.text_input("Enter Stock Symbol", "AAPL")

interval = st.sidebar.selectbox(
    "Select Interval",
    ["1m", "5m", "15m", "1h", "1d"]
)

target = st.sidebar.number_input("🔔 Set Alert Price", value=0.0)

watchlist = st.sidebar.multiselect(
    "📊 Select Watchlist",
    ["AAPL", "TSLA", "GOOGL", "MSFT", "INFY.NS", "RELIANCE.NS"]
)

data = yf.Ticker(stock)
df = data.history(period="1d", interval=interval)

if not df.empty:

    df["MA20"] = df["Close"].rolling(window=20).mean()

    rsi = RSIIndicator(close=df["Close"], window=14)
    df["RSI"] = rsi.rsi()

    price = df["Close"].iloc[-1]
    prev = df["Close"].iloc[-2]
    change = price - prev

    col1, col2 = st.columns(2)
    col1.metric("💰 Current Price", f"{price:.2f}", f"{change:.2f}")
    col2.metric("📊 Volume", int(df["Volume"].iloc[-1]))

    if target > 0:
        if price > target:
            st.success("📈 Price is ABOVE target")
        else:
            st.info("📉 Price is BELOW target")

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["MA20"],
        name="MA20",
        mode="lines"
    ))

    fig.update_layout(
        title=f"{stock} Candlestick Chart",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📉 RSI Indicator")

    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(
        x=df.index,
        y=df["RSI"],
        name="RSI"
    ))

    fig_rsi.update_layout(title="RSI Indicator")

    st.plotly_chart(fig_rsi, use_container_width=True)

else:
    st.error("❌ Invalid stock symbol or no data found")

if watchlist:
    st.subheader("📊 Watchlist")

    for s in watchlist:
        try:
            d = yf.Ticker(s).history(period="1d")
            if not d.empty:
                latest = d["Close"].iloc[-1]
                st.write(f"{s}: {latest:.2f}")
        except:
            st.write(f"{s}: Error fetching data")

st.subheader("📰 Latest Stock News")

try:
    news = newsapi.get_everything(
        q=stock + " stock",
        language='en',
        sort_by='publishedAt',
        page_size=5
    )

    for article in news['articles']:
        st.markdown(f"### 🔹 {article['title']}")
        st.write(article['source']['name'])
        st.write(article['description'])
        st.markdown(f"[Read more]({article['url']})")
        st.write("---")

except:
    st.error("⚠️ Unable to fetch news. Check API key or internet.")