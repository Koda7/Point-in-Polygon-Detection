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

# Ray casting algorithm
def ray_casting(point, polygons):
    inside_polygons = []
    for i, polygon in enumerate(polygons):
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for j in range(n+1):
            p2x, p2y = polygon[j % n]
            if point.y > min(p1y, p2y):
                if point.y <= max(p1y, p2y):
                    if point.x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (point.y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or point.x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        if inside:
            inside_polygons.append(i)
    return inside_polygons

# Performing ray casting for each point-polygon pair
for index, point in enumerate(points):
    inside_polygons = ray_casting(point, [list(polygon.exterior.coords) for polygon in polygons])
    
# end_time = timeit.default_timer()
# print("Execution time:", end_time - start_time, "seconds")