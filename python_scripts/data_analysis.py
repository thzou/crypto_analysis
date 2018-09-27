#Author : Zoumpekas Athanasios
#codename : thzou 


import os
import numpy as np
import pandas as pd
import pickle
import quandl
import datetime
import statsmodels.api as sm
from scipy import stats
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



def correlation_analysis(combined_df):
	# split dataset to 4 datasets by year (2015,2016,2017,2018)
	combined_df2018 = combined_df[combined_df.index.year == 2018]
	combined_df2017 = combined_df[combined_df.index.year == 2017]
	combined_df2016 = combined_df[combined_df.index.year == 2016]
	combined_df2015 = combined_df[combined_df.index.year == 2015]

	plt.style.use('fivethirtyeight')
	plt.style.use('seaborn-notebook')

	f,ax = plt.subplots(2, 2,figsize=(18, 12))

	sns.heatmap(combined_df2015.pct_change().corr(), annot=False, linewidths=.5, fmt= '.2f',ax=ax[0,0],cmap="YlGnBu")

	sns.heatmap(combined_df2016.pct_change().corr(), annot=False, linewidths=.5, fmt= '.2f',ax=ax[0,1],cmap="YlGnBu")

	sns.heatmap(combined_df2017.pct_change().corr(), annot=False, linewidths=.5, fmt= '.2f',ax=ax[1,0],cmap="YlGnBu")

	sns.heatmap(combined_df2018.pct_change().corr(), annot=False, linewidths=.5, fmt= '.2f',ax=ax[1,1],cmap="YlGnBu")

	ax[0,0].set_title('2015')
	ax[0,1].set_title('2016')
	ax[1,0].set_title('2017')
	ax[1,1].set_title('2018')

	#plt.show()
	plt.savefig('images/Correlation_heatmaps.png')

def distribution_analysis(combined_df):

	combined_df2018 = combined_df[combined_df.index.year == 2018]
	combined_df2017 = combined_df[combined_df.index.year == 2017]
	combined_df2016 = combined_df[combined_df.index.year == 2016]
	combined_df2015 = combined_df[combined_df.index.year == 2015]

	###BOXPLOTS###

	##ZRX##
	fig, axs = plt.subplots(nrows=2,figsize=(12, 8))
	sns.boxplot(data=combined_df2017['ZRX'], ax=axs[0],orient="h").set_title('ZRX 2017')
	sns.boxplot(data=combined_df2018['ZRX'], ax=axs[1],orient="h").set_title('ZRX 2018')
	fig.tight_layout()
	#plt.show()
	plt.savefig('images/ZRX_boxplots.png')

	##BCN##
	fig, axs = plt.subplots(nrows=2,figsize=(12, 8))
	sns.boxplot(data=combined_df2017['BCN'], ax=axs[0],orient="h").set_title('BCN 2017')
	sns.boxplot(data=combined_df2018['BCN'], ax=axs[1],orient="h").set_title('BCN 2018')
	fig.tight_layout()
	#plt.show()
	plt.savefig('images/BCN_boxplots.png')


	###HISTOGRAMS###

	##ZRX##
	fig, axs = plt.subplots(nrows=2,figsize=(12, 8))

	combined_df2017['ZRX'].hist(bins=30,ax=axs[0], figsize=(12,8)).axvline(combined_df2017['ZRX'].median(), color='b', linestyle='dashed', linewidth=2)
	axs[0].set_title('ZRX 2017')

	combined_df2018['ZRX'].hist(bins=30,ax=axs[1], figsize=(12,8)).axvline(combined_df2018['ZRX'].median(), color='b', linestyle='dashed', linewidth=2)
	axs[1].set_title('ZRX 2018')

	fig.tight_layout()
	#plt.show()
	plt.savefig('images/ZRX_hist.png')

	##BCN##
	fig, axs = plt.subplots(nrows=2,figsize=(12, 8))

	combined_df2017['BCN'].hist(bins=30,ax=axs[0], figsize=(12,8)).axvline(combined_df2017['BCN'].median(), color='b', linestyle='dashed', linewidth=2)
	axs[0].set_title('BCN 2017')

	combined_df2018['BCN'].hist(bins=30,ax=axs[1], figsize=(12,8)).axvline(combined_df2018['BCN'].median(), color='b', linestyle='dashed', linewidth=2)
	axs[1].set_title('BCN 2018')

	fig.tight_layout()
	#plt.show()
	plt.savefig('images/BCN_hist.png')




def trading_strategies(combined_df):

	combined_df2018 = combined_df[combined_df.index.year == 2018]
	combined_df2017 = combined_df[combined_df.index.year == 2017]
	combined_df2016 = combined_df[combined_df.index.year == 2016]
	combined_df2015 = combined_df[combined_df.index.year == 2015]

	combined = combined_df2017.append(combined_df2018)
	combined = combined.dropna()

	df_return = combined.apply(lambda x: x / x[0])
	df_return = df_return.dropna()

	df_return.plot(grid=True, figsize=(15, 10)).axhline(y = 1, color = "black", lw = 2)
	#plt.show()
	plt.savefig('images/return.png')


	return_trace1 = go.Scatter(x=df_return.index, 
	                           y=df_return['ZRX'],
	                           name = "ZRX Return",
	                           line = dict(color = 'green'),
	                           opacity = 0.8)
	return_trace2 = go.Scatter(x=df_return.index, 
	                           y=df_return['BCN'],
	                           name = "BCN Return",
	                           line = dict(color = 'red'),
	                           opacity = 0.8)

	data = [return_trace1,return_trace2]

	layout = dict(
	    title='Returns (Buy & Hold Strategy)',
	    xaxis=dict(
	        rangeselector=dict(
	            buttons=list([
	                dict(count=1,
	                     label='1m',
	                     step='month',
	                     stepmode='backward'),
	                dict(count=6,
	                     label='6m',
	                     step='month',
	                     stepmode='backward'),
	                dict(step='all')
	            ])
	        ),
	        rangeslider=dict(),
	        type='date'
	    )
	)

	fig = dict(data=data, layout=layout)
	py.plot(fig, filename = "images/buyandhold_returns.html", auto_open=False)
	pio.write_image(fig, 'images/buyandhold_returns.png')

	df_perc = df_return.tail(1) * 100
	ax = sns.barplot(data=df_perc)

	for item in ax.get_xticklabels():
	    item.set_rotation(45)

	ax.set_title('Percentage Increase')
	#plt.show()
	plt.savefig('images/Percentage_increase.png')

	budget = 1000 # USD
	df_coins = budget/combined.head(1)

	ax = sns.barplot(data=df_coins)

	for item in ax.get_xticklabels():
	    item.set_rotation(45)

	ax.set_title('Number of Coins (Investment : $1000)')
	plt.savefig('images/number_of_coins.png')
	#plt.show()


	df_profit = df_return.tail(1) * budget

	ax = sns.barplot(data=df_profit)

	for item in ax.get_xticklabels():
	    item.set_rotation(45)

	ax.set_title('Return a year later')
	#plt.show()
	plt.savefig('images/return_a_year_later.png')

