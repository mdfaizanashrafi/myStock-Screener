import pandas as pd
from sqlalchemy.ext.mypy.util import set_mapped_attributes


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

#filter by date range
def filter_by_date_range(df,date_column,start_date,end_date):
    #convert start date and end date to datetime
    start_date=pd.to_datetime(start_date)
    end_date=pd.to_datetime(end_date)

    #filter the DataFrame
    filtered_df = df[(df[date_column]>=start_date)&(df[date_column]<=end_date)]
    return filtered_df

#calculate SMA(simple moving average)
def calculate_sma(df,window):
    if 'Close' not in df.columns:
        raise ValueError("DataFrame must contain a 'close' column for SMA calculation.")

    #calculate the rolling mean (SMA) using the window size
    sma = df['Close'].rolling(window=window).mean()
    return sma

#calculte RSI
def calculate_rsi(df,window):
    delta = df['CLose'].diff()  # calculates between concsec closing price
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()  # keeps positive value and replaces negative to 0
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()  # keeps megative value and converts into positive, and converts positive to 0
    rs = gain / loss.replace(0, 1e-10)  # relative stength, replace 0 with a very small number
    df['RSI'] = 100 - (100 / (1 + rs))

#calculate boolinger bands
def calculate_boolinger_bands(df,window,k):
    rolling_mean = df['CLose'].rolling(window=window).mean()
    rolling_std = df['Close'].rolling(window=window).std()
    df['BB_Upper'] = rolling_mean + (k * rolling_std)
    df['BB_Lower'] = rolling_mean - (k * rolling_std)
    return df[['Date','Close','BB_Upper','BB_Lower']]


