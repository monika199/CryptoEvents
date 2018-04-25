from flask import Flask
from flask import render_template
from flask import request
from getquotes import *
import pandas as pd
import os
app = Flask(__name__)
@app.route("/")
def hello():
	return render_template("index.html")
@app.route("/home")
def home():
	return render_template("index.html")
@app.route("/trends")
def trends():
	return render_template("graphs.html")

@app.route("/corr", methods=['POST'])
def call_quotes():
	# print "CALLED CORR"
	cur = request.json['cur[]']
	time = request.json['time_range[]']
	print time,cur
	if time[0] == "daily":
		df = get_corr(currency_names=cur, mode="daily")
	else:
		df = get_corr(currency_names=cur, mode="intra")
	
	
	z = df.corr().as_matrix().tolist()
	x = df.columns.tolist()
	y = df.columns.tolist()
	data = {'z':z,'y':y,'x':x,'type':'heatmap'}
	# corr = json.loads(corr)
	# for i in corr.keys():
	# 	for j in corr[i]:
	# 		t = [i, j, corr[i][j]]
	# 		data.append(t)
	# print data
	# print corr
	print data
	return json.dumps(data)

@app.route("/basic", methods=['POST'])
def get_quotes():
	# print "CALLED APP"
	cur = request.json['cur[]']
	time = request.json['time_range[]']
	print time, cur
	traces = []
	if time[0] == "daily":
		prices,_ = get_quotes_daily(currency_names=cur)
		# print prices
		# low = []
		high = []
		dates = []
		for k in prices.keys():
			# low=[x['low'] for x in price]
			high=[x['high'] for x in prices[k]]
			dates=[x['time'] for x in prices[k]]
			#############
			x = pd.Series(dates)
			Y = pd.Series(high)
			x, y, y_av, x_anomaly, y_anomaly = plot_results(x, y=Y, window_size=10, text_xlabel="Time", sigma_value=2,
             text_ylabel="Quotes")
			events = explain_anomalies(Y, window_size=10, sigma=2)
			print("Information about the anomalies model:{}".format(events))
			#############
			trace = {'type':"line", 'mode':"lines", 'name':k, 'x':dates,'y':high}
			traces.append(trace)
		# trace2 = {'type':"scatter", 'mode':"lines", 'name':'LOW', 'x':dates,'y':low, 'line':{'color': '#7F7F7F'}}
		# data = [trace1, trace2]
	else:
		prices,_ = get_quotes_intraday(currency_names=cur)
		for k in prices.keys():
			quotes=[x['price'] for x in prices[k]]
			dates=[x['time'].split(" ")[1]+x['time'].split(" ")[0] for x in prices[k]]
			###################
			x = pd.Series(dates)
			Y = pd.Series(quotes)
			x, y, y_av, x_anomaly, y_anomaly = plot_results(x, y=Y, window_size=10, text_xlabel="Time", sigma_value=2,
             text_ylabel="Quotes")
			events = explain_anomalies(Y, window_size=10, sigma=2)
			print("Information about the anomalies model:{}".format(events))
			#########################
			trace = {'type':"line", 'mode':"lines", 'name':k, 'x':dates,'y':quotes}
			traces.append(trace)
	# print prices
	# z=df['BTC'].tolist()
	# print z
	# print data
	# for k in range(len(traces)):
	#     traces[k].update(
	#         {
	#             "type": "line",
	#             # "hoverinfo": "name+x+text",
	#             # "line": {"width": 0.5}, 
	#             # "marker": {"size": 8},
	#             "mode": "lines+markers",
	#             # "showlegend": False
	#         }
	#     )
	# data = {'traces':trace}
	return json.dumps(traces)
if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
