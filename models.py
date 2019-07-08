#!/Users/chelsea/practice/python/monte/venv python

from flask import Flask, render_template, request, Response
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

# from aylienapiclient import textapi
# import time
# import aylien_news_api
# from aylien_news_api.rest import ApiException

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

from dotenv import load_dotenv
import os

load_dotenv()

IEX_secret_token = os.getenv("IEX_secret_token")
IEX_publishable_token = os.getenv("IEX_publishable_token")
token = IEX_secret_token

# AYLIEN_key = os.getenv("AYLIEN_key")
# AYLIEN_id = os.getenv("AYLIEN_id")

def camelcase_split(*args):
	new_args =[]
	for arg in args:
		word_list = wordninja.split(arg)
		new_key = " ".join(word for word in word_list).title()
		new_args.append(new_key)
	return new_args

class Asset():
	def __init__(self, ticker):
		self.ticker = ticker
		self.company = {}
		self.company_name = ""
		self.financials= {}
		self.tops = {}
		self.historicals = {}

	def fetch_company(self):
		query = urllib.parse.quote(self.ticker)
		data = requests.get("https://api.iextrading.com/1.0/stock/"+query+"/company").json()
		
		# # dummy data
		# data = {"symbol":"AAPL","companyName":"Apple Inc.","exchange":"Nasdaq Global Select","industry":"Computer Hardware","website":"http://www.apple.com","description":"Apple Inc is designs, manufactures and markets mobile communication and media devices and personal computers, and sells a variety of related software, services, accessories, networking solutions and third-party digital content and applications.","CEO":"Timothy D. Cook","issueType":"cs","sector":"Technology","tags":["Technology","Consumer Electronics","Computer Hardware"]}

		self.company_name = data["companyName"]
		self.company = data

	def fetch_financials(self):
		query = urllib.parse.quote(self.ticker)
		data = requests.get("https://cloud.iexapis.com/stable/stock/"+query+"/financials?token="+token+"&symbols="+query).json()
		
		# # dummy data
		# data = {"symbol":"AAPL","financials":[{"reportDate":"2019-03-31","grossProfit":21648000000,"costOfRevenue":36270000000,"operatingRevenue":57918000000,"totalRevenue":57918000000,"operatingIncome":13242000000,"netIncome":11561000000,"researchAndDevelopment":3948000000,"operatingExpense":44676000000,"currentAssets":123346000000,"totalAssets":341998000000,"totalLiabilities":236138000000,"currentCash":38329000000,"currentDebt":22429000000,"shortTermDebt":22429000000,"longTermDebt":90201000000,"totalCash":80433000000,"totalDebt":112630000000,"shareholderEquity":105860000000,"cashChange":-4954000000,"cashFlow":11155000000}]}
		
		financials = data['financials']
		financials = financials[0]
		financials_cleaned = {}

		for key, value in financials.items():
			cleaned = camelcase_split(key)
			new_key = cleaned[0]
			if key != "reportDate" and value != None and value != "None" :
				financials_cleaned[new_key] = "${:,.2f}".format(value)
			else:
				financials_cleaned[new_key] = value

		self.financials = financials_cleaned

	def fetch_tops(self):
		query = urllib.parse.quote(self.ticker)
		data = requests.get("https://cloud.iexapis.com/stable/tops/?token="+token+"&symbols="+query).json()
		
		# # dummy data
		# data = [{"symbol":"AAPL","sector":"electronictechnology","securityType":"cs","bidPrice":0,"bidSize":0,"askPrice":0,"askSize":0,"lastUpdated":1557432002489,"lastSalePrice":200.64,"lastSaleSize":50,"lastSaleTime":1557432002489,"volume":940961}]
		
		self.tops = data[0]

	def fetch_historicals(self, time_range):
		query = urllib.parse.quote(self.ticker)
		data = requests.get("https://cloud.iexapis.com/stable/stock/"+query+"/chart/"+time_range+"?token="+token).json()

		# # dummy data
		# data = [{"date":"2019-04-08","open":196.42,"close":200.1,"high":200.23,"low":196.34,"volume":25881697,"uOpen":196.42,"uClose":200.1,"uHigh":200.23,"uLow":196.34,"uVolume":25881697,"change":0,"changePercent":0,"label":"Apr 8","changeOverTime":0},{"date":"2019-04-09","open":200.32,"close":199.5,"high":202.85,"low":199.23,"volume":35768237,"uOpen":200.32,"uClose":199.5,"uHigh":202.85,"uLow":199.23,"uVolume":35768237,"change":-0.6,"changePercent":-0.2999,"label":"Apr 9","changeOverTime":-0.002999},{"date":"2019-04-10","open":198.68,"close":200.62,"high":200.74,"low":198.18,"volume":21695288,"uOpen":198.68,"uClose":200.62,"uHigh":200.74,"uLow":198.18,"uVolume":21695288,"change":1.12,"changePercent":0.5614,"label":"Apr 10","changeOverTime":0.002599},{"date":"2019-04-11","open":200.85,"close":198.95,"high":201,"low":198.44,"volume":20900808,"uOpen":200.85,"uClose":198.95,"uHigh":201,"uLow":198.44,"uVolume":20900808,"change":-1.67,"changePercent":-0.8324,"label":"Apr 11","changeOverTime":-0.005747},{"date":"2019-04-12","open":199.2,"close":198.87,"high":200.14,"low":196.21,"volume":27760668,"uOpen":199.2,"uClose":198.87,"uHigh":200.14,"uLow":196.21,"uVolume":27760668,"change":-0.08,"changePercent":-0.0402,"label":"Apr 12","changeOverTime":-0.006147},{"date":"2019-04-15","open":198.58,"close":199.23,"high":199.85,"low":198.01,"volume":17536646,"uOpen":198.58,"uClose":199.23,"uHigh":199.85,"uLow":198.01,"uVolume":17536646,"change":0.36,"changePercent":0.181,"label":"Apr 15","changeOverTime":-0.004348},{"date":"2019-04-16","open":199.46,"close":199.25,"high":201.37,"low":198.56,"volume":25696385,"uOpen":199.46,"uClose":199.25,"uHigh":201.37,"uLow":198.56,"uVolume":25696385,"change":0.02,"changePercent":0.01,"label":"Apr 16","changeOverTime":-0.004248},{"date":"2019-04-17","open":199.54,"close":203.13,"high":203.38,"low":198.61,"volume":28906780,"uOpen":199.54,"uClose":203.13,"uHigh":203.38,"uLow":198.61,"uVolume":28906780,"change":3.88,"changePercent":1.9473,"label":"Apr 17","changeOverTime":0.015142},{"date":"2019-04-18","open":203.12,"close":203.86,"high":204.15,"low":202.52,"volume":24195766,"uOpen":203.12,"uClose":203.86,"uHigh":204.15,"uLow":202.52,"uVolume":24195766,"change":0.73,"changePercent":0.3594,"label":"Apr 18","changeOverTime":0.018791},{"date":"2019-04-22","open":202.83,"close":204.53,"high":204.94,"low":202.34,"volume":19439545,"uOpen":202.83,"uClose":204.53,"uHigh":204.94,"uLow":202.34,"uVolume":19439545,"change":0.67,"changePercent":0.3287,"label":"Apr 22","changeOverTime":0.022139},{"date":"2019-04-23","open":204.43,"close":207.48,"high":207.75,"low":203.9,"volume":23322991,"uOpen":204.43,"uClose":207.48,"uHigh":207.75,"uLow":203.9,"uVolume":23322991,"change":2.95,"changePercent":1.4423,"label":"Apr 23","changeOverTime":0.036882},{"date":"2019-04-24","open":207.36,"close":207.16,"high":208.48,"low":207.05,"volume":17540609,"uOpen":207.36,"uClose":207.16,"uHigh":208.48,"uLow":207.05,"uVolume":17540609,"change":-0.32,"changePercent":-0.1542,"label":"Apr 24","changeOverTime":0.035282},{"date":"2019-04-25","open":206.83,"close":205.28,"high":207.76,"low":205.12,"volume":18543206,"uOpen":206.83,"uClose":205.28,"uHigh":207.76,"uLow":205.12,"uVolume":18543206,"change":-1.88,"changePercent":-0.9075,"label":"Apr 25","changeOverTime":0.025887},{"date":"2019-04-26","open":204.9,"close":204.3,"high":205,"low":202.12,"volume":18649102,"uOpen":204.9,"uClose":204.3,"uHigh":205,"uLow":202.12,"uVolume":18649102,"change":-0.98,"changePercent":-0.4774,"label":"Apr 26","changeOverTime":0.02099},{"date":"2019-04-29","open":204.4,"close":204.61,"high":205.97,"low":203.86,"volume":22204716,"uOpen":204.4,"uClose":204.61,"uHigh":205.97,"uLow":203.86,"uVolume":22204716,"change":0.31,"changePercent":0.1517,"label":"Apr 29","changeOverTime":0.022539},{"date":"2019-04-30","open":203.06,"close":200.67,"high":203.4,"low":199.11,"volume":46534923,"uOpen":203.06,"uClose":200.67,"uHigh":203.4,"uLow":199.11,"uVolume":46534923,"change":-3.94,"changePercent":-1.9256,"label":"Apr 30","changeOverTime":0.002849},{"date":"2019-05-01","open":209.88,"close":210.52,"high":215.31,"low":209.23,"volume":64827328,"uOpen":209.88,"uClose":210.52,"uHigh":215.31,"uLow":209.23,"uVolume":64827328,"change":9.85,"changePercent":4.9086,"label":"May 1","changeOverTime":0.052074},{"date":"2019-05-02","open":209.84,"close":209.15,"high":212.65,"low":208.13,"volume":31996324,"uOpen":209.84,"uClose":209.15,"uHigh":212.65,"uLow":208.13,"uVolume":31996324,"change":-1.37,"changePercent":-0.6508,"label":"May 2","changeOverTime":0.045227},{"date":"2019-05-03","open":210.89,"close":211.75,"high":211.84,"low":210.23,"volume":20892378,"uOpen":210.89,"uClose":211.75,"uHigh":211.84,"uLow":210.23,"uVolume":20892378,"change":2.6,"changePercent":1.2431,"label":"May 3","changeOverTime":0.058221},{"date":"2019-05-06","open":204.29,"close":208.48,"high":208.84,"low":203.5,"volume":32443113,"uOpen":204.29,"uClose":208.48,"uHigh":208.84,"uLow":203.5,"uVolume":32443113,"change":-3.27,"changePercent":-1.5443,"label":"May 6","changeOverTime":0.041879}]
		
		historicals = [tuple((i["date"],i["close"])) for i in data]
		
		self.historicals = historicals

# 	# UNFINISHED
# 	def fetch_news_data(self):
# 		# Configure API key authorization: app_id
# 		aylien_news_api.configuration.api_key['X-AYLIEN-NewsAPI-Application-ID'] = AYLIEN_id
# 		# Configure API key authorization: app_key
# 		aylien_news_api.configuration.api_key['X-AYLIEN-NewsAPI-Application-Key'] = AYLIEN_key

# 		# create an instance of the API class
# 		api_instance = aylien_news_api.DefaultApi()

# 		params = {
# 			'language' : ['en'],
# 			'sort_by' : 'relevance',
# 			'text' : self.company_name,
# 			'cursor': '*',
#   			'per_page': 10,
#   			'_return' : ['title', 'summary', 'sentiment']
# 		}

# 		response = api_instance.list_stories(**params)

# 		stories = response.stories

# 		for story in stories:
# 			print(story["title"])

# asset = Asset("aapl")
# asset.company_name = "Apple, Inc."
# asset.fetch_news_data()