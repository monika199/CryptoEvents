from __future__ import division

API_KEY="Q62XADJ7WXO7GHVC"

import requests
import json
import urllib
import pandas as pd
import time

from itertools import izip, count
import matplotlib.pyplot as plt
# import plotly.plotly as py
from numpy import linspace, loadtxt, ones, convolve
import numpy as np
import pandas as pd
import collections
from random import randint
from matplotlib import style
style.use('fivethirtyeight')


intraday_cache={}
def get_quotes_daily(currency_names,time_period=200):
	print 'daily in getquotes'
	prices={}
	retrieved=[]
	for i  in range(len(currency_names)):
		print currency_names[i]
		tries=5
		try:
			# import pdb; pdb.set_trace()
			result=requests.get("https://min-api.cryptocompare.com/data/histoday?fsym="+currency_names[i]+"&tsym=USD&limit="+str(time_period))
			# print "https://min-api.cryptocompare.com/data/histoday?fsym="+currency_names[i]+"&tsym=USD&limit="+str(time_period)
			result = result.json()['Data']
		    # print result
			ctr=time_period
			# price=[]
			prices[currency_names[i]] = []
			for k in result:
				if ctr<0:
					break
				#import pdb;pdb.set_trace()
				dic={ 'time': k['time'], 'open': float(k['open']), 'high': float(k['high']), 'low':float(k['low']), 'close':float(k['close']),'volumefrom':float(k['volumefrom']),'volumeto':float(k['volumeto'])}
				prices[currency_names[i]].append(dic)
				ctr-=ctr
			print 'fetched'
			retrieved.append(currency_names[i])
			
			# prices.append(price)
		except:
			if tries>0:
				i=i-1
				tries-=1
				continue
			else:
				continue 
	# import pdb; pdb.set_trace()
	# print prices
	return prices,retrieved




def get_quotes_intraday(currency_names):
	print 'intraday'
	prices={}
	retrieved=[]
	for i  in range(len(currency_names)):
		if currency_names[i] not in intraday_cache:
			print currency_names[i]
			tries=5
			try:
				result=requests.get("https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_INTRADAY&symbol="+currency_names[i]+"&market=EUR&apikey="+API_KEY+"&extraParams=cryptoevents")
			# import pdb;pdb.set_trace()
				result = result.json()['Time Series (Digital Currency Intraday)']
		    # print result
			
				prices[currency_names[i]] = []
				
				for k in result.keys():
					
					#import pdb;pdb.set_trace()
					dic={'time': k, 'price': float(result[k]['1b. price (USD)']), 'volume': float(result[k]['2. volume'])}
					prices[currency_names[i]].append(dic)
				print 'fetched'
				# prices.append(price)
				time.sleep(10)
				retrieved.append(currency_names[i])
				intraday_cache[currency_names[i]]=prices[currency_names[i]]
			except:
				if tries>0:
					i=i-1
					tries-=1
					continue
				else:
					continue
		else:
			prices[currency_names[i]] = intraday_cache[currency_names[i]]
	return prices,retrieved



def get_corr(currency_names=['BTC','XRP','ETC','DASH','LTC','XEM','ETH'], attr='open', mode='daily', days=200):
	if mode=='intra':
		prices,retrieved=get_quotes_intraday(currency_names)
		for x in currency_names:
			if x not in retrieved and x in intraday_cache:
				prices[x] = intraday_cache[x]
				retrieved.append(x)
		attr='price'
	else:
		prices,retrieved=get_quotes_daily(currency_names,days)
	# print prices
	attr_prices=[]
	for k in prices.keys():
		
		attr_p=[x[attr] for x in prices[k]]
		attr_prices.append(attr_p)
	
	df=pd.DataFrame()
	for i,ar in enumerate(attr_prices):
		#import pdb;pdb.set_trace()
		se = pd.Series(ar)
		# import pdb;pdb.set_trace()
		df[retrieved[i]] = se
	# print df.corr()
	
	return df
	


def moving_average(data, window_size):
	window = np.ones(int(window_size))/float(window_size)
	return np.convolve(data, window, 'same')
def explain_anomalies(y, window_size, sigma=1.0):
	avg = moving_average(y, window_size).tolist()
	residual = y - avg
    # Calculate the variation in the distribution of the residual
	std = np.std(residual)
	return {'standard_deviation': round(std, 3),'anomalies_dict': collections.OrderedDict([(index, y_i) for index, y_i, avg_i in izip(count(), y, avg) if (y_i > avg_i + (sigma*std)) | (y_i < avg_i - (sigma*std))])}

def explain_anomalies_rolling_std(y, window_size, sigma=1.0):
	avg = moving_average(y, window_size)
	avg_list = avg.tolist()
	residual = y - avg
	# Calculate the variation in the distribution of the residual
	testing_std = pd.rolling_std(residual, window_size)
	testing_std_as_df = pd.DataFrame(testing_std)
	rolling_std = testing_std_as_df.replace(np.nan,
	                              testing_std_as_df.ix[window_size - 1]).round(3).iloc[:,0].tolist()
	std = np.std(residual)
	return {'stationary standard_deviation': round(std, 3),
	        'anomalies_dict': collections.OrderedDict([(index, y_i)
	                                                   for index, y_i, avg_i, rs_i in izip(count(),
	                                                                                       y, avg_list, rolling_std)
          if (y_i > avg_i + (sigma * rs_i)) | (y_i < avg_i - (sigma * rs_i))])}

def plot_results(x, y, window_size, sigma_value=1,
                 text_xlabel="X Axis", text_ylabel="Y Axis", applying_rolling_std=False):
	# plt.figure(figsize=(15, 8))
	# plt.plot(x, y, "k.")
	y_av = moving_average(y, window_size)
	# plt.plot(x, y_av, color='green')
	#     plt.xlim(0, 1000)
	# plt.xlabel(text_xlabel)
	# plt.ylabel(text_ylabel)

	# Query for the anomalies and plot the same
	events = {}
	if applying_rolling_std:
	    events = explain_anomalies_rolling_std(y, window_size=window_size, sigma=sigma_value)
	else:
	    events = explain_anomalies(y, window_size=window_size, sigma=sigma_value)

	x_anomaly = np.fromiter(events['anomalies_dict'].iterkeys(), dtype=int, count=len(events['anomalies_dict']))
	y_anomaly = np.fromiter(events['anomalies_dict'].itervalues(), dtype=float,
	                                        count=len(events['anomalies_dict']))
	return x, y, y_av, x_anomaly, y_anomaly
	# print x_anomaly, y_anomaly
	#     plt.plot(x_anomaly, y_anomaly, "r*", markersize=12)

	#     add grid and lines and enable the plot
	# plt.grid(True)
	# plt.show()
	# get_corr(['BTC','ETH','ETC','DASH','XEM','LTC'])
# res = get_corr(['BTC','ETH','DASH'])
# res.to_json()
