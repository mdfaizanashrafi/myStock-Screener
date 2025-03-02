from http.client import responses

import requests
import yfinance as yf
import pandas as pd
import os
import time
from datetime import datetime

#fetch historical stock data for a given symbol using yfinance
def fetch_stock_data(symbol,period='1y',interval='1d', retries=3, timeout=10):
    """Args:
            symbol: stock symbol like REL,OIC,etc
            period: time period for data like 1d,1mo or 1y
            interval: data interval 1m,1h,or 1d"""

    for attempt in range(retries):
        try:
            #download stock data
            stock = yf.Ticker(symbol)
            df = stock.history(period, interval=interval, timeout= timeout)
            #data frame containing historical stock data

            if df.empty:
                raise ValueError(f"No data found for symbol: {symbol}")
                #Clean up column names:
            df.reset_index(inplace=True)  #Reset index to include 'Date' as a column
            return df
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt<retries - 1:
                time.sleep(2)
            else:
                raise ValueError(f"Failed to fetch data for symbol: {symbol} after {retries} attempts.")

    df.rename(columns={'Datetime':'Date'},inplace=True) #Rename 'Datetime' to 'Date' if needed

#CACHING: simple caching mechanism to store fetched data temporarily

CACHE_DIR = 'cache/'
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_stock_data_with_cache(symbol,period='1y',interval='1d'):
    cache_file = os.path.join(CACHE_DIR, f"{symbol}_{period}_{interval}.csv")

    if os.path.exists(cache_file):
        #load data from cache
        return pd.read_csv(cache_file,parse_dates=['Date'])

    #fetch data from yfinance
    df = fetch_stock_data(symbol,period,interval)

    #save data to cache
    df.to_csv(cache_file,index= False)
    return df

#filter columns: for close price
def get_close_prices(df):
    return df[['Date','Close']]

#Handling missing data: dropping or replacing them
def clean_stock_data(df):
    return df.dropna() #drops rows with the missing values

#Resampling data to different timeframes
def resample_to_weekly(df):
    df.set_index('Date',inplace=True)
    weekly_data = df.resample('W').last()  #gets the last price of each week
    weekly_data.reset_index(inplace=True)
    return weekly_data

#Resampling to custom interval
def resample_to_custom_interval(df, interval='W'):
    #set 'Date' as the index for resampling
    df.set_index('Date',inplace=True)

    #resample data
    resampled = df.resample(interval).agg({
        # for given intervals
        'Open':'first',
        'High':'max',
        'Low':'min',
        'Close':'last',
        'Volume':'sum'
    })

    #calculate percantage change in close price
    resampled['P%_Change']= resampled['Close'].pct_change()*100

    #reset index to include 'Date' as a column
    resampled.reset_index(inplace=True)

    return resampled

#Add multiple resampling optionsn:

def get_resampled_data(df,interval='W'):
    if interval == 'D':
        #no resampling meeded for daily data
        return df
    return resample_to_custom_interval(df,interval)


#setch real time stock data
def fetch_real_time_stock_data(symbol):
    try:
        stock=yf.Ticker(symbol)
        data=stock.info
        return {
            "symbol":symbol,
            "price":data.get("regularMarketPrice"),
            "volume":data.get("regularMarketVolume"),
            "market_cap":data.get("marketCap"),
            "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise Exception(f"Error fetching real-time data for {symbol}:{e}")

#fetch financial statements like balance sheets,income statements and cash flow statements

def fetch_financial_statements(symbol):
    try:
        stock=yf.Ticker(symbol)
        balance_sheet=stock.balance_sheet
        income_statement=stock.financials
        cash_flow=stock.cash_flow
        return {
            "balance_sheet":balance_sheet.to_dict(),
            "income_statement":income_statement.to_dict(),
            "cash_flow":cash_flow.to_dict()
        }
    except Exception as e:
        raise Exception(f"Error fetching financial statements for {symbol}:{e}")

#filter stocks
def filter_stocks_by_price(stocks,min_price,max_price):
    return stocks[(stocks['Close']>=min_price)&(stocks['Close']<=max_price)]

def filter_stocks_by_volume(stocks,min_volumes):
    return stocks[stocks['Volume']>=min_volumes]

#cache data locally
def cache_date(symbol,data):
    data.to_csv(f"data/{symbol}_data.csv")

def load_cache_data(symbol):
    try:
        return pd.read_csv(f"data/{symbol}_data.csv",index_col=0,parse_dates=True)
    except FileNotFoundError:
        return None


#FETCH SECTOR AND INDUSTRY DATA FOR A GIVEN STOCK
def fetch_sector_industry(symbol):
    try:
        stock=yf.Ticker(symbol)
        info=stock.info
        return {
            "Sector": info.get("sector"),
            "Industry": info.get("industry")}
    except Exception as e:
        raise Exception(f"Error fetching sector/industry data for {symbol}:{e}")


#Backtesting trading strategies:
#simulate a simple trading strategy

def backtest_strategy(df,rsi_column='RSI',buy_threshold=30,sell_threshold=70):
    df['Signal']=0
    df.loc[df[rsi_column]<buy_threshold,'Signal']=1
    df.loc[df[rsi_column]>sell_threshold,'Signal']=-1
    df['Positions']=df['Signal'].cumsum()
    return df

#Allow isers to export stock data to excel for further analysis
def export_to_excel(df,filename="Stock_Data.xlsx"):
    df.to_excel(filename,index=False)
    print(f"Data exported to {filename}")


