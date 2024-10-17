import streamlit as st
import pandas as pd
import yfinance as yf
from tradingview_ta import TA_Handler, Interval
from plotly import graph_objects as go
import time
from support_resistance import identify_levels, group_levels, plot_levels

# Function to fetch stock data
def fetch_stock_data(ticker, interval='1m'):
    data = yf.download(tickers=ticker, interval=interval, period="1d")  # Adjust period to '1d' for 1-minute interval
    return data

# Function to get TradingView recommendation
def get_tradingview_recommendation(symbol, exchange):
    handler = TA_Handler(
        symbol=symbol,
        exchange=exchange,
        screener="america",
        interval=Interval.INTERVAL_1_MINUTE,
        timeout=None
    )
    try:
        analysis = handler.get_analysis()
        recommendation = analysis.summary['RECOMMENDATION']
        buy_count = analysis.summary['BUY']
        sell_count = analysis.summary['SELL']
        neutral_count = analysis.summary['NEUTRAL']
        indicators = analysis.indicators
        return recommendation, buy_count, sell_count, neutral_count, indicators
    except Exception as e:
        return f"Error: {e}", 0, 0, 0, {}

# Function to calculate metrics
def calculate_metrics(data):
    wins = data[data['Prediction Correct'] == True].shape[0]
    losses = data[data['Prediction Correct'] == False].shape[0]
    total_trades = wins + losses
    win_ratio = wins / total_trades if total_trades else 0
    loss_ratio = losses / total_trades if total_trades else 0
    profit_factor = (data[data['Prediction Correct'] == True]['Next Price'] - data[data['Prediction Correct'] == True][
        'Current Price']).sum() / ((data[data['Prediction Correct'] == False]['Current Price'] -
                                    data[data['Prediction Correct'] == False]['Next Price']).sum() or 1)
    average_win = (data[data['Prediction Correct'] == True]['Next Price'] - data[data['Prediction Correct'] == True][
        'Current Price']).mean() or 0
    average_loss = (data[data['Prediction Correct'] == False]['Current Price'] -
                    data[data['Prediction Correct'] == False]['Next Price']).mean() or 0

    return {
        'Win Ratio': win_ratio,
        'Loss Ratio': loss_ratio,
        'Profit Factor': profit_factor,
        'Average Win': average_win,
        'Average Loss': average_loss
    }

# Main function to run the app
def main():
    st.header("APPLE")

    # Read the CSV file
    try:
        results = pd.read_csv('C:/Users/mredu_ykchdzs/pythonProject/Treading/trading_results.csv')
    except FileNotFoundError:
        st.error("The CSV file 'trading_results.csv' was not found. Please ensure the file exists.")
        return

    # Fetch Apple's stock data
    stock_data = fetch_stock_data('AAPL', '1m')

    if stock_data.empty:
        st.write("No data available for the selected period.")
    else:
        # Convert the index to a timezone-aware datetime index
        if stock_data.index.tz is None:
            stock_data.index = stock_data.index.tz_localize('UTC').tz_convert('Asia/Dhaka')
        else:
            stock_data.index = stock_data.index.tz_convert('Asia/Dhaka')

        # Identify support and resistance levels
        levels = identify_levels(stock_data)
        grouped_levels = group_levels(levels)

        # Plot the stock data using Plotly with adjusted time zone
        fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                             open=stock_data['Open'],
                                             high=stock_data['High'],
                                             low=stock_data['Low'],
                                             close=stock_data['Close'])])

        # Add support and resistance lines
        fig = plot_levels(fig, stock_data, grouped_levels)

        fig.update_layout(xaxis_rangeslider_visible=False,
                          xaxis=dict(
                              title='Time',
                              tickformat='%Y-%m-%d %H:%M',  # Customize the time format as needed
                              tickangle=0,  # Ensure the labels are straight
                              tickfont=dict(size=12),  # Adjust font size for better readability
                              ticklabelmode="period",  # Display labels in periods for better readability
                              ticklabelstep=1,  # Adjust the step between ticks
                              tickmode='auto',  # Automatically determine the tick placement
                              showticklabels=True,  # Ensure tick labels are shown
                              showgrid=True,  # Show grid lines for better readability
                              zeroline=False,  # Hide the zero line for a cleaner look
                              type='date'  # Ensure the type is set to date for proper time handling
                          ))

        st.plotly_chart(fig, use_container_width=True)

        # Display the stock data
        st.subheader("STOCK DATA")

        # Generate buy and sell signals based on support and resistance levels
        current_price = stock_data['Close'].iloc[-1]
        support_levels = [level[1] for level in grouped_levels if level[2] == 'support']
        resistance_levels = [level[1] for level in grouped_levels if level[2] == 'resistance']

        if resistance_levels and current_price > max(resistance_levels):
            st.subheader("Signal: Buy")
        elif support_levels and current_price < min(support_levels):
            st.subheader("Signal: Sell")
        else:
            st.subheader("Signal: Hold")

    # Calculate metrics
    metrics = calculate_metrics(results)

    # Get TradingView recommendation
    recommendation, buy_count, sell_count, neutral_count, indicators = get_tradingview_recommendation('AAPL', 'NASDAQ')
    st.divider()

    st.subheader(f"Recommendation: {(recommendation).replace('_', ' ')}")
    st.subheader(f"Buy Count: {buy_count} | Neutral Count: {neutral_count} | Sell Count: {sell_count}")

    # Display metrics
    st.write(
        f"Win Ratio: {metrics['Win Ratio']:.2f} | Loss Ratio: {metrics['Loss Ratio']:.2f} | Profit Factor: {metrics['Profit Factor']:.2f} | Average Win: {metrics['Average Win']:.2f} | Average Loss: {metrics['Average Loss']:.2f}")

    # Button to navigate to the more page
    if st.button("More", key="more_button"):
        st.session_state.page = "more"
        st.rerun()

    # Auto-reload every 30 seconds
    time.sleep(60)
    st.rerun()

