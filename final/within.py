# Does edge based indexing for the final candidate polygons.
# Finally, with the 2n x 2n bounding box for the point, perform a range query on the edge indexed R tree
# to check if the point is 'within n' distance from the polygon.
# Note that the edge of the polygon is not considered as inside
import rtree
from shapely.geometry import Point, Polygon, LineString
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

# Change values
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

# Change values
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

# Creating an R-tree index using the MBRs of the polygons
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

# Defining distance threshold
n = 4000

# Finding candidate polygons for each point
# We are interested in not_in_polygons
for index, point in enumerate(points):
    # Create 2n x 2n bounding box for point
    bbox = (point.x - n, point.y - n, point.x + n, point.y + n)
    intersected_polygons = [polygons[i] for i in idx.intersection(bbox)]
    candidate_polygons = [polygon for polygon in intersected_polygons if ray_casting(
        point, list(polygon.exterior.coords))]
    not_in_polygons = [
        polygon for polygon in intersected_polygons if polygon not in candidate_polygons]

   # Creating an R-tree index for each not-in-polygon
    for polygon in not_in_polygons:
        segments = [LineString([polygon.exterior.coords[i], polygon.exterior.coords[i+1]])
                    for i in range(len(polygon.exterior.coords) - 1)]
        edge_idx = rtree.index.Index()
        for i, segment in enumerate(segments):
            edge_idx.insert(i, segment.bounds)

        # Performing edge-based queries using the index
        intersections = [segment for segment in edge_idx.intersection(
            (point.x - n, point.y - n, point.x + n, point.y + n))]
        if intersections:
            print(
                f"Point {index} is within {n} from polygon {polygons.index(polygon)}")
        else:
            print(
                f"Point {index} is not within {n} from polygon {polygons.index(polygon)}")

for point in points:
    # Creating 2n x 2n bounding box for point
    bbox = (point.x - n, point.y - n, point.x + n, point.y + n)

    # Visualizing the bounding box
    x1, y1, x2, y2 = bbox
    plt.plot([x1, x1], [y1, y2], 'k-')
    plt.plot([x1, x2], [y2, y2], 'k-')
    plt.plot([x2, x2], [y2, y1], 'k-')
    plt.plot([x2, x1], [y1, y1], 'k-')

# Plotting the polygons
for i, poly in enumerate(polygons):
    plt.plot(*poly.exterior.xy)
    plt.annotate(str(i), [poly.centroid.x, poly.centroid.y], color='blue')

# Plotting the points
for i, point in enumerate(points):
    plt.plot(point.x, point.y, 'ro')
    plt.annotate(str(i), [point.x, point.y], color='red')
    
# end_time = timeit.default_timer()

# print("Execution time:", end_time - start_time, "seconds")

plt.show()


