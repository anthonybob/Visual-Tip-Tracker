from googlemaps import Client
import numpy as np
import pandas as pd
from datetime import datetime
import time

#get API client and read data frame
gmapskey = Client(key='API_KEY')
deliveries = pd.read_csv('deliveries.csv')

latitudelist = []
longitudelist = []
daylist = []
weekdays = {0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',
    4:'Friday',5:'Saturday',6:'Sunday'}

#uses google api to get coordinates for all addresses in deliveries df
for address in deliveries['Address']:
    geocode_result = gmapskey.geocode(address)
    print("Getting Coordinates... \
        This may take a minute, so grab a cup of tea.")

    try:
        latitudelist.append(geocode_result[0]['geometry']['location']['lat'])
        longitudelist.append(geocode_result[0]['geometry']['location']['lng'])
        print('Added address: ' + address)
    except:
        print('Error.')
        print(geocode_result)
        latitudelist.append(None)
        longitudelist.append(None)
    time.sleep(.22)

for date in deliveries['Date']:
    daylist.append(weekdays[datetime.strptime(date, '%Y-%m-%d').weekday()])

deliveries.insert(1, 'Day of Week', daylist)

deliveries['Tip'] = deliveries['Paid'] - deliveries['Total']
deliveries['TipPercent'] = deliveries['Tip'] / deliveries['Total']

deliveries['Latitude'] = latitudelist
deliveries['Longitude'] = longitudelist

print('Created newdeliveries.csv file')
deliveries.to_csv('newdeliveries.csv')
