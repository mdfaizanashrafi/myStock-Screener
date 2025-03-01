from backend.utils.data_fetcher import get_resampled_data, fetch_financial_statements
from utils.data_fetcher import fetch_stock_data_with_cache,fetch_stock_data

if __name__ == '__main__':
    try:
        stock_data = fetch_stock_data_with_cache('AAPL',period='1mo',interval='1d')
        print("Original Data:")
        #fetch 1 month of daily data of Apple
        print(stock_data.head())

        #resample to weekly
        weekly_data = get_resampled_data(stock_data,interval='W')
        print("\n Weekly Resampled Data:")
        print(weekly_data.head())

        #resample to monthly data
        monthly_data = get_resampled_data(stock_data,interval='M')
        print("\n Monthly Resampled Data: ")
        print(monthly_data.head())

    except Exception as e:
        print(f"Error: {e}")

df = fetch_stock_data("RELIANCE.NS",period="1y",interval="1d")
print(df.head())

financials=fetch_financial_statements("RELIANCE.NS")
print(financials["balance_sheet"])


