import rtree
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import geopandas as gpd
import lxml.etree as ET
import pandas as pd
import timeit

# start_time = timeit.default_timer()

def makePolygon(coordinates):
    split = coordinates[:-1].split(" ")
    df = pd.DataFrame({"lat": [float(x.split(",")[0]) for x in split], "long": [
                      x.split(",")[1] for x in split]})
    # gdf = gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df.lat,df.long))

    polygon_geom = Polygon(zip(df['lat'], df['long']))
    polygon = gpd.GeoDataFrame(index=[0], geometry=[polygon_geom])
    return polygon


def makePoint(coordinates):
    lat, long = (float(x) for x in coordinates.split(","))
    polygon_geom = Point(lat, long)
    point = gpd.GeoDataFrame(index=[0], geometry=[polygon_geom])
    return point


file = "../data/poly15.txt"
cnt = 15
polygons = []
with open(file, 'r') as f:
    for line in f:
        cnt -= 1
        if cnt == 0:
            break
        poly = '<' + line.split(":<")[1]
        poly = poly.replace('srsName', 'crsName')
        root = ET.fromstring(poly)
        coordinates = root.findall(
            ".//{http://www.opengis.net/gml}coordinates")
        maxi = -1e15
        point = None
        for index, c in enumerate(coordinates):
            p = makePolygon(c.text)
            polygons.append(p['geometry'][0])

point_file = "../data/points500.txt"
count = 500
points = []
with open(point_file, 'r') as f:
    for line in f:
        count -= 1
        if count == 0:
            break
        point = '<' + line.split(":<")[1]
        point = point.replace('srsName', 'crsName')
        root = ET.fromstring(point)
        coordinates = root.findall(
            ".//{http://www.opengis.net/gml}coordinates")
        for c in coordinates:
            p = makePoint(c.text)
            points.append(p['geometry'][0])


# Creating R-tree index using the MBRs of the polygons
idx = rtree.index.Index()
for i, polygon in enumerate(polygons):
    idx.insert(i, polygon.bounds)

# Ray casting algorithm
def ray_casting(point, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n+1):
        p2x, p2y = poly[i % n]
        if point.y > min(p1y, p2y):
            if point.y <= max(p1y, p2y):
                if point.x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (point.y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or point.x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

# Performing a range query for each point
for index, point in enumerate(points):
    bbox = point.bounds
    intersected_polygons = [polygons[i] for i in idx.intersection(bbox)]
    for polygon in intersected_polygons:
        if ray_casting(point, list(polygon.exterior.coords)):
            print(
                f"Point {index} is inside Polygon {polygons.index(polygon)}")

# Printing a message for any points that are not inside any polygons
for index, point in enumerate(points):
    bbox = point.bounds
    intersected_polygons = [polygons[i] for i in idx.intersection(bbox)]
    if not intersected_polygons:
        print(f"Point {index} is not inside any polygons")

# Plot the polygons
for i, poly in enumerate(polygons):
    plt.plot(*poly.exterior.xy)
    plt.annotate(str(i), [poly.centroid.x, poly.centroid.y], color='blue')

# Plot the points
for i, point in enumerate(points):
    plt.plot(point.x, point.y, 'ro')
    plt.annotate(str(i), [point.x, point.y], color='red')


# Set the axis limits and show the plot
# end_time = timeit.default_timer()
# print("Execution time:", end_time - start_time, "seconds")

plt.show()



