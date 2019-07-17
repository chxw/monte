import math
import statistics
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style

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

def graph_MC_sim(simulations, num_predicted_days, end_y):

	# Create figure
	p = figure(title="Monte Carlo Simulation", name="MC")

	# Format figure
	hover_tool = HoverTool(
		tooltips=[('date', '@x'), ('y', '$@{y}{0.2f}')],
		)
	p.tools.append(hover_tool)
	p.grid.grid_line_alpha=0.3
	p.xaxis.axis_label = 'Days Out'
	p.yaxis.axis_label = 'Price'

	# Plot each simulation in rotating colors
	colors = itertools.cycle(palette)
	for ycoords, color in zip(simulations, colors):
		p.line(range(num_predicted_days), ycoords, color=color)

	# Plot end y line
	p.line(range(num_predicted_days), end_y)

	return(p)

def graph_historicals(historicals):
	# Format data
	xs = [tup[0] for tup in historicals]
	xs = [datetime.strptime(x, "%Y-%m-%d") for x in xs]
	ys = [tup[1] for tup in historicals]

	# Create figure
	p = figure(title="Historical prices", name="historicals", x_axis_type='datetime')

	# Format figure
	hover_tool = HoverTool(
		tooltips=[('date', '@x{%F}'), ('y', '$@{y}{0.2f}')],
		formatters={'x': 'datetime'},
		mode='vline'
		)
	p.tools.append(hover_tool)

	p.grid.grid_line_alpha=0.3
	p.xaxis.axis_label = 'Date'
	p.yaxis.axis_label = 'Close Price'
	p.xaxis.formatter=DatetimeTickFormatter(
	    years=["%Y-%m%-d"],
	    months=["%Y-%m-%d"],
	    days=["%Y-%m-%d"],
	)

	# Plot line
	p.line(xs, ys)

	return(p)

def MC_sim(historicals, num_sims, num_predicted_days):
	# Get ys from y-coordinate in tuple from list of tuple
	ys = [tup[1] for tup in historicals]

	# Put in panda dataframe to calculate returns and daily volatility
	df = pd.DataFrame(ys)
	returns = df.pct_change()
	daily_vol = returns.std()

	# Set most recent price as starting point for each simulation
	recent = ys[-1]

	# List to collect simulations (lists of y-coordinates)
	simulations = []

	# Given num_sims of simulations to run...
	for sim in range(num_sims):
		i = 0

		# Create a new simulation
		simulation = []

		# To get next y: previous y * some random deviation (normalized to 0) within scale of historical daily volatility
		# This is base case - to be done for first predicted y for each simulation
		y = recent*(1+np.random.normal(0, daily_vol))

		# Add first predicted y
		simulation.append(y)

		# Add the next day y, each "predicted" off the "most recent" one
		for days_out in range(num_predicted_days-1):
			# "Predict" next day y
			y = simulation[i]*(1+np.random.normal(0, daily_vol))
			simulation.append(y)
			i += 1

		simulations.append(simulation)

	# Graph simulation
	monte = graph_MC_sim(simulations, num_predicted_days, recent)
	
	return monte
