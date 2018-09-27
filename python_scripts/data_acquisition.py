#Author : Zoumpekas Athanasios
#codename : thzou 

import os
import numpy as np
import pandas as pd
import pickle
import quandl
import datetime
import time
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import sys
import io
from itertools import product
import warnings
from plotly import tools
import plotly.offline as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
import plotly.io as pio



def get_quandl_data(quandl_id):
    '''Download and cache Quandl dataseries'''
    cache_path = 'data/' + '{}.pkl'.format(quandl_id).replace('/','-')
    try:
        f = open(cache_path, 'rb')
        df = pickle.load(f)   
        print('Loaded {} from cache'.format(quandl_id))
    except (OSError, IOError) as e:
        print('Downloading {} from Quandl'.format(quandl_id))
        df = quandl.get(quandl_id, returns="pandas")
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(quandl_id, cache_path))
    return df


def merge_dfs_on_column(dataframes, labels, col):
    '''Merge a single column of each dataframe into a new combined dataframe'''
    series_dict = {}
    for index in range(len(dataframes)):
        series_dict[labels[index]] = dataframes[index][col]
        
    return pd.DataFrame(series_dict)


def get_json_data(json_url, cache_path):
    '''Download and cache JSON data, return as a dataframe.'''
    try:        
        f = open(cache_path, 'rb')
        df = pickle.load(f)   
        print('Loaded {} from cache'.format(json_url))
    except (OSError, IOError) as e:
        print('Downloading {}'.format(json_url))
        df = pd.read_json(json_url)
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(json_url, cache_path))
    return df


def get_poloniex_data(poloniex_pair):

	base_polo_url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'
	start_date = datetime.datetime.strptime('2014-01-01', '%Y-%m-%d') # get data from the start of 2014
	end_date = datetime.datetime.now() # up until today
	pediod = 86400 # pull daily data (86,400 seconds per day)
	#Retrieve cryptocurrency data from poloniex#
	json_url = base_polo_url.format(poloniex_pair, start_date.timestamp(), end_date.timestamp(), pediod)
	data_df = get_json_data(json_url, 'data/'+poloniex_pair)
	data_df = data_df.set_index('date')
	return data_df

def df_scatter(df, title, seperate_y_axis=False, y_axis_label='', scale='linear', initial_hide=False):
    #Generate a scatter plot of the entire dataframe#
    label_arr = list(df)
    series_arr = list(map(lambda col: df[col], label_arr))
    
    layout = go.Layout(
        title=title,
        legend=dict(orientation="h"),
        xaxis=dict(type='date'),
        yaxis=dict(
            title=y_axis_label,
            showticklabels= not seperate_y_axis,
            type=scale
        )
    )
    
    y_axis_config = dict(
        overlaying='y',
        showticklabels=False,
        type=scale )
    
    visibility = True
    if initial_hide:
        visibility = 'legendonly'
        
    # Form Trace For Each Series
    trace_arr = []
    for index, series in enumerate(series_arr):
        trace = go.Scatter(
            x=series.index, 
            y=series, 
            name=label_arr[index],
            visible=visibility
        )
        
        # Add seperate axis for the series
        if seperate_y_axis:
            trace['yaxis'] = 'y{}'.format(index + 1)
            layout['yaxis{}'.format(index + 1)] = y_axis_config    
        trace_arr.append(trace)

    fig = go.Figure(data=trace_arr, layout=layout)
    py.plot(fig, filename = 'images/cryptos.html', auto_open=False)
    pio.write_image(fig, 'images/cryptos.png')
    #py.iplot(fig)



def btc_average_data():

	# Pull Kraken BTC price exchange data
	btc_usd_price_kraken = get_quandl_data('BCHARTS/KRAKENUSD')
	# Pull pricing data for 3 more BTC exchanges
	exchanges = ['COINBASE','BITSTAMP','ITBIT']

	exchange_data = {}

	exchange_data['KRAKEN'] = btc_usd_price_kraken

	for exchange in exchanges:
	    exchange_code = 'BCHARTS/{}USD'.format(exchange)
	    btc_exchange_df = get_quandl_data(exchange_code)
	    exchange_data[exchange] = btc_exchange_df

	# Merge the BTC price dataseries' into a single dataframe
	btc_usd_datasets = merge_dfs_on_column(list(exchange_data.values()), list(exchange_data.keys()), 'Weighted Price')
	#btc_usd_datasets_close = merge_dfs_on_column(list(exchange_data.values()), list(exchange_data.keys()), 'Close')
	btc_usd_datasets.replace(0, np.nan, inplace=True)
	# Calculate the average BTC price as a new column
	btc_usd_datasets['avg_btc_price_usd'] = btc_usd_datasets.mean(axis=1)
	#btc_usd_datasets_close['close'] = btc_usd_datasets_close.mean(axis=1)

	return btc_usd_datasets



def get_altcoins_data():

	altcoins = ['XRP','ETH','XMR','STR','LTC','DGB','BTS','DOGE','BCH','BCN','ZRX','DASH','ZEC','MAID','ETC']

	altcoin_data = {}
	for altcoin in altcoins:
	    coinpair = 'BTC_{}'.format(altcoin)
	    crypto_price_df = get_poloniex_data(coinpair)
	    altcoin_data[altcoin] = crypto_price_df

	return altcoin_data


def convert_and_combine(altcoin_data,btc_usd_datasets):

	# Calculate USD Price as a new column in each altcoin dataframe
	for altcoin in altcoin_data.keys():
		altcoin_data[altcoin]['price_usd'] =  altcoin_data[altcoin]['weightedAverage'] * btc_usd_datasets['avg_btc_price_usd']
	
	combined_df = merge_dfs_on_column(list(altcoin_data.values()), list(altcoin_data.keys()), 'price_usd')
	# Add BTC price to the dataframe
	combined_df['BTC'] = btc_usd_datasets['avg_btc_price_usd']

	df_scatter(combined_df, 'Cryptocurrency Prices (USD)', seperate_y_axis=False, y_axis_label='Coin Value (USD)', scale='log')
	return combined_df