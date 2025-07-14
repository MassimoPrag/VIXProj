import yfinance as yf  # Import yfinance
import pandas as pd  # Import pandas
import numpy as np
from datetime import datetime
# Get vix prices in clean df

def get_vix(start, end, time = '1d'):
    """
    Takes start and end date for a certain observation and will retrun a pandas series of the VIX, will utilize the yfinance API

    Args:
        start (str) = start date in the format 'YYYY-MM-DD'
        end (str) = end date in the format 'YYYY-MM-DD'
        
    Returns:
        vix (series) = retruns a pandas series of the VIX, with time in datetime format as index and VIX as values
    """
    data = yf.download('^VIX', start=start, end=end, interval = time)
    data.reset_index(inplace=True)
    data = data[['Date', 'Close']]
    data.columns = ['Date', 'Close: VIX']
    data.set_index('Date', inplace=True)
    return data

def get_sp(start, end, time = '1d'):
    """
    Takes start and end date for a certain observation and will retrun a pandas series of the SPY, will utilize the yfinance API

    Args:
        start (str) = start date in the format 'YYYY-MM-DD'
        end (str) = end date in the format 'YYYY-MM-DD'
        
    Returns:
        spy (series) = retruns a pandas series of the SPY, with time in datetime format as index and SPY as values
    """
    data = yf.download('^GSPC', start=start, end=end, interval = time)
    data.reset_index(inplace=True)
    data = data[['Date', 'Close']]
    data.columns = ['Date', 'Close: S&P']
    data.set_index('Date', inplace=True)
    return data

def get_svix(start, end, time = '1d'):
    """
    Takes start and end date for a certain observation and will retrun a pandas series of the SPY, will utilize the yfinance API

    Args:
        start (str) = start date in the format 'YYYY-MM-DD'
        end (str) = end date in the format 'YYYY-MM-DD'
        
    Returns:
        spy (series) = retruns a pandas series of the SPY, with time in datetime format as index and SPY as values
    """
    start_date = datetime(2002,3,30)
    start = datetime.strptime(start, '%Y-%m-%d')

    if start < start_date:
        raise ValueError("Start date is before the first date of SVIX data")

    data = yf.download('SVIX', start=start, end=end, interval = time)
    data.reset_index(inplace=True)
    data = data[['Date', 'Close']]
    data.columns = ['Date', 'Close: SVIX']
    data.set_index('Date', inplace=True)
    return data

def get_vixy(start, end, time = '1d'):
    """
    Takes start and end date for a certain observation and will retrun a pandas series of the vxy, will utilize the yfinance API
    VXY is the pro shares short term (long vix ) ETF

    Args:
        start (str) = start date in the format 'YYYY-MM-DD'
        end (str) = end date in the format 'YYYY-MM-DD'
        
    Returns:
        spy (series) = retruns a pandas series of the SPY, with time in datetime format as index and SPY as values
    """
    start_date = datetime(2011,1,4)
    start = datetime.strptime(start, '%Y-%m-%d')

    if start < start_date:
        raise ValueError("Start date is before the first date of SVIX data")

    data = yf.download('VIXY', start=start, end=end, interval = time)
    data.reset_index(inplace=True)
    data = data[['Date', 'Close']]
    data.columns = ['Date', 'Close: VIXY']
    data.set_index('Date', inplace=True)
    return data


x = get_vixy('2011-01-04', '2025-02-28')

x.to_csv('data_1.csv')