# -*- coding: utf-8 -*-

import pandas as pd
import common as cmn

def load_data():
    country_df = pd.read_csv(cmn.datapath/"CountryData.csv", parse_dates=['date']).set_index('date')
    
    state_df = pd.read_csv(cmn.datapath/"StateData.csv", parse_dates=['date']).set_index('date')
    
    county_df = pd.read_csv(cmn.datapath/"CountyData.csv", parse_dates=['date']).set_index('date')
    county_df.fips_str = county_df.fips_str.apply(lambda x: "%05d"%x)
    
    dates = country_df.index.unique().to_list()
    
    return country_df, state_df, county_df, dates

if __name__ == "__main__":
    # execute only if run as a script
    country_df, state_df, county_df, dates = load_data()

