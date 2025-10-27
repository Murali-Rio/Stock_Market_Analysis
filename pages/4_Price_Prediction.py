import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from prophet import Prophet
from datetime import datetime, timedelta
import logging
import yfinance as yf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Stock Price Prediction", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
<style>
.header {
    padding: 2rem;
    margin-bottom: 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.metric-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.prediction-card {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.disclaimer {
    background: #f8f9fa;
    padding: 1rem;
    border-left: 5px solid #ffc107;
    border-radius: 5px;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=30)
def load_stock_data():
    """Fetch live stock data from Yahoo Finance"""
    try:
        # List of popular stock symbols to track
        symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM',
            'JNJ', 'V', 'PG', 'UNH', 'HD', 'BAC', 'MA', 'DIS', 'NFLX', 'ADBE',
            'CRM', 'INTC', 'VZ', 'CSCO', 'PFE', 'KO', 'PEP', 'WMT', 'MRK'
        ]

        logger.info(f"Fetching live data for {len(symbols)} stocks...")

        # Fetch data for all symbols at once
        data = yf.download(
            tickers=symbols,
            period="2d",  # Get 2 days of data to calculate daily change
            group_by="ticker",
            auto_adjust=True,
            prepost=False,
            threads=True
        )

        # Prepare the dataframe
        stock_data = []

        for symbol in symbols:
            try:
                # Get today's and yesterday's data for the symbol
                if len(symbols) == 1:
                    # When only one symbol, data structure is different
                    today_data = data.iloc[-1]
                    yesterday_data = data.iloc[-2]
                else:
                    today_data = data[symbol].iloc[-1]
                    yesterday_data = data[symbol].iloc[-2]

                # Get additional info
                ticker = yf.Ticker(symbol)
                info = ticker.info

                # Calculate daily change percentage
                price = today_data['Close']
                prev_price = yesterday_data['Close']
                change = ((price - prev_price) / prev_price) * 100

                # Get sector information (if available)
                sector = info.get('sector', 'Unknown')

                # Get market cap (if available)
                market_cap = info.get('marketCap', 0)

                # Get PE ratio (if available)
                pe_ratio = info.get('trailingPE', None)

                # Get dividend yield (if available)
                dividend_yield = info.get('dividendYield', 0)
                if dividend_yield:
                    dividend_yield = dividend_yield * 100  # Convert to percentage

                # Add to our list
                stock_data.append({
                    'symbol': symbol,
                    'name': info.get('shortName', symbol),
                    'sector': sector,
                    'price': price,
                    'change': change,
                    'volume': today_data['Volume'],
                    'market_cap': market_cap,
                    'pe_ratio': pe_ratio,
                    'dividend_yield': dividend_yield
                })

            except Exception as e:
                logger.warning(f"Error processing {symbol}: {str(e)}")
                continue

        # Convert to DataFrame
        df = pd.DataFrame(stock_data)
        logger.info(f"Successfully fetched data for {len(df)} stocks")
        return df

    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def load_historical_data(symbol, years=2):
    """Fetch historical stock data for prediction"""
    try:
        logger.info(f"Fetching historical data for {symbol}...")
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=f"{years}y", interval="1d")
        if data.empty:
            logger.warning(f"No historical data found for {symbol}")
            return None
        # Prepare data for Prophet
        df = data.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
        # Remove timezone from ds column as Prophet doesn't support it
        df['ds'] = df['ds'].dt.tz_localize(None)
        logger.info(f"Successfully fetched {len(df)} days of historical data for {symbol}")
        return df
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
        return None



def train_prophet_model(historical_data, periods=30):
    """Train Prophet model and generate forecast"""
    model = Prophet(
        daily_seasonality=True,
        yearly_seasonality=True,
        weekly_seasonality=True,
        changepoint_prior_scale=0.05
    )
    
    model.fit(historical_data)
    
    # Create future dataframe
    future = model.make_future_dataframe(periods=periods)
    
    # Generate forecast
    forecast = model.predict(future)
    
    return model, forecast

