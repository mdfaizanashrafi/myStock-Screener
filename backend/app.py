from flask import Flask,jsonify,request
from flask_cors import CORS #cross-origin-resource-sharing

import logging
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

from dotenv import load_dotenv
import os

from backend.utils.data_fetcher import export_to_excel
from backend.utils.technical_indicators import calculate_sma, calculate_rsi, calculate_boolinger_bands
#import utility func()
from utils.data_fetcher import (
fetch_stock_data_with_cache,fetch_stock_data,
fetch_real_time_stock_data,fetch_financial_statements,
fetch_sector_industry,filter_stocks_by_price,
filter_stocks_by_volume,resample_to_custom_interval,
resample_to_weekly, get_resampled_data
)

from utils.technical_indicators import (
calculate_stock_correlation,calculate_macd,
calculate_atr,calculate_sharpe_ratio,
calculate_stochastic_oscillator,detect_candlestick_patterns,
add_technical_indicators,filter_by_date_range,
filter_by_macd,filter_by_rsi,
find_support_resistance
)

load_dotenv()  #Load environment variables from .env

#initialize Flask app
app = Flask(__name__)
CORS(app)  #rnable CORS for frontend-backend communication

#Health check endpoint
@app.route('/')
def home():
    return f"BackEnd is running! {os.getenv('FLASK_ENV')}  mode!"

#fetch historical stock data
@app.route('/api/stocks/historical/<symbol>',methods=['GET'])
def get_historical_data(symbol):
    try:
        period=request.args.get('period','1y')
        interval=request.args.get('interval','1d')
        df=fetch_stock_data(symbol,period=period,interval=interval)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error":str(e)}),400

#fetch real time stock data
@app.route('/api/stocks/realtime/<symbol>',methods=['GET'])
def get_real_time_data(symbol):
    try:
        real_time_data=fetch_real_time_stock_data(symbol)
        return jsonify(real_time_data)
    except Exception as e:
        return jsonify({"error":str(e)}),400

#fetch financial statements:
@app.route('/api/stocks/financials/<symbol>',methods=['GET'])
def get_financial_statements(symbol):
    try:
        financials=fetch_financial_statements(symbol)
        return jsonify(financials)
    except Exception as e:
        return jsonify({"error":str(e)}),400

#filter stock by price range:
@app.route('/api/stocks/filter/price',methods=['GET'])
def filter_stocks_by_price_range():
    try:
        min_price=float(request.args.get('min_price'))
        max_price=float(request.args.get('max_price'))
        symbol=request.args.get('symbol')
        df=fetch_stock_data(symbol,period="1y",interval="1d")
        filtered_df=filter_stocks_by_price(df,min_price=min_price,max_price=max_price)
        return jsonify(filtered_df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error":str(e)}),400

#filter stocks by volume
@app.route('/api/stocks/filter/volume',methods=['GET'])
def filter_stocks_by_volume_threshold():
    try:
        min_volume=int(request.args.get('min_volume'))
        symbol=request.args.get('symbol')
        df=fetch_stock_data(symbol,period="1y",interval="1d")
        filtered_df=filter_stocks_by_volume(df,min_volume=min_volume)
        return jsonify(filtered_df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error":str(e)}),400

#calculate technical indicators
@app.route('/api/stocks/indicators/<symbol>',methods=['GET'])
def get_technical_indicators(symbol):
    try:
        df = fetch_stock_data(symbol,period='1y',interval="1d")
        df=calculate_sma(df,window=10)
        df= calculate_rsi(df,window=14)
        df=calculate_boolinger_bands(df,window=20)
        df=calculate_macd(df)
        df=calculate_atr(df)
        df=calculate_stochastic_oscillator(df)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error":str(e)}),400

#fetch sector and industry data
@app.route('/api/stocks/sector-industry/<symbol>',methods=['GET'])
def get_sector_industry(symbol):
    try:
        sector_industry_data=fetch_sector_industry(symbol)
        return jsonify(sector_industry_data)
    except Exception as e:
        return jsonify({"error":str(e)}),400

#detect canclestick patterm
@app.route('/api/stocks/patterns/<symbol>',methods=['GET'])
def detect_patterns(symbol):
    try:
        df=fetch_stock_data(symbol,period="1mo",interval="1d")
        df=detect_candlestick_patterns(df)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error":str(e)}),400

#export stock data to excel
@app.route('/api/stocks/export/<symbol>',methods=['GET'])
def export_stock_data(symbol):
    try:
        df=fetch_stock_data(symbol,period="1y",interval="1d")
        filename=f"{symbol}_stock_data.xlsx"
        export_to_excel(df,filename=filename)
        return jsonify({"message":f"Data Exported to {filename}"})
    except Exception as e:
        return jsonify({"error":str(e)}),400


#Run the FLASK app
if __name__ == '__main__':
    app.run(debug=True)

