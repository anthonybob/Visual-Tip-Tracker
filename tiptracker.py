import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import requests
import seaborn as sns
import matplotlib.pyplot as plt
import processdata

@st.cache
def loaddata():	
	featuredata = processdata.processData('deliveries.csv')
	featuredata.to_csv('featuredata.csv', index=False)
	print('Updated Feature Data.')
	return featuredata

def loadcontent():
	st.title('Tip Tracking and Predicting')

	center=[45.505372,-122.475917]

	COLOR_BREWER_BLUE_SCALE = [
	    [240, 249, 232],
	    [204, 235, 197],
	    [168, 221, 181],
	    [123, 204, 196],
	    [67, 162, 202],
	    [8, 104, 172],
	]

	featuredata = loaddata()
	st.subheader("Average Tips Heatmaps")
	showHeatmap(featuredata, COLOR_BREWER_BLUE_SCALE)
	showHeatmap(featuredata, COLOR_BREWER_BLUE_SCALE, filter_by='dayofweek')
	showHeatmap(featuredata, COLOR_BREWER_BLUE_SCALE, filter_by='dayofyear')
	showPlots(featuredata, filter_by='hour')
	showPlots(featuredata, filter_by='dayofweek')
	showPlots(featuredata, filter_by='month')

def showPlots(data, filter_by=None):
	filtereddata = data.groupby(filter_by).mean()	
	sns.barplot(x=filtereddata.index, y=filtereddata['tipPercent'])
	st.pyplot()

def showHeatmap(data, color_gradient, filter_by=None):
	if(filter_by != None):
		filter_val = st.slider(
			str('Tips from the ' + str(data[filter_by].min()) + ' ' + filter_by +
				" to the " + str(data[filter_by].max()) + ' ' + filter_by), 
			int(data[filter_by].min()), int(data[filter_by].max()))

		filtereddata = data[data[filter_by]  == filter_val]

	else: filtereddata = data

	if(len(filtereddata) == 0):
		st.write("No Data for this day.")
	else:

		view = pdk.data_utils.compute_view(filtereddata[["longitude", "latitude"]])
		view.zoom = 11
	
		st.pydeck_chart(pdk.Deck(
			layers = [pdk.Layer(
		 	   "HeatmapLayer",
		 	   data=filtereddata,
		 	   opacity=0.8,
		 	   get_position=["longitude", "latitude"],
		 	   aggregation='"MEAN"',
		 	   color_range=color_gradient,
		 	   threshold=.3,
		 	   get_weight="tip * 100",
		 	   pickable=True,
			)], 
			initial_view_state=view))
	
def datetime_converter(date, time):
     return pd.to_datetime(date + '-' + time, format='%Y-%m-%d-%H:%M')

loadcontent()
