import streamlit as st
import pandas as pd
import plotly.express as px
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
    page_title="Stock Comparison",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .header {
        background-color: #343a40;
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .comparison-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a049;
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

def get_stock_metrics(df, symbol):
    """Get metrics for a specific stock"""
    stock_data = df[df['symbol'] == symbol].iloc[0]
    return {
        'price': stock_data['price'],
        'change': stock_data['change'],
        'volume': stock_data['volume'],
        'market_cap': stock_data['market_cap'],
        'pe_ratio': stock_data['pe_ratio'],
        'dividend_yield': stock_data['dividend_yield'],
        'sector': stock_data['sector']
    }

def create_comparison_chart(df, stock1, stock2):
    """Create a comparison chart for two stocks"""
    # Create a DataFrame with both stocks' data
    comparison_data = pd.DataFrame({
        'Metric': ['Price', 'Change', 'Volume', 'Market Cap', 'P/E Ratio', 'Dividend Yield'],
        stock1: [
            df[df['symbol'] == stock1]['price'].iloc[0],
            df[df['symbol'] == stock1]['change'].iloc[0],
            df[df['symbol'] == stock1]['volume'].iloc[0],
            df[df['symbol'] == stock1]['market_cap'].iloc[0],
            df[df['symbol'] == stock1]['pe_ratio'].iloc[0],
            df[df['symbol'] == stock1]['dividend_yield'].iloc[0]
        ],
        stock2: [
            df[df['symbol'] == stock2]['price'].iloc[0],
            df[df['symbol'] == stock2]['change'].iloc[0],
            df[df['symbol'] == stock2]['volume'].iloc[0],
            df[df['symbol'] == stock2]['market_cap'].iloc[0],
            df[df['symbol'] == stock2]['pe_ratio'].iloc[0],
            df[df['symbol'] == stock2]['dividend_yield'].iloc[0]
        ]
    })
    
    # Create the comparison chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=stock1,
        x=comparison_data['Metric'],
        y=comparison_data[stock1],
        marker_color='#1f77b4',
        text=comparison_data[stock1].round(2),
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        name=stock2,
        x=comparison_data['Metric'],
        y=comparison_data[stock2],
        marker_color='#ff7f0e',
        text=comparison_data[stock2].round(2),
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Stock Comparison',
        xaxis_title='Metrics',
        yaxis_title='Values',
        barmode='group',
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_radar_chart(df, stock1, stock2):
    """Create a radar chart for comparing stocks"""
    metrics = ['price', 'change', 'volume', 'market_cap', 'pe_ratio', 'dividend_yield']
    stock1_data = df[df['symbol'] == stock1].iloc[0]
    stock2_data = df[df['symbol'] == stock2].iloc[0]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=[stock1_data[m] for m in metrics],
        theta=metrics,
        fill='toself',
        name=stock1,
        line_color='#1f77b4'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[stock2_data[m] for m in metrics],
        theta=metrics,
        fill='toself',
        name=stock2,
        line_color='#ff7f0e'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                type='log'
            )
        ),
        showlegend=True,
        title='Radar Chart Comparison',
        height=500
    )
    
    return fig

