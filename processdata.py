from googlemaps import Client
import numpy as np
import pandas as pd
from datetime import datetime
from os import path
import time

weatherdata = pd.read_csv('weatherdata.csv')

#sets center
center = [45.505372, -122.475917]

#get API key
gmapskey = Client(key='API_KEY')
	
#takes deliveries dataframe, adds features recursively
#starting from a given row, returns new df with 
#latitude, longitude, tip, tipPercent, dayofweek, dayofmonth, month
def extractFeatures(deliveries):		

	#calculates tip
	deliveries['tip'] = deliveries['paid'] - deliveries['total']

	#calculates tipPercent
	deliveries['tipPercent'] = deliveries['tip'] / deliveries['total']

	#converts date to datetime obj and adds date/time features to df
	dates = pd.to_datetime(deliveries['date'] + '-' + 
		deliveries['time'], format='%Y-%m-%d-%H:%M')	
	deliveries['dayofyear'] = dates.dt.dayofyear
	deliveries['dayofmonth'] = dates.dt.day
	deliveries['dayofweek'] = dates.dt.weekday
	deliveries['month'] = dates.dt.month
	deliveries['hour'] = dates.dt.hour

	#extract weather features
	deliveries['prcp'] = deliveries['date'].apply(extractPrecipitation)

	#applies geocode function to get lat and long
	deliveries['latitude'], deliveries['longitude'] = zip(
		*deliveries['address'].apply(extractCoords))
	
	#gets zip code from address
	deliveries['zip'] = deliveries['address'].apply(
		lambda address: int(address[-5:]))

	return deliveries

def extractCoords(address):
	print("Geocoding " + address)

	#uses google geocoding api to get latitude, longitude of entry
	geocode_result = gmapskey.geocode(address)

	#set quota limit (google has a limit of 50 requests/sec)
	time.sleep(.05)

	#adds lat and lng to dataframe
	try:
		latitude = geocode_result[0]['geometry']['location']['lat']
		longitude = geocode_result[0]['geometry']['location']['lng']
	except:
		print("Error.")
		print(geocode_result)		
		return 0, 0
	return latitude, longitude

def extractPrecipitation(date):
    dateweather = weatherdata[weatherdata['DATE'] == date]
    closestreport = np.sqrt(((dateweather['LATITUDE'] - center[0])**2) + 
		((dateweather['LONGITUDE'] - center[1])**2))
    return dateweather[closestreport == closestreport.min()]['PRCP'].values[0]
	
#creates/updates featuredata.csv from original deliveries.csv
#calls extractfeatures(), returns a dataframe w/ extracted features
def processData(filename):
	if path.exists(filename): 
		print("Getting Coordinates...")
		print("This may take a minute, so grab a cup of tea.")

		data = pd.read_csv(filename)

		#checks if some feature data already exists
		if path.exists('featuredata.csv'): 
			featuredata = pd.read_csv('featuredata.csv')

			#checks if featuredata needs to be updated
			if len(featuredata) < len(data):
				
				#concatenates new deliveries and calls extractfeatures()
				return pd.concat([featuredata,
					extractFeatures(data[len(featuredata):])], axis=0)

			return featuredata #returns if theres nothing to update

		return extractFeatures(data)
	return
