import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go

import openai
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.indices.struct_store import GPTPandasIndex
from llama_index.llms import OpenAI

API_KEY = st.secrets["api"]["iex_key"]
openai.api_key = st.secrets["api"]['open_ai']
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

    service_context = ServiceContext.from_defaults(llm=OpenAI(
    model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert on the Data Analysis and your job is to answer analytical questions. Assume that all questions are related to dataset provided. Keep your answers technical and based on facts – do not hallucinate features."))
    # index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    index = GPTPandasIndex(df=stock_data, service_context=service_context)

    return stock_data, index

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

    st.header(f"Stock Data for {symbol}")

    if symbol:
        stock_data = get_stock_data(symbol)[0]
        index = get_stock_data(symbol)[1]

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


            if "messages" not in st.session_state.keys():  # Initialize the chat messages history
                st.session_state.messages = [
                    {"role": "assistant", "content": f"Ask me a question about{symbol}"}
                ]

            if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
                st.session_state.chat_engine = index.as_chat_engine(
                    chat_mode="condense_question", verbose=True)

            # Prompt for user input and save to chat history
            if prompt := st.chat_input("Your question"):
                st.session_state.messages.append({"role": "user", "content": prompt})

            for message in st.session_state.messages:  # Display the prior chat messages
                with st.chat_message(message["role"]):
                    st.write(message["content"])

            # If last message is not from assistant, generate a new response
            if st.session_state.messages[-1]["role"] != "assistant":
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = st.session_state.chat_engine.chat(prompt)
                        st.write(response.response)
                        message = {"role": "assistant", "content": response.response}
                        # Add response to message history
                        st.session_state.messages.append(message)


if __name__ == "__main__":
    app()
