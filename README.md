## Check out the application [here](https://stocksapi.streamlit.app/)

# Stock Dashboard
This is a Streamlit app that displays stock data and a candlestick chart for a selected stock symbol. The app also calculates the price difference (YoY), 52-week high, and 52-week low of the selected stock.

## How to run the app
Clone the repository:
```bash
git clone https://github.com/cameronjoejones/streamlit-kpi-dashboard.git
```
Install the requirements:
```bash
pip install -r requirements.txt

```

Set up the API key by creating a secrets.toml file inside the .streamlit folder with the following format:
```bash
[api]
iex_key = "<your_iex_cloud_api_key>"
```

Run the app:
```bash
streamlit run app.py
```


# App functionality
When the app is launched, it displays a sidebar with a dropdown menu of popular stock symbols. The user can select a stock symbol from the dropdown menu to display the corresponding stock data and candlestick chart.

The app calculates the price difference (YoY), 52-week high, and 52-week low of the selected stock and displays them as metrics on the top of the app. It also displays the latest stock data and a candlestick chart for the selected stock.

Finally, the app provides a "Download Stock Data Overview" button that allows the user to download the stock data overview as a CSV file.
