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
@app.route("/anomaly")
def anomaly():
	return render_template("anomaly.html")
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
	return json.dumps(data)

@app.route("/basic", methods=['POST'])
def get_quotes():
	# print "CALLED APP"
	cur = request.json['cur[]']
	time = request.json['time_range[]']
	# print time, cur
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
			x, y, y_av, x_anomaly, y_anomaly = plot_results(x, y=Y, window_size=10, text_xlabel="Time", sigma_value=2, text_ylabel="Quotes")
			events = explain_anomalies(Y, window_size=10, sigma=2)
			print("Information about the anomalies model:{}".format(events))
			#############
			trace = {'name':k, 'x':dates,'y':high}
			traces.append(trace)
		# trace2 = {'type':"scatter", 'mode':"lines", 'name':'LOW', 'x':dates,'y':low, 'line':{'color': '#7F7F7F'}}
		# data = [trace1, trace2]
	else:
		prices,_ = get_quotes_intraday(currency_names=cur)
		for k in prices.keys():
			quotes=[x['price'] for x in prices[k]]
			dates=[x['time'] for x in prices[k]]
			###################
			x = pd.Series(dates)
			Y = pd.Series(quotes)
			x, y, y_av, x_anomaly, y_anomaly = plot_results(x, y=Y, window_size=10, text_xlabel="Time", sigma_value=2, text_ylabel="Quotes")
			events = explain_anomalies(Y, window_size=10, sigma=2)
			print("Information about the anomalies model:{}".format(events))
			###################
			trace = {'name':k, 'x':dates,'y':quotes}
			traces.append(trace)
	for k in range(len(traces)):
	    traces[k].update(
	        {
	            "type": "line",
	            "mode": "lines",
	        }
	    )
	layout = {
		
		"xaxis": {"autorange": True, "rangeslider": dict(), "type": "date"},
	}
	data = {'traces':traces,'layout':layout, 'anomaly': {'x':x.tolist(),'y':y.tolist(),'y_av':y_av.tolist(),'x_anomaly':x_anomaly.tolist()}}
	# print data
	return json.dumps(data)

@app.route("/get_articles", methods=['POST'])
def get_articles():
	cur = request.json['cur[]']
	time = request.json['time[]']
	# if len(cur)==1 and len(time) == 1:
	articles=get_article_recommendations(request.json['cur[]'][0],request.json['time[]'][0])
	return json.dumps(articles)

if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