# Function to display more page
def more_page():
    # Button to navigate back to the main page
    if st.button("Back to Main Page", key="back_to_main_button"):
        st.session_state.page = "main"
        st.rerun()

    st.title("More Information")

    # Get TradingView recommendation
    recommendation, buy_count, sell_count, neutral_count, indicators = get_tradingview_recommendation('AAPL', 'NASDAQ')

    st.subheader("TradingView TA Indicators")
    st.write(f"Recommendation: {recommendation}")
    st.write(f"Buy Count: {buy_count}")
    st.write(f"Sell Count: {sell_count}")
    st.write(f"Neutral Count: {neutral_count}")

    st.subheader("Indicators Details")

    handler = TA_Handler(
        symbol='AAPL',
        exchange='NASDAQ',
        screener="america",
        interval=Interval.INTERVAL_1_MINUTE,
        timeout=None)
    analysis = handler.get_analysis()

    # Create two columns with custom CSS
    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("**Moving Averages**")
        st.write(analysis.moving_averages)

    with col2:
        st.write("**Oscillators**")
        st.write(analysis.oscillators)

    st.subheader("Statistics")
    try:
        results = pd.read_csv('C:/Users/mredu_ykchdzs/pythonProject/Treading/trading_results.csv')
    except FileNotFoundError:
        st.error("The CSV file 'trading_results.csv' was not found. Please ensure the file exists.")
        return

    metrics = calculate_metrics(results)
    st.write(f"Win Ratio: {metrics['Win Ratio']:.2f}")
    st.write(f"Loss Ratio: {metrics['Loss Ratio']:.2f}")
    st.write(f"Profit Factor: {metrics['Profit Factor']:.2f}")
    st.write(f"Average Win: {metrics['Average Win']:.2f}")
    st.write(f"Average Loss: {metrics['Average Loss']:.2f}")

    # Button to navigate to the raw data page
    if st.button("Check Raw Data", key="check_raw_data_button"):
        st.session_state.page = "raw_data"
        st.rerun()

# Function to display raw data page
def raw_data_page():
    st.title("Raw Data")
    try:
        results = pd.read_csv('C:/Users/mredu_ykchdzs/pythonProject/Treading/trading_results.csv')
    except FileNotFoundError:
        st.error("The CSV file 'trading_results.csv' was not found. Please ensure the file exists.")
        return

    # Add filtering, sorting, and pagination
    st.subheader("Filter Data")
    filter_column = st.selectbox("Select column to filter by", results.columns)
    filter_value = st.text_input(f"Enter value for {filter_column}")
    if filter_value:
        results = results[results[filter_column] == filter_value]

    st.subheader("Sort Data")
    sort_column = st.selectbox("Select column to sort by", results.columns)
    sort_order = st.selectbox("Select sort order", ["Ascending", "Descending"])
    if sort_order == "Ascending":
        results = results.sort_values(by=sort_column, ascending=True)
    else:
        results = results.sort_values(by=sort_column, ascending=False)

    st.subheader("Paginate Data")
    page_size = st.number_input("Enter page size", min_value=1, value=10)
    total_pages = len(results) // page_size + (1 if len(results) % page_size else 0)
    page_number = st.number_input("Enter page number", min_value=1, max_value=total_pages, value=1)
    start_idx = (page_number - 1) * page_size
    end_idx = start_idx + page_size
    st.write(results.iloc[start_idx:end_idx])

    # Button to navigate back to the main page
    if st.button("Back to Main Page", key="back_to_main_button_raw_data"):
        st.session_state.page = "main"
        st.rerun()

# Determine which page to displayin this code you
if "page" not in st.session_state:
    st.session_state.page = "main"

if st.session_state.page == "main":
    main()
elif st.session_state.page == "more":
    more_page()
elif st.session_state.page == "raw_data":
    raw_data_page()

# streamlit run C:\Users\mredu_ykchdzs\pythonProject\Treading\Dashboard.py
