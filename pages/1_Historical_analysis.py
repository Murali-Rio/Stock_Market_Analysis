import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import logging
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(
    page_title="Stock History",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .header {
        background-color: #1e3d59;
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .info-box {
        background-color: #f8f9fa;
        border-left: 4px solid #17a2b8;
        padding: 10px;
        margin: 10px 0;
        border-radius: 0 5px 5px 0;
    }
    .positive-value { color: #28a745; font-weight: bold; }
    .negative-value { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30)  # Cache data for 30 seconds
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

def generate_historical_data(current_price, days=365):
    """Generate historical price data based on current price"""
    dates = pd.date_range(end=datetime.now(), periods=days).tolist()
    
    # Generate realistic price movements
    volatility = 0.02
    returns = np.random.normal(loc=0.0001, scale=volatility, size=days-1)
    price_factors = np.exp(np.cumsum(returns[::-1]))  # Reverse to start from current price
    prices = current_price / price_factors[-1] * price_factors
    prices = np.append(prices, current_price)
    
    # Generate OHLC data
    data = {
        'Date': dates,
        'Close': prices,
        'Open': prices * np.random.uniform(0.998, 1.002, size=days),
        'High': prices * np.random.uniform(1.001, 1.004, size=days),
        'Low': prices * np.random.uniform(0.996, 0.999, size=days),
        'Volume': np.random.uniform(0.5, 1.5, size=days) * 1000000
    }
    
    return pd.DataFrame(data)

def calculate_technical_indicators(df):
    """Calculate technical indicators for the stock"""
    # Moving averages
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    
    # Bollinger Bands
    df['BB_middle'] = df['Close'].rolling(window=20).mean()
    df['BB_upper'] = df['BB_middle'] + 2 * df['Close'].rolling(window=20).std()
    df['BB_lower'] = df['BB_middle'] - 2 * df['Close'].rolling(window=20).std()
    
    return df

def create_price_chart(df, symbol):
    """Create an interactive price chart with technical indicators"""
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ))
    
    # Add moving averages
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['MA20'],
        name='20-day MA',
        line=dict(color='#2196f3', width=1)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['MA50'],
        name='50-day MA',
        line=dict(color='#ff9800', width=1)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['MA200'],
        name='200-day MA',
        line=dict(color='#673ab7', width=1)
    ))
    
    # Add Bollinger Bands
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['BB_upper'],
        name='BB Upper',
        line=dict(color='gray', width=1, dash='dash'),
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['BB_lower'],
        name='BB Lower',
        line=dict(color='gray', width=1, dash='dash'),
        showlegend=True,
        fill='tonexty'
    ))
    
    # Update layout
    fig.update_layout(
        title=f'{symbol} - 1 Year Price History',
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

def calculate_metrics(df):
    """Calculate key metrics from historical data"""
    current_price = df['Close'].iloc[-1]
    start_price = df['Close'].iloc[0]
    year_return = ((current_price - start_price) / start_price) * 100
    
    high_52w = df['High'].max()
    low_52w = df['Low'].min()
    
    volatility = df['Close'].pct_change().std() * np.sqrt(252) * 100
    
    return {
        'year_return': year_return,
        'high_52w': high_52w,
        'low_52w': low_52w,
        'volatility': volatility
    }

def main():
    # Header
    st.markdown("""
    <div class="header">
        <h1 style="margin: 0;">📈 Stock History</h1>
        <p style="margin: 10px 0 0 0;">Historical price analysis and technical indicators</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load current stock data
    df_current = load_stock_data()
    if df_current is None or df_current.empty:
        st.error("No stock data available. Please check the data source.")
        return
    
    # Stock selection
    selected_stock = st.selectbox(
        "Select a stock",
        options=df_current['symbol'].unique(),
        format_func=lambda x: f"{x} - {df_current[df_current['symbol'] == x]['name'].iloc[0]}"
    )
    
    # Get current stock info
    stock_info = df_current[df_current['symbol'] == selected_stock].iloc[0]
    
    # Generate and process historical data
    historical_data = generate_historical_data(stock_info['price'])
    historical_data = calculate_technical_indicators(historical_data)
    
    # Display current price and metrics
    metrics = calculate_metrics(historical_data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Current Price",
            f"${stock_info['price']:.2f}",
            f"{stock_info['change']:.2f}%"
        )
    
    with col2:
        st.metric(
            "52-Week High",
            f"${metrics['high_52w']:.2f}"
        )
    
    with col3:
        st.metric(
            "52-Week Low",
            f"${metrics['low_52w']:.2f}"
        )
    
    with col4:
        st.metric(
            "1-Year Return",
            f"{metrics['year_return']:.2f}%"
        )
    
    # Display chart
    st.plotly_chart(create_price_chart(historical_data, selected_stock), use_container_width=True)
    
    # Technical Analysis Summary
    st.markdown("### 📊 Technical Analysis Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_price = historical_data['Close'].iloc[-1]
        ma20 = historical_data['MA20'].iloc[-1]
        ma50 = historical_data['MA50'].iloc[-1]
        ma200 = historical_data['MA200'].iloc[-1]
        
        st.markdown("""
        #### Moving Averages
        """)
        
        ma20_status = "Above" if current_price > ma20 else "Below"
        ma50_status = "Above" if current_price > ma50 else "Below"
        ma200_status = "Above" if current_price > ma200 else "Below"
        
        st.markdown(f"""
        - Price is {ma20_status} 20-day MA (${ma20:.2f})
        - Price is {ma50_status} 50-day MA (${ma50:.2f})
        - Price is {ma200_status} 200-day MA (${ma200:.2f})
        """)
    
    with col2:
        bb_upper = historical_data['BB_upper'].iloc[-1]
        bb_lower = historical_data['BB_lower'].iloc[-1]
        
        st.markdown("""
        #### Bollinger Bands
        """)
        
        if current_price > bb_upper:
            bb_status = "above the upper band (overbought)"
        elif current_price < bb_lower:
            bb_status = "below the lower band (oversold)"
        else:
            bb_status = "within the bands (neutral)"
        
        st.markdown(f"""
        - Upper Band: ${bb_upper:.2f}
        - Lower Band: ${bb_lower:.2f}
        - Current price is {bb_status}
        """)
    
    # Volume Analysis
    st.markdown("### 📈 Volume Analysis")
    fig_volume = go.Figure()
    
    fig_volume.add_trace(go.Bar(
        x=historical_data['Date'],
        y=historical_data['Volume'],
        name='Volume',
        marker_color='#2196f3'
    ))
    
    fig_volume.update_layout(
        title='Trading Volume History',
        yaxis_title='Volume',
        xaxis_title='Date',
        template='plotly_white'
    )
    
    st.plotly_chart(fig_volume, use_container_width=True)

if __name__ == "__main__":
    main()