def create_volume_distribution(df, stock1, stock2):
    """Create a volume distribution chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df[df['symbol'] == stock1]['volume'],
        name=stock1,
        marker_color='#1f77b4',
        opacity=0.75
    ))
    
    fig.add_trace(go.Histogram(
        x=df[df['symbol'] == stock2]['volume'],
        name=stock2,
        marker_color='#ff7f0e',
        opacity=0.75
    ))
    
    fig.update_layout(
        title='Volume Distribution',
        xaxis_title='Volume',
        yaxis_title='Count',
        barmode='overlay',
        height=400
    )
    
    return fig

def create_sector_pie_chart(df, stock1, stock2):
    """Create a pie chart showing sector distribution"""
    sector_data = df[df['symbol'].isin([stock1, stock2])]
    
    fig = px.pie(
        sector_data,
        values='market_cap',
        names='sector',
        title='Sector Distribution',
        color='symbol',
        color_discrete_sequence=['#1f77b4', '#ff7f0e']
    )
    
    fig.update_layout(
        height=400,
        showlegend=True
    )
    
    return fig

def main():
    # Header
    st.markdown("""
    <div class="header">
        <h1 style="margin: 0;">📊 Stock Comparison</h1>
        <p style="margin: 0;">Compare two stocks side by side</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_stock_data()
    if df is None or df.empty:
        st.error("No data available. Please check if the CSV file exists and contains valid data.")
        return
    
    # Stock selection
    col1, col2 = st.columns(2)
    
    with col1:
        stock1 = st.selectbox(
            "Select First Stock",
            options=df['symbol'].unique(),
            index=0
        )
    
    with col2:
        stock2 = st.selectbox(
            "Select Second Stock",
            options=df['symbol'].unique(),
            index=1
        )
    
    if stock1 == stock2:
        st.warning("Please select two different stocks for comparison.")
        return
    
    # Get stock metrics
    stock1_metrics = get_stock_metrics(df, stock1)
    stock2_metrics = get_stock_metrics(df, stock2)
    
    # Display stock cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="comparison-card">
            <h3>{stock1}</h3>
            <p>Sector: {stock1_metrics['sector']}</p>
            <h4>${stock1_metrics['price']:,.2f}</h4>
            <p style="color: {'green' if stock1_metrics['change'] >= 0 else 'red'}">
                {stock1_metrics['change']:+.2f}%
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="comparison-card">
            <h3>{stock2}</h3>
            <p>Sector: {stock2_metrics['sector']}</p>
            <h4>${stock2_metrics['price']:,.2f}</h4>
            <p style="color: {'green' if stock2_metrics['change'] >= 0 else 'red'}">
                {stock2_metrics['change']:+.2f}%
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main comparison chart
    st.markdown("### 📈 Metrics Comparison")
    fig = create_comparison_chart(df, stock1, stock2)
    st.plotly_chart(fig, use_container_width=True)
    
    # Additional visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Radar Chart")
        radar_fig = create_radar_chart(df, stock1, stock2)
        st.plotly_chart(radar_fig, use_container_width=True)
        
        st.markdown("### 📊 Volume Distribution")
        volume_fig = create_volume_distribution(df, stock1, stock2)
        st.plotly_chart(volume_fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Sector Distribution")
        sector_fig = create_sector_pie_chart(df, stock1, stock2)
        st.plotly_chart(sector_fig, use_container_width=True)
        
        # Detailed metrics
        st.markdown("### 📊 Detailed Metrics")
        st.markdown("""
        <div class="metric-card">
            <h4>Volume</h4>
            <p>{stock1}: {volume1:,.0f}</p>
            <p>{stock2}: {volume2:,.0f}</p>
        </div>
        """.format(
            stock1=stock1,
            stock2=stock2,
            volume1=stock1_metrics['volume'],
            volume2=stock2_metrics['volume']
        ), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4>Market Cap</h4>
            <p>{stock1}: ${market_cap1:,.2f}B</p>
            <p>{stock2}: ${market_cap2:,.2f}B</p>
        </div>
        """.format(
            stock1=stock1,
            stock2=stock2,
            market_cap1=stock1_metrics['market_cap']/1e9,
            market_cap2=stock2_metrics['market_cap']/1e9
        ), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4>Valuation</h4>
            <p>{stock1} P/E: {pe1:.2f}</p>
            <p>{stock2} P/E: {pe2:.2f}</p>
            <p>{stock1} Div Yield: {div1:.2f}%</p>
            <p>{stock2} Div Yield: {div2:.2f}%</p>
        </div>
        """.format(
            stock1=stock1,
            stock2=stock2,
            pe1=stock1_metrics['pe_ratio'],
            pe2=stock2_metrics['pe_ratio'],
            div1=stock1_metrics['dividend_yield'],
            div2=stock2_metrics['dividend_yield']
        ), unsafe_allow_html=True)

if __name__ == "__main__":
    main() 