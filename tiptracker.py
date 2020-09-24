import streamlit as st
import pydeck as pdk
import pandas as pd
import processdata
import tipvisuals 

#loads data through streamlit file uploader
#processes data through cached function
#returns featuredata
def loaddata(api_key):
	st.set_option('deprecation.showfileUploaderEncoding', False)
	datafile = st.file_uploader(
		"Choose a deliveries CSV data file", type=['csv'])
	return cachedata(datafile, api_key)
@st.cache
def cachedata(datafile, api_key):
	if datafile is not None:
		data = pd.read_csv(datafile)
		featuredata = processdata.processData(data, api_key)
		print('Updated Feature Data.')
		return featuredata
	else: return pd.DataFrame()

#loads main content onto streamlit page
def loadcontent():
	st.title('Tip Tracking & Predicting')

	#gets api key from client
	api_input = st.text_input(
		"Enter API Key for Data Processing", "API_KEY")	
	
	#calls loaddata, toggle data visualizations
	featuredata = loaddata(api_input)
	if not featuredata.empty:	

		#displays geoheatmap for average tips
		st.header('Average Tips Geo-Heatmap')
		tipvisuals.geo_weighted_heatmap(
			featuredata[featuredata['tip'] < 10], 350, 500, api_input)	
		st.pyplot()

		#data visualizations over time
		if st.checkbox('Show Time Data'):
			if st.checkbox('Show Tip Percent vs. Hour'):
				tipvisuals.showPlot(featuredata, filter_by='hour')
				st.pyplot()
			if st.checkbox('Show Tip Percent vs. Day of Week'):
				tipvisuals.showPlot(featuredata, filter_by='dayofweek')
				st.pyplot()
			if st.checkbox('Show Tip Percent vs. Month'):	
				tipvisuals.showPlot(featuredata, filter_by='month')
				st.pyplot()
		

loadcontent()
