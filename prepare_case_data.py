# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

import common as cmn

def get_case_data(start_date=None):

    def compute_stats(df):
        df['new_cases'] = df['cases'] - df['cases'].shift(1, fill_value=0)
        df['new_deaths'] = df['deaths'] - df['deaths'].shift(1, fill_value=0)
        df['cases_per_100k'] = 1e5 * df['cases']/df.population
        df['deaths_per_100k'] = 1e5 * df['deaths']/df.population
        
    
    #nyt_file = cmn.datapath/'NYTimes_us-counties.csv'
    cases_file = cmn.datapath/'covid_confirmed_usafacts.csv'
    deaths_file = cmn.datapath/'covid_deaths_usafacts.csv'
    county_pop_file = cmn.datapath/'covid_county_population_usafacts.csv'
    
    # get raw county case and population data, plus state abbreviations
    #df = pd.read_csv(nyt_file)
    #df.date = pd.to_datetime(df.date)
    
    cases_df = pd.read_csv(cases_file)
    cases_df = cases_df.melt(id_vars=['countyFIPS', 'County Name', 'State', 'stateFIPS'], 
                             var_name="date", 
                             value_name="cases").set_index(['stateFIPS', 'countyFIPS', 'date'])
    
    deaths_df = pd.read_csv(deaths_file)
    deaths_df = deaths_df.melt(id_vars=['countyFIPS', 'County Name', 'State', 'stateFIPS'], 
                               var_name="date", 
                               value_name="deaths").set_index(['stateFIPS', 'countyFIPS', 'date'])
    df = cases_df.join(deaths_df[['deaths']]).reset_index()
    
    # merge county populations into case data
    pop_df = pd.read_csv(county_pop_file).drop_duplicates(subset='countyFIPS')
    df = df.merge(pop_df[['countyFIPS', 'population']], on='countyFIPS')
    # keep records with a county identifier
    df = df[df.countyFIPS > 0]
    df['fips_str'] = df.countyFIPS.apply(lambda x: "%05d"%x)
    # keep records at or after start date
    df.date = pd.to_datetime(df.date)
    if start_date is not None:
        df = df[df.date >= start_date]

    # build state-level aggregates
    state_pop_df = pop_df.groupby('State').agg({'population': 'sum'})
    state_df = df.groupby(['State', 'date']).agg({'cases': 'sum', 'deaths': 'sum'}).reset_index()
    state_df = state_df.merge(state_pop_df, on='State')
    
    # build country-level aggregates
    country_df = state_df.groupby(['date']).agg({'cases': 'sum', 'deaths': 'sum'})
    country_df['population'] = state_pop_df.population.sum()
    
    # add computed features
    compute_stats(country_df)
    compute_stats(state_df)
    compute_stats(df)

    return country_df, state_df.set_index('date'), df.set_index('date')

if __name__ == "__main__":
    # execute only if run as a script
    country_df, state_df, county_df = get_case_data()