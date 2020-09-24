from googlemaps import Client
import pandas as pd
from datetime import datetime
from os import path
import time

weatherdata = pd.read_csv('weatherdata.csv')

#sets center
center = [45.505372, -122.475917]
	
#takes deliveries dataframe, adds features recursively
#starting from a given row, returns new df with 
#latitude, longitude, tip, tipPercent, dayofweek, dayofmonth, month
def extractFeatures(deliveries, api_key):		

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
	deliveries['hour'] = dates.dt.hour.apply(lambda time: 24 if time == 0 else time)

	
	#get API key
	gmapskey = Client(key=api_key)
	#applies geocode function to get lat and long
	deliveries['latitude'], deliveries['longitude'] = zip(
		*deliveries['address'].apply(extractCoords, kwargs=(api_key,)))
	
	#gets zip code from address
	deliveries['zip'] = deliveries['address'].apply(
		lambda address: int(address.split()[-1]))

	return deliveries

def extractCoords(address, gmapskey):
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
def processData(data, api_key):
	if path.exists('featuredata.csv'):
		featuredata = pd.read_csv('featuredata.csv')
		if(len(featuredata) < len(data)):
			deliveries = pd.concat([featuredata,
				extractFeatures(data.loc[len(featuredata):, :], api_key)],
				axis=0)
		else: return featuredata
	else: deliveries = extractFeatures(data, api_key)

	deliveries.to_csv('featuredata.csv', index=False)
	return deliveries 
