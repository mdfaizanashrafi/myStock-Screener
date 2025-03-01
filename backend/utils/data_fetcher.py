import yfinance as yf
import pandas as pd
import os
import time

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