def plot_prediction(historical_data, forecast, stock_symbol, prediction_days):
    """Create plot with historical data and prediction"""
    fig = go.Figure()

    # Add historical data
    fig.add_trace(go.Scatter(
        x=historical_data['ds'],
        y=historical_data['y'],
        mode='lines',
        name='Historical',
        line=dict(color='#1f77b4')
    ))

    # Add prediction
    fig.add_trace(go.Scatter(
        x=forecast['ds'][-prediction_days:],  # Only show the prediction part
        y=forecast['yhat'][-prediction_days:],
        mode='lines',
        name='Prediction',
        line=dict(color='#ff7f0e', width=3)
    ))

    # Add prediction intervals
    fig.add_trace(go.Scatter(
        x=forecast['ds'][-prediction_days:],
        y=forecast['yhat_upper'][-prediction_days:],
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=forecast['ds'][-prediction_days:],
        y=forecast['yhat_lower'][-prediction_days:],
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(255, 127, 14, 0.2)',
        name='95% Confidence'
    ))

    fig.update_layout(
        title=f'{stock_symbol} Price Prediction ({prediction_days} Days)',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        height=600,
        hovermode='x unified'
    )

    return fig

def main():
    # Header
    st.markdown("""
    <div class="header">
        <h1 style="margin: 0;">🔮 Stock Price Prediction</h1>
        <p style="margin: 0;">Forecast future stock prices using machine learning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_stock_data()
    if df is None or df.empty:
        st.error("No data available. Please check if the CSV file exists and contains valid data.")
        return
    
    # Stock selection
    selected_stock = st.selectbox(
        "Select a stock to predict",
        options=df['symbol'].unique(),
        format_func=lambda x: f"{x} - {df[df['symbol'] == x]['name'].iloc[0]}"
    )
    
    # Get current stock info
    stock_info = df[df['symbol'] == selected_stock].iloc[0]
    
    # Prediction period selection
    prediction_days = st.slider(
        "Prediction period (days)",
        min_value=30,
        max_value=365,
        value=365,
        step=30
    )

    # Load historical data
    historical_data = load_historical_data(selected_stock, years=2)
    if historical_data is None or historical_data.empty:
        st.error(f"No historical data available for {selected_stock}. Please select another stock.")
        return

    # Train model and get forecast
    with st.spinner("Training prediction model..."):
        model, forecast = train_prophet_model(historical_data, periods=prediction_days)
    
    # Display current price and predicted price
    col1, col2, col3 = st.columns(3)

    current_price = stock_info['price']
    predicted_price = forecast['yhat'].iloc[-1]
    price_change = ((predicted_price - current_price) / current_price) * 100

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Current Price",
            f"${current_price:.2f}",
            f"{stock_info['change']:.2f}%"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
        st.metric(
            f"Predicted Price ({prediction_days} days)",
            f"${predicted_price:.2f}",
            f"{price_change:.2f}%"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Prediction Confidence",
            f"±${(forecast['yhat_upper'].iloc[-1] - forecast['yhat_lower'].iloc[-1])/2:.2f}"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Plot prediction
    fig = plot_prediction(historical_data, forecast, selected_stock, prediction_days)
    st.plotly_chart(fig, use_container_width=True)
    
    # Show forecast components
    st.subheader("Forecast Components")
    
    # Plot forecast components
    with st.spinner("Generating component plots..."):
        fig2 = model.plot_components(forecast)
        st.pyplot(fig2)
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
    <h4>⚠️ Important Disclaimer</h4>
    <p>This stock price prediction is for educational and informational purposes only. It is not financial advice, and you should not make investment decisions based solely on this prediction. Stock prices are influenced by many unpredictable factors, and past performance does not guarantee future results. Always consult with a qualified financial advisor before making any investment decisions.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
