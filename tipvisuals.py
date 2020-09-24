import numpy as np
import math
import requests
import seaborn as sns
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

url = "https://maps.googleapis.com/maps/api/staticmap?"

#displays barplot of tipPercent against filter_by parameter
#function takes dataframe as input, and column to use as x_axis
def showPlot(data, filter_by=None):
	filtereddata = data.groupby(filter_by).mean()	
	sns.barplot(x=filtereddata.index, y=filtereddata['tip'])

#creates a grid bounded by map limits, taking deliveries dataframe
#as input, along with width and height of pixels for map
#and the center of map along with the zoom level
#returns numpy grid of averaged tips
def weightedgrid(df, w, h, center, zoom, resolution=40000):
	
	#calculates coords for the corners
    northEast = get_pixel_coords(w, 0, w, h, center, zoom)
    southWest = get_pixel_coords(0, h, w, h, center, zoom)

    #grid size = (width, height)
    grid_size = (northEast[1] - southWest[1], northEast[0] - southWest[0])

    #length of side of an individual cell
    cell_len = np.sqrt((grid_size[0] * grid_size[1]) / resolution)

    #creates two grids for sum and count to calculate average
    gridsum = np.zeros((int(grid_size[1] / cell_len),
                      int(grid_size[0] / cell_len)))
    gridcount = np.zeros((int(grid_size[1] / cell_len),
                          int(grid_size[0] / cell_len)))

	#goes through all deliveries and find the grid cell
	#it belongs to and adds the tip and adds to the count
	#to that cell
    for row in df.itertuples():
        tip = df['tip'].mean()
        x = int((row.longitude - southWest[1]) / cell_len)
        if x >= gridsum.shape[1]: x = gridsum.shape[1] - 1
        elif x < 0: x = 0
        else: tip = row.tip

        y = int((northEast[0] - row.latitude) / cell_len)
        if y >= gridsum.shape[0]: y = gridsum.shape[0] - 1
        elif y < 0: y = 0
        else: tip = row.tip

        gridsum[y, x] += tip
        gridcount[y, x] += 1
	
	#divides the first layer of grid by the second to get average
    grid = np.divide(gridsum, gridcount, out=gridcount, where=gridcount!=0)

	#sets empty data to average tip value
    grid[grid==0] = df['tip'].mean()

	#applies a gaussian blur to the grid to get smoothing
    grid = gaussian_filter(grid, sigma=4)
    return grid

#calculates coordinates for given pixel of google static map
#x and y as pixel values as input, width, height, center, and
#zoom of map necessary for input. Returns coordinates for given pixel
def get_pixel_coords(x, y, w, h, center, zoom):
    parallelMultiplier = math.cos(center[0] * math.pi / 180)
    
    degreesPerPixelX = 360 / math.pow(2, zoom + 8)
    degreesPerPixelY = 360 / math.pow(2, zoom + 8) * parallelMultiplier
    
    pointLat = center[0] - degreesPerPixelY * (y - h / 2)
    pointLng = center[1] + degreesPerPixelX * (x  - w / 2)
    
    return (pointLat, pointLng)

#creates a weighted heatmap of tip averages, takes dataframe
#as input, along with width and height for pixels, and
#an api_key to generate google map image
def geo_weighted_heatmap(df, w, h, api_key, zoom=12):

	#calculates the center 
    center = (df['latitude'].mean(), df['longitude'].mean())

	#requests a map from google api
    img = open('map.png','wb')
    img.write(requests.get(url + "center=" + str(center[0]) + "," + 
				str(center[1]) + "&zoom=" + str(zoom) + "&size=" + str(w) +
				"x" + str(h) +"&key=" + api_key).content)
    img.close()
    img = mpimg.imread('map.png', 0)

	#creates weighted grid
    grid = weightedgrid(df, w, h, center, zoom)

	#plots heatmap over grid
    plt.figure(figsize=(10, 10))
    heatmap = sns.heatmap(grid, cmap='RdYlGn',
						xticklabels=False, yticklabels=False)
    cbar = heatmap.collections[0].colorbar
    cbar.set_ticks([])
    cbar.set_ticklabels([])
    heatmap.imshow(img,
          aspect = heatmap.get_aspect(),
          extent = heatmap.get_xlim() + heatmap.get_ylim(),
          zorder = 1,
        alpha=.5)
    heatmap.figure
