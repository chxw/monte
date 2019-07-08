#! /usr/bin/env python

from flask import Flask, render_template, request, Response
from models import *
from graph_tools import *

import urllib
import requests
import math
import statistics
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import io
import base64
import re
import wordninja

from bokeh.io import curdoc
from bokeh.models import HoverTool
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models.widgets import Slider
from datetime import datetime
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.palettes import Category20_10 as palette
from bokeh.embed import components
import itertools 

app = Flask(__name__)

# HOME
@app.route("/", methods = ['POST', 'GET'])
def home():
	return render_template("index.html")

# COMPANY INFO 
@app.route("/ticker", methods = ['POST', 'GET'])
def ticker():
	if request.method == "POST":
		# Get user input from form
		ticker = request.form['ticker']

		# Create instance of class and start filling with necessary data
		asset = Asset(ticker=ticker)
		asset.fetch_company()
		asset.fetch_tops()
		asset.fetch_financials()

		return render_template("ticker.html", ticker=asset.ticker,company=asset.company, tops=asset.tops, financials=asset.financials)

# MONTE CARLO SIMULATION
@app.route("/MC", methods = ['POST', 'GET'])
def monte_carlo():
	if request.method == "POST":
		# Get user input from form
		time_range = request.form.get('range-select')

		if (request.form['num_sims'] == ''):
			num_sims = 100
		else:
			num_sims = int(request.form['num_sims'])

		if (request.form['days_out'] == ''):
			days_out = 252
		else:
			days_out = int(request.form['days_out'])

		ticker = request.form['MC-ticker']

		# Create instance of class and start filling with necessary data
		asset = Asset(ticker=ticker)
		asset.fetch_historicals(time_range)

		# Graph historical prices
		historicals_graph = graph_historicals(asset.historicals)

		# Embed plot into HTML via Flask Render
		historicals_script, historicals_div = components(historicals_graph)

		# Run monte carlo simulation
		monte = MC_sim(asset.historicals, num_sims, days_out)

		# Embed plot into HTML via Flask Render
		monte_script, monte_div = components(monte)

		return render_template("full.html", ticker=asset.ticker, historicals_script=historicals_script, historicals_div=historicals_div, 
			monte_script=monte_script, monte_div=monte_div)

# __name___ != "__main__" if "app" is running a different app
# this prevents duplicating app.run
if __name__ == "__main__":
	app.debug = True
	app.run()
