# Stock_Market_Analysis
A comprehensive real-time stock market analysis dashboard built with Streamlit, featuring live data visualization, price prediction using machine learning, and interactive charts. The application provides real-time stock market insights with a clean, modern interface.

#Features
📊 Real-Time Market Dashboard
Live stock data from Yahoo Finance for 27 major stocks
Top and bottom performers with daily change percentages
Interactive performance analysis charts
Auto-refresh functionality (every 30 seconds)
Responsive design with custom styling
🔮 Price Prediction
Machine learning-based stock price forecasting using Facebook Prophet
Historical data analysis for accurate predictions
Customizable prediction periods (30-365 days)
Confidence intervals and prediction accuracy metrics
Interactive prediction charts with historical and forecast data
📈 Historical Analysis
Comprehensive historical stock data visualization
Technical indicators and trend analysis
Custom date range selection
Multiple chart types (line, candlestick, volume)
📊 Market Overview
Sector-wise market analysis
Market capitalization insights
Dividend yield tracking
PE ratio analysis
🔍 Stock Comparison
Side-by-side stock comparison
Performance metrics comparison
Correlation analysis
Custom stock selection
Technologies Used
Frontend: Streamlit
Data Sources: Yahoo Finance (yfinance)
Machine Learning: Facebook Prophet for price prediction
Visualization: Plotly for interactive charts
Styling: Custom CSS for modern UI
Installation
Clone the repository:

git clone https://github.com/yourusername/stock-market-analysis.git
cd stock-market-analysis
Install dependencies:

pip install -r requirements.txt
Run the application:

streamlit run dashboard.py
Usage
Open your browser and navigate to http://localhost:8501
Explore the main dashboard for real-time market data
Use the sidebar to navigate between different analysis pages
Select stocks for prediction and analysis
Customize prediction periods and view forecast results
Features in Detail
Dashboard Page
Real-time stock prices and changes
Top 10 performing stocks
Bottom 10 performing stocks
Performance comparison charts
Auto-refresh with countdown timer
Price Prediction Page
Select any stock from the tracked list
Choose prediction period (30-365 days)
View historical data and predictions
Confidence intervals for forecast accuracy
Component analysis (trend, seasonality)
Historical Analysis Page
Detailed historical price charts
Volume analysis
Moving averages and technical indicators
Custom date range selection
Market Overview Page
Sector distribution
Market cap analysis
Dividend yield insights
PE ratio comparisons
Stock Comparison Page
Compare multiple stocks simultaneously
Performance metrics
Correlation matrix
Side-by-side analysis
Data Sources
The application fetches real-time data from Yahoo Finance for the following stocks:
AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA, JPM, JNJ, V, PG, UNH, HD, BAC, MA, DIS, NFLX, ADBE, CRM, INTC, VZ, CSCO, PFE, KO, PEP, WMT, MRK

Disclaimer
This application is for educational and informational purposes only. Stock price predictions are not financial advice. Always consult with qualified financial advisors before making investment decisions. Past performance does not guarantee future results.

Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

License
This project is licensed under the MIT License - see the LICENSE file for details.
