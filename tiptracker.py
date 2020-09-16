import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import requests
import seaborn as sns
import matplotlib.pyplot as plt
import processdata

#loads data through streamlit file uploader
#processes data through cached function
#returns featuredata
def loaddata():
	st.set_option('deprecation.showfileUploaderEncoding', False)
	datafile = st.file_uploader("Choose a file", type=['csv'])
	return cachedata(datafile)
@st.cache
def cachedata(datafile):
	if datafile is not None:
		data = pd.read_csv(datafile)
		featuredata = processdata.processData(data)
		print('Updated Feature Data.')
		return featuredata
	else: return pd.DataFrame()

#loads main content onto streamlit page
def loadcontent():
	st.title('Tip Tracking & Predicting')

	center=[45.505372,-122.475917]
	
	#heatmap gradient
	COLOR_HEATMAP = [
		[247, 240, 198],
		[232, 222, 165],
		[252, 233, 121],
		[235, 205, 30],
		[245, 168, 2],
		[245, 144, 2],
		[245, 107, 2],
		[245, 79, 2],
		[245, 79, 2]
	]

	#calls loaddata, toggle data visualizations
	featuredata = loaddata()
	if not featuredata.empty:
		if st.checkbox('Show Average Tips Heatmap'):
			showHeatmap(featuredata, COLOR_HEATMAP)
		if st.checkbox('Show Average Day of Week Tips Heatmap'):
			showHeatmap(featuredata, COLOR_HEATMAP, filter_by='dayofweek')	
		if st.checkbox('Show Average Day of Year Tips Heatmap'):
			showHeatmap(featuredata, COLOR_BREWER_BLUE_SCALE, filter_by='dayofyear')
		if st.checkbox('Show Tip Percent vs. Hour'):
			showPlots(featuredata, filter_by='hour')
		if st.checkbox('Show Tip Percent vs. Day of Week'):
			showPlots(featuredata, filter_by='dayofweek')
		if st.checkbox('Show Tip Percent vs. Month'):	
			showPlots(featuredata, filter_by='month')

#displays barplot of tipPercent against filter_by parameter
#function takes dataframe as input, and column to use as x_axis
def showPlots(data, filter_by=None):
	filtereddata = data.groupby(filter_by).mean()	
	sns.barplot(x=filtereddata.index, y=filtereddata['tipPercent'])
	st.pyplot()

#displays heatmap using feature to filter by
#takes dataframe, color gradient, and filter as input
#if filter is None, heatmap of all data will be created
def showHeatmap(data, color_gradient, filter_by=None):

	#slider to filter data by the filter
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
		#displays heatmap
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
	
loadcontent()
