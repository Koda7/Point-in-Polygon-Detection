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
cnt = 10
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


point_file = "../data/points1000.txt"
count = 1000
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
            
# Defining distance threshold
n = 4000

def withinNdistance(points, polygons, n):
    results = []
    for point in points:
        within = False
        for polygon in polygons:
            if(ray_casting(point, list(polygon.exterior.coords))): 
                break
            else: 
                distance = polygon.boundary.distance(point)
                if distance <= n:
                    within = True
                    break
        results.append(within)
    return results

results = withinNdistance(points, polygons, n)

# end_time = timeit.default_timer()

# print("Execution time:", end_time - start_time, "seconds")

    