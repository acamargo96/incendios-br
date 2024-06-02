import os
import pandas as pd
import numpy as np

def dataprep():
    
    df = pd.concat([pd.read_csv(f'data/{file}', compression = 'zip') for file in os.listdir('data')])
    
    df['lat'] = np.where(df['lat'].isna(), df['latitude'], df['lat'])
    df['lon'] = np.where(df['lon'].isna(), df['longitude'], df['lon'])
    
    df = df[(df['lat'].notna()) & (df['lon'].notna())].copy()
    df.drop(['latitude', 'longitude', 'foco_id', 'pais'], axis = 1, inplace = True)
    
    df['lat_r'] = df['lat'].round(1)
    df['lon_r'] = df['lon'].round(1)
    
    df['data_pas'] = pd.to_datetime(df['data_pas'])
    
    return df