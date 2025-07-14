import time
import pandas as pd
import numpy as np

def combine_series():
    """
    This function will combine data series that are in the same time frame and will remove any double time columns
    """
    pass

def make_daily(x):
    """
    This function will take all the data and will make it daily, will fill in missing data with the previous data point
    """
    if not isinstance(x.index, pd.DatetimeIndex):
        x.index = pd.to_datetime(x.index)

    X = x[~x.index.duplicated(keep='first')]
    final = X.resample('D').ffill()
    return final

def combine(*series):
    """
    This function will take time series dataframe and combine them into one dataframe 
    along trading days. 
    """
    smallest_df = min(series, key=len)
    trading_days = smallest_df.index

    combined_df = pd.DataFrame(index=trading_days)
    for s in series:
        combined_df = combined_df.join(s.reindex(trading_days).ffill(), how='outer')

    return combined_df

def find_returns(x):
    """
    This function will take a pandas series and will return the returns of that series
    """
    return x.pct_change()

def standardize(x):
    """
    This function will take a pandas series and will standardize it
    """
    return (x - x.mean()) / x.std()

def addstandardcolumns(df, columns):
    for col in columns:
        if col in df.columns:
            df[f'standardized_{col}'] = standardize(df[col])
        else:
            print(f"Column {col} not found in DataFrame.")