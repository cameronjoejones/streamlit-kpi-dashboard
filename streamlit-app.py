import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go

API_KEY = st.secrets["api"]["iex_key"]
API_BASE_URL = "https://cloud.iexapis.com/stable/"

def get_stock_data(symbol, time_range="5y"):
    params = {
        "token": API_KEY
    }

    response = requests.get(API_BASE_URL + f"stock/{symbol}/chart/{time_range}", params=params)
    data = response.json()

    if "error" in data:
        st.error(f"Error: {data['error']}")
        return None

    stock_data = pd.DataFrame(data)
    stock_data["date"] = pd.to_datetime(stock_data["date"])
    stock_data.set_index("date", inplace=True)
    stock_data = stock_data[["open", "high", "low", "close", "volume"]]
    stock_data.columns = ["Open", "High", "Low", "Close", "Volume"]
    return stock_data

def calculate_price_difference(stock_data):
    latest_price = stock_data.iloc[-1]["Close"]
    previous_year_price = stock_data.iloc[-252]["Close"] if len(stock_data) > 252 else stock_data.iloc[0]["Close"]
    price_difference = latest_price - previous_year_price
    percentage_difference = (price_difference / previous_year_price) * 100
    return price_difference, percentage_difference

def app():
    #-- BOLIERPLATE --#
    st.set_page_config(page_title="Stock Dashboard", layout="wide", page_icon="📈")
    hide_menu_style = "<style> footer {visibility: hidden;} </style>"
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    
    st.title("📈 Stock Dashboard")
    popular_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "FB", "BRK-B", "V", "NVDA", "JPM"]
    symbol = st.sidebar.selectbox("Select a stock symbol:", popular_symbols, index=2)
 
    st.sidebar.info('Created by Cameron Jones, view the Source Code on [GitHub](https://github.com/cameronjoejones/streamlit-kpi-dashboard)')
    st.sidebar.text("")
    st.sidebar.markdown(
    """
    <a href="https://twitter.com/cameronjoejones" target="_blank" style="text-decoration: none;">
        <div style="display: flex; align-items: center;">
            <img src="https://abs.twimg.com/icons/apple-touch-icon-192x192.png" width="30" height="30">
            <span style="font-size: 16px; margin-left: 5px;">Follow me on Twitter</span>
        </div>
    </a>
    """, unsafe_allow_html=True
    )

    st.header(f"Stock Data for {symbol}")

    if symbol:
        stock_data = get_stock_data(symbol)

        if stock_data is not None:
            price_difference, percentage_difference = calculate_price_difference(stock_data)
            latest_close_price = stock_data.iloc[-1]["Close"]
            max_52_week_high = stock_data["High"].tail(252).max()
            min_52_week_low = stock_data["Low"].tail(252).min()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Close Price", f"${latest_close_price:.2f}")
            with col2:
                st.metric("Price Difference (YoY)", f"${price_difference:.2f}", f"{percentage_difference:+.2f}%")
            with col3:
                st.metric("52-Week High", f"${max_52_week_high:.2f}")
            with col4:
                st.metric("52-Week Low", f"${min_52_week_low:.2f}")

            st.subheader("Candlestick Chart")
            candlestick_chart = go.Figure(data=[go.Candlestick(x=stock_data.index, open=stock_data['Open'], high=stock_data['High'], low=stock_data['Low'], close=stock_data['Close'])])
            candlestick_chart.update_layout(title=f"{symbol} Candlestick Chart", xaxis_rangeslider_visible=False)
            st.plotly_chart(candlestick_chart, use_container_width=True)

            st.subheader("Summary")
            st.dataframe(stock_data.tail())

            st.download_button("Download Stock Data Overview", stock_data.to_csv(index=True), file_name=f"{symbol}_stock_data.csv", mime="text/csv")


if __name__ == "__main__":
    app()
