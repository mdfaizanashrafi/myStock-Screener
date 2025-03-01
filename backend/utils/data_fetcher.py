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

#adding technical indicators to the stock data:
#Moving Average (MA), Relative Strength Index (RSI) and Bollinger Bands

def add_technical_indicators(df,indicators):
    for indicator in indicators:
        if indicator == 'MA':
            #calculate 10days and 50 days moving avg
            df['MA_10'] = df['Close'].rolling(window=10).mean()
            df['MA_50'] = df['Close'].rolling(window=50).mean()

        elif indicator == 'RSI':
            #calculate 14-day RSI (Relative Strength Index)
            delta = df['CLose'].diff()  #calculates between concsec closing price
            gain = (delta.where(delta > 0,0)).rolling(window=14).mean() #keeps positive value and replaces negative to 0
            loss = (-delta.where(delta< 0,0)).rolling(window=14).mean() #keeps megative value and converts into positive, and converts positive to 0
            rs = gain/loss.replace(0,1e-10) #relative stength, replace 0 with a very small number
            df['RSI'] = 100 - (100/(1+rs))

        elif indicator == 'BB': #calculate bollinger bands
            rolling_mean = df['CLose'].rolling(window=20).mean()
            rolling_std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = rolling_mean+(2*rolling_std)
            df['BB_Lower'] = rolling_mean-(2*rolling_std)
    return df

#filter by date range
def filter_by_date_range(df,date_column,start_date,end_date):
    #convert start date and end date to datetime
    start_date=pd.to_datetime(start_date)
    end_date=pd.to_datetime(end_date)

    #filter the DataFrame
    filtered_df = df[(df[date_column]>=start_date)&(df[date_column]<=end_date)]
    return filtered_df

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


#calculate moving AVERAGES CONVERGENCE DIVERGENCE (MACD)
def calculate_macd(df,short_window=12,long_window=26,signal_window=9):
    df['EMA_Short']=df['Close'].ewm(span=short_window,adjust=False).mean()
    df['EMA_Long']=df['Close'].ewm(span=long_window,adjust=False).mean()
    df['MACD']=df['EMA_Short'] -df['EMA_Long']
    df['Signal_Line']=df['MACD'].ewm(span=signal_window,adjust=False).mean()
    df['MACD_Histogram']=df['MACD'] - df['Signal_Line']
    return df

#calculate Average True Range (ATR)

def calculate_atr(df,window=14):
    high_low=df['High']-df['Low']
    high_close=abs(df['High']-df['Close'].shift())
    low_close=abs(df['Low']-df['Close'].shift())
    ranges=pd.concat([high_low,high_close,low_close],axis=1)
    true_range=ranges.max(axis=1)
    df['ATR']=true_range.rolling(window=window).mean()
    return df

#calculate stochastic oscillator
#compares a stocks closing price to its price range over a specified period
def calculate_stochastic_oscillator(df,window=14,smooth_k=3,smooth_d=3):
    low_min=df['Low'].rolling(window=window).min()
    high_max=df['High'].rolling(window=window).max()
    df['%K']=((df['Close']-low_min)/(high_max-low_min))**100
    df['%D']=df['%K'].rolling(window=smooth_k).mean()
    df['%D_Slow']=df['%D'].rolling(window=smooth_d).mean()
    return df

#Identify support and resistance levels
def find_support_resistance(df,window=20):
    rolling_max=df['High'].rolling(window=window).max()
    rolling_min=df['Low'].rolling(window=window).min()
    support=rolling_min.iloc[-1]
    resistance=rolling_max.iloc[-1]
    return {"Support":support,'Resistance':resistance}

#calculate Sharpe Ratio
#it measures risk adjusted returns, helping investors evaluate the performance of a stock
def calculate_sharpe_ratio(df,risk_free_rate=0.02):
    daily_returns = df['Close'].pct_change().dropna()
    mean_return=daily_returns.mean()
    std_dev=daily_returns.std()
    sharpe_ratio=(mean_return-risk_free_rate)/std_dev
    annualized_sharpe=sharpe_ratio*(252**0.5)  #annualize the ratio
    return annualized_sharpe

#filter stocks by Technical Indicators(RSI,MACD)
def filter_by_rsi(df,rsi_column='RSI',lower_bound=30,upper_bound=70):
    return df[(df[rsi_column]>=lower_bound)&(df[rsi_column]<=upper_bound)]

def filter_by_macd(df,macd_column='MACD',signal_column='Signal_Line'):
    df['MACD_Crossover']=(df[macd_column]>df[signal_column]).astype(int)
    return df[df['MACD_Crossover'].diff()==1]  #only include crossover points

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

#calculate correlation between stocks
def calculate_stock_correlation(stock1_df,stock2_df):
    combined_df = pd.merge(stock1_df,stock2_df,on='Date',suffixes=('_stock1','_stock2_'))
    correlation=combined_df['Close_stock1'].corr(combined_df['Close_stock2'])
    return correlation

#identify candlestick patterns:
def detect_candlestick_patterns(df):
    df['Doji']=abs(df['Close']-df['Open'])/(df['High']-df['Low'])<0.1
    df['Hammer']=(df['Close']>df['Open'])&((df['High']-df['Close'])/(df['High']-df['Low'])<0.1)
    df['Engulfing']=(df['Close']>df['Open'].shift())&(df['Open']<df['Close'].shift())
    return df

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


