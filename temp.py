import gmplot
import os
latitudes = [17.4432902, 17.4422778]
longitudes = [78.4874663, 78.4688006]
gmap = gmplot.GoogleMapPlotter((latitudes[0]+latitudes[-1])/2, (longitudes[0]+longitudes[-1])/2, 12)
gmap.plot(latitudes, longitudes, 'cornflowerblue', edge_width=10, marker=True)
gmap.scatter(latitudes, longitudes, '#4444aa', size=80, marker=False)
gmap.scatter(latitudes, longitudes, '#FF0000', size=80, marker=True, c=None, s=None)
gmap.heatmap(latitudes, longitudes)
a = os.path.join(os.path.dirname(__file__), 'markers/%s.png')
print(gmap.coloricon)
gmap.draw("mymap.html")