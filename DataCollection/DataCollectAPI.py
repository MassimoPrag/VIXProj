#use the to time function to convert the date to a datetime object
import sys
import os

# Add the parent directory of DataCollection to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from datetime import datetime
from DataCollection.collectFRED_API import get_quantity_of_money, get_Fred
from DataCollection.collect_yfinance_API import get_vix, get_sp, get_svix, get_vixy



def get_data(start, end, *functions):
    """
    Fetches data for the specified functions and combines them into a single DataFrame.
    Dynamically determines the valid date range across all data sources.
    """
    data_frames = {}
    all_dates = set()

    for arg in functions:
        try:
            if arg == 'VIX':
                vix_data = get_vix(start, end)
                vix_data.index = pd.to_datetime(vix_data.index)
                data_frames['VIX'] = vix_data['Close: VIX']
                all_dates.update(vix_data.index)
            elif arg == 'SP':
                sp_data = get_sp(start, end)
                sp_data.index = pd.to_datetime(sp_data.index)
                data_frames['SP'] = sp_data['Close: S&P']
                all_dates.update(sp_data.index)
            elif arg == 'VIXY':
                vixy_data = get_vixy(start, end)
                vixy_data.index = pd.to_datetime(vixy_data.index)
                data_frames['VIXY'] = vixy_data['Close: VIXY']
                all_dates.update(vixy_data.index)
            elif arg == 'P':
                p_data = get_quantity_of_money(start, end)
                p_data.index = pd.to_datetime(p_data.index)
                data_frames['P'] = p_data
                all_dates.update(p_data.index)
            elif arg == 'M2':
                m2_data = get_Fred(series_id='WM2NS', key="0c4f873ed6a493bf5bbfd87280eda6de", startDate=start, endDate=end)
                m2_data.index = pd.to_datetime(m2_data.index)
                data_frames['M2'] = m2_data['value']
                all_dates.update(m2_data.index)
            elif arg == 'FEDFUNDS':
                fed_funds_data = get_Fred(series_id='FEDFUNDS', key="0c4f873ed6a493bf5bbfd87280eda6de", startDate=start, endDate=end)
                fed_funds_data.index = pd.to_datetime(fed_funds_data.index)
                data_frames['FEDFUNDS'] = fed_funds_data['value']
                all_dates.update(fed_funds_data.index)
            elif arg == 'RealGDP':
                real_gdp_data = get_Fred(series_id='GDPC1', key="0c4f873ed6a493bf5bbfd87280eda6de", startDate=start, endDate=end)
                real_gdp_data.index = pd.to_datetime(real_gdp_data.index)
                data_frames['RealGDP'] = real_gdp_data['value']
                all_dates.update(real_gdp_data.index)
            elif arg == 'GDP':
                gdp_data = get_Fred(series_id='GDP', key="0c4f873ed6a493bf5bbfd87280eda6de", startDate=start, endDate=end)
                gdp_data.index = pd.to_datetime(gdp_data.index)
                data_frames['GDP'] = gdp_data['value']
                all_dates.update(gdp_data.index)
            elif arg == 'CPI':
                cpi_data = get_Fred(series_id='CPIAUCSL', key="0c4f873ed6a493bf5bbfd87280eda6de", startDate=start, endDate=end)
                cpi_data.index = pd.to_datetime(cpi_data.index)
                data_frames['CPI'] = cpi_data['value']
                all_dates.update(cpi_data.index)
            elif arg == 'UNEMPLOYlevel':
                unemploy_data = get_Fred(series_id='UNEMPLOY', key="0c4f873ed6a493bf5bbfd87280eda6de", startDate=start, endDate=end)
                unemploy_data.index = pd.to_datetime(unemploy_data.index)
                data_frames['UNEMPLOYlevel'] = unemploy_data['value']
                all_dates.update(unemploy_data.index)
            else:
                raise ValueError(f"Unknown data series: {arg}")
        except Exception as e:
            print(f"Warning: Skipping {arg} due to error: {e}")

    # Determine the valid date range
    all_dates = sorted(all_dates)
    combined_df = pd.DataFrame(index=all_dates)

    # Combine all data frames
    for name, df in data_frames.items():
        if isinstance(df, pd.DataFrame):
            df = df.iloc[:, 0]
        combined_df[name] = df.reindex(combined_df.index).ffill()

    return combined_df

x = get_data('2000-01-01', '2024-09-20', 'CPI', 'P', 'VIX', 'SP', 'M2', 'FEDFUNDS', 'RealGDP', 'GDP', 'UNEMPLOYlevel')
print(x)