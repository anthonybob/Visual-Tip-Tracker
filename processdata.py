from googlemaps import Client
import numpy as np
import pandas as pd
from datetime import datetime
from os import path
import time

#sets center
center = [45.505372, -122.475917]

#get API key
gmapskey = Client(key='AIzaSyCqRs4Fb4sY74l52iOjEedBhjt2cKb00L8')
	
#takes deliveries dataframe, adds features recursively
#starting from a given row, returns new df with 
#latitude, longitude, tip, tipPercent, dayofweek, dayofmonth, month
def extractfeatures(deliveries, row):	

	#stop condition, stops at end of dataframe and returns
	if row >= (len(deliveries)): return deliveries
		
	#calculates tip
	deliveries.loc[row, 
		'tip'] = deliveries.loc[row, 'paid'] - deliveries.loc[row, 'total']

	#calculates tipPercent
	deliveries.loc[row, 
		'tipPercent'] = (deliveries.loc[row,'tip'] / deliveries.loc[row,'total'])
	print("Geocoding " + deliveries.loc[row, 'address'] + " # " + str(row + 1)
		+ "/" + str(len(deliveries)))

	#uses google geocoding api to get latitude, longitude of entry
	geocode_result = gmapskey.geocode(deliveries.loc[row, 'address'])

	#adds lat and lng to dataframe
	try:
		deliveries.loc[row, 
			'latitude'] = geocode_result[0]['geometry']['location']['lat']
		deliveries.loc[row, 
			'longitude'] = geocode_result[0]['geometry']['location']['lng']
	except:
		print("Error.")
		print(geocode_result)

	#converts date to datetime obj and adds date/time features to df
	date = pd.to_datetime(deliveries.loc[row, 'date'] + '-' + 
		deliveries.loc[row, 'time'], format='%Y-%m-%d-%H:%M')	
	deliveries.loc[row, 'dayofyear'] = date.dayofyear
	deliveries.loc[row, 'dayofmonth'] = date.day
	deliveries.loc[row, 'dayofweek'] = date.weekday
	deliveries.loc[row, 'month'] = date.month
	if date.hour == 0: deliveries.loc[row, 'hour'] = 24
	else: deliveries.loc[row, 'hour'] = date.hour

	#extract weather features
	deliveries.loc[row, 'prcp'] = extract_precipitation(deliveries.loc[row, 'date'])

	#set quota limit (google has a limit of 50 requests/sec)
	time.sleep(.05)

	#recursive call to continue down the dataframe
	return extractfeatures(deliveries, row + 1)

def extract_precipitation(date):
    dateweather = weatherdata[weatherdata['DATE'] == date]
    closestreport = np.sqrt(((dateweather['LATITUDE'] - center[0])**2) + 
		((dateweather['LONGITUDE'] - center[1])**2))
    return dateweather[closestreport == closestreport.min()]['PRCP'].values[0]
	
#creates/updates featuredata.csv from original deliveries.csv
#calls extractfeatures(), returns a dataframe w/ extracted features
def updatedeliveries():
	if path.exists('deliveries.csv'): 
		print("Getting Coordinates...")
		print("This may take a minute, so grab a cup of tea.")

		deliveries = pd.read_csv('deliveries.csv')

		#checks if some feature data already exists
		if path.exists('featuredata.csv'): 
			featuredata = pd.read_csv('featuredata.csv')

			#checks if featuredata needs to be updated
			if len(featuredata) < len(deliveries):
				
				#concatenates new deliveries and calls extractfeatures()
				deliveries = pd.concat([featuredata, 
					deliveries[len(featuredata):]], axis=0)
				return extractfeatures(deliveries, len(featuredata))

			return featuredata #returns if theres nothing to update

		return extractfeatures(deliveries, 0)
	return

weatherdata = pd.read_csv('weatherdata.csv')
updatedeliveries().to_csv('featuredata.csv', index=False)
print('Updated Feature Data.')
