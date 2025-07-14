import pandas as pd
import requests
import json
import time
import pandas_datareader as pdr
import datetime
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helpingfunctions as dca

def get_Fred(series_id, key, startDate, endDate):
    """
    Takes series id, key, start and end date for a certain observation from FRED and returns that data in JSON format
    
    Args:
        series_id (str): id of the observation that we want, either "M2", "GDP", 'FEDFUNDS'
        key (str): my FRED API key
        startDate (str) = start date in the format 'YYYY-MM-DD'
        endDate (str) = end date in the format 'YYYY-MM-DD'
        
    Returns:
        infos (json) = returns infos in json format
    
    """
    url = f'https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={key}&file_type=json&observation_start={startDate}&observation_end={endDate}'
    infos = requests.get(url)
    obs =  infos.json()
    observations = obs["observations"]
    df = pd.DataFrame(observations)[["date", "value"]]
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df["value"] = pd.to_numeric(df["value"])
    # Q. How do i multiply my values by a billion using numpy
    if series_id == "GDP" or series_id == "WM2NS" or series_id == "GDPC1":
        df["value"] = df["value"] * 1000000000
    elif series_id == "FEDFUNDS":
        df["value"] = df["value"] / 100
    elif series_id == 'UNEMPLOY':
        df['value'] = df['value'] * 1000
    else:
        pass
    df = dca.make_daily(df)
    return df

def get_quantity_of_money(start, end):
    # YYYY-MM-DD
    #Friedman Quantity of Money per unit of out put, MV = PY
    #P = MV / Y, inflation is the result of money supply growing faster than output, belive that devience or variance in P will resuly in VIX spikes or periods of higher return for the VIX

    M2Data = get_Fred(series_id = 'WM2NS', key = "0c4f873ed6a493bf5bbfd87280eda6de", startDate = start, endDate= end)
    # weekly and times one billion

    RealGDPData = get_Fred(series_id = 'GDPC1', key = "0c4f873ed6a493bf5bbfd87280eda6de", startDate = start, endDate= end)
    # quarterly, and times one billion

    velocityM2 = get_Fred(series_id = 'M2V', key = "0c4f873ed6a493bf5bbfd87280eda6de", startDate = start, endDate= end)


    m2Daily = dca.make_daily(M2Data)
    RealGDPDaily = dca.make_daily(RealGDPData)
    velocityM2Daily = dca.make_daily(velocityM2)

    combined = pd.concat([m2Daily, RealGDPDaily, velocityM2Daily], axis=1, join='inner')
    combined.columns = ['M2', 'GDP', 'Velocity']



    combined['P'] = (combined['M2'] * combined['Velocity']) / combined['GDP']

    x = combined["P"]
    x.columns = ['P']
    return x
   

#P = m2Daily["value"] * velocityM2Daily["value"] / RealGDPDaily["value"]

  

CPIData = get_Fred(series_id = 'CPIAUCSL', key = "0c4f873ed6a493bf5bbfd87280eda6de", startDate = "2000-01-01", endDate= "2023-09-01")
# monthly CPI all items
print(CPIData)
#GDPData = get_Fred(series_id = 'GDP', key = "0c4f873ed6a493bf5bbfd87280eda6de", startDate = "2000-02-20", endDate= "2023-09-01")

#fFundsData = get_Fred(series_id = 'FEDFUNDS', key = "0c4f873ed6a493bf5bbfd87280eda6de", startDate = "2000-01-20", endDate= "2023-09-01")
# monthly percentage

#M2Data = get_Fred(series_id = 'WM2NS', key = "0c4f873ed6a493bf5bbfd87280eda6de", startDate = "2000-01-01", endDate= "2024-01-30")
# weekly and times one billion

#RealGDPData = get_Fred(series_id = 'GDPC1', key = "0c4f873ed6a493bf5bbfd87280eda6de", startDate = "2000-01-01", endDate= "2024-01-30")
# quarterly, and times one billion

#velocityM2 = get_Fred(series_id = 'M2V', key = "0c4f873ed6a493bf5bbfd87280eda6de", startDate = "2000-01-01", endDate= "2024-01-30")


# series id for unemployment: UNEMPLOY , thousands of people, monthly

#print(get_quantity_of_money("2000-01-01", "2024-01-30"))


#CPIData.to_csv("DataCollection/cpi.csv")

#combined.to_csv("DataCollection/combined.csv")
