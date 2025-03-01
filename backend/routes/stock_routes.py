from flask import Flask,jsonify,request
import os
import sys
import os

from backend.utils.data_fetcher import (
fetch_stock_data_with_cache,
get_resampled_data,
add_technical_indicators,
filter_by_date_range
)

app = Flask(__name__)

@app.route('/api/stocks/<symbol>',methods=['GET'])
def get_stock_date(symbol):
    try:
        #parse query parameters
        period = request.args.get('period','1y') #default: 1 year
        interval=request.args.get('interval','1d') #defaults: daily
        resample=request.args.get('resample',None) #optional: resample interval ('W','M',etc.)
        start_date=request.args.get('start_date',None) #optional: filter by start date
        end_date=request.args.get('end_date',None) #optional: filter by end date
        indicators=request.args.getlist('indicators') #optional: list of technical indicators

        #Fetch stock data
        stock_data=fetch_stock_data_with_cache(symbol,period=period,interval=interval)

        #filter by date range if provided
        if start_date or end_date:
            stock_data=filter_by_date_range(stock_data,start_date,end_date)

        #resample data if requested
        if resample:
            stock_data=get_resampled_data(stock_data,interval=resample)

        #add technical indicators if requested
        if indicators:
            stock_data=add_technical_indicators(stock_data,indicators)

        #return JSON response
        return jsonify(stock_data.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error':str(e)}),400

