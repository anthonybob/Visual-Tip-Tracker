import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import requests
import seaborn as sns
import matplotlib.pyplot as plt

newdeliveries = pd.read_csv('featuredata.csv')
deliveries = pd.read_csv('deliveries.csv')

center=[45.505372,-122.475917]
bounds = [newdeliveries['latitude'].min(), newdeliveries['longitude'].max(), 
          newdeliveries['latitude'].max(), newdeliveries['longitude'].min()]

COLOR_BREWER_BLUE_SCALE = [
    [240, 249, 232],
    [204, 235, 197],
    [168, 221, 181],
    [123, 204, 196],
    [67, 162, 202],
    [8, 104, 172],
]

coords = newdeliveries[['latitude', 'longitude']]

st.pydeck_chart(pdk.Deck(
	map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
		latitude=center[0],
        longitude=center[1],
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
			'HexagonLayer',
            data=newdeliveries,
            get_position=['longitude', 'latitude'],
            radius=200,
            elevation_scale=4,
            elevation_range=[0, 1000],
			get_elevation='tipPercent * 1000',
            pickable=True,
            extruded=True,
		),
        pdk.Layer(
            'ScatterplotLayer',
            data=newdeliveries,
            get_position=['longitude', 'latitude'],
            get_color='[200, 30, 0, 160]',
            get_radius=200,
         ),
     ],
))


view = pdk.data_utils.compute_view(newdeliveries[["longitude", "latitude"]])
view.zoom = 11

st.pydeck_chart(pdk.Deck(
	layers = [pdk.Layer(
 	   "HeatmapLayer",
 	   data=newdeliveries,
 	   opacity=0.8,
 	   get_position=["longitude", "latitude"],
 	   aggregation='"MEAN"',
 	   color_range=COLOR_BREWER_BLUE_SCALE,
 	   threshold=.3,
 	   get_weight="tipPercent * 100",
 	   pickable=True,
	)],

	initial_view_state=view
))
