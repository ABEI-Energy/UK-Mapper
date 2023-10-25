import pandas as pd
import streamlit as st

st.cache_data
def filter_df(df, selected_periods, selected_ISOs, selected_states, selected_priceTypes):

    selected_periods_set = set(selected_periods)
    selected_ISOs_set = set(selected_ISOs)
    selected_states_set = set(selected_states)
    selected_priceTypes_set = set(selected_priceTypes)

    # Filter the DataFrame based on selected values
    filtered_df = df[
        df['Period From'].isin(selected_periods_set) &
        df['ISO'].isin(selected_ISOs_set) &
        df['State'].isin(selected_states_set) &
        df['Price type'].isin(selected_priceTypes_set)
    ].reset_index(drop = True)

    df_indexed = filtered_df.copy()

    df_indexed = df_indexed.sort_values(by=['Average Max Daily LMP', 'Average Min Daily LMP'],
     ascending=[True, False]).reset_index(drop = True)
    
    df_indexed['Heat map scale'] = df_indexed.groupby('State').cumcount() + 1

    df_indexed['Heat map scale'] = df_indexed.groupby('State')['Heat map scale'].transform(lambda x: (x - 1) / (len(x) - 1))

    
    df_indexed.loc[df_indexed['Heat map scale'].isnull(), 'Heat map scale'] = 1 

    return filtered_df, df_indexed




st.cache_data
def df_adequacy(uploadedFile):
    
    df = pd.read_csv(uploadedFile)

    # We filter the df by years first.
    df = df.loc[((df['dateRange']=='Past 1 Year') | (df['dateRange']=='Past 3 Years') | (df['dateRange']=='Past 5 Years'))]

    df.rename(columns = {'y':'Latitude', 'x':'Longitude', 'nodeName':'Node', 'iso':'ISO', 'lmpAverage': 'Average LMP', 'mindaylmp': 'Average Min Daily LMP', 'avgmaxlmp': 'Average Max Daily LMP', 'lmpspread': 'Average Max - Min Daily LMP Spread', 'lmpAveragePeak': 'Average LMP peak', 'lmpMax': 'LMP Max', 'lmpAverageOffPeak': 'Average LMP offpeak', 'lmpMin': 'LMP Min', 'lmpTotalNegativeValues': 'LMP negative hours', 'lmpWeightedSolar': 'LMP Solar', 'lmpWeightedWind': 'LMP Wind', 'nodeZoneDifferential': 'Node zone differential', 'averageDayAheadRealtimeSpread': 'Average day real time spread', 'averageTopBottom4SpreadDailyLMP': 'Average LMP top-bottom daily spread', 'mclAverage': 'Average line loss', 'mclMax': 'Max line loss', 'mclMin': 'Min line loss', 'mccAverage': 'MCC Average', 'storageArbitragePotential': 'Storage arbitrage potential', 'priceType': 'Price type', 'dateRange': 'Period From', 'ENVNodeID' : 'Node ID', 'state': 'State', 'county' : 'County'}, inplace = True)

    df = df.loc[~df['Latitude'].isnull() | ~df['Longitude'].isnull()]

    df.drop(columns = ['hub', 'zone', 'nodeType'], inplace = True)

    df[['Latitude', 'Longitude']] = df[['Latitude', 'Longitude']].astype(float)

    df = df[['Node', 'State', 'County', 'ISO', 'Period From', 'Latitude', 'Longitude', 'Average LMP', 'Average Min Daily LMP', 'Average Max Daily LMP', 'Average Max - Min Daily LMP Spread', 'LMP negative hours', 'Price type']]

    df_stateless = df.loc[df['State'].isnull()].reset_index(drop = True)
    df_statefull = df.loc[~df['State'].isnull()].reset_index(drop = True) 

    df_stateless_or_countiless = df.loc[df['State'].isnull() |df['County'].isnull()]
    df_full = df.iloc[~df.index.isin(df_stateless_or_countiless.index)]


    return df_stateless, df_statefull, df_stateless_or_countiless, df_full
