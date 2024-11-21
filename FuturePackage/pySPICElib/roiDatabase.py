import math
import numpy as np
from shapely.geometry import Polygon
import spiceypy as spice

# vertices can be a np.array with a vertex in each row; with lon and lat
# or a list with 4 numbers: loncenter, sizelon, latcenter, sizelat
class roi:
    def __init__(self, body, name, vertices):
        self.body = body
        self.name = name
        if isinstance(vertices, np.ndarray): #array of vertices
            self.vertices = vertices
        else:
            if not isinstance(vertices,list):
                raise Exception('vertices must be a list 4 doubles or a numpy array')
            lonc  = vertices[0]
            lonsz = vertices[1]
            latc  = vertices[2]
            latsz = vertices[3]
            self.vertices=np.array( [[lonc-lonsz/2., latc-latsz/2],
                                     [lonc+lonsz/2, latc-latsz/2],
                                     [lonc+lonsz/2., latc+latsz/2],
                                     [lonc-lonsz/2, latc+latsz/2]] )

        cc = Polygon(self.vertices).centroid.xy
        self.centroid = [cc[0][0],cc[1][0]]
        rr=spice.bodvrd(self.body,'RADII',3)
        lon,lat = zip(*self.vertices)
        a=rr[1][0]
        b=rr[1][2]
        print(a)
        print(b)
        print(lon)
        print(lat)

        self.area=self.areaint(a,b,lat,lon)

    def print(self):
        print('ROI: /',self.body,'/',self.name,' centroid=',self.centroid,' area=',self.area,'km^2')

    def areaint(self,a, b, lat, lon):
        if isinstance(lat, tuple):
            lat = list(lat)
        if isinstance(lon, tuple):
            lon = list(lon)

        if lat[-1] != lat[0] or lon[-1] != lon[0]:
            lat.append(lat[0])
            lon.append(lon[0])
        # Same as Matlab areaint. For the moment only custom ellipsoids and degrees as units are accepted
        e = math.sqrt(1 - (b ** 2) / (a ** 2))
        # 1. Transform latitudes and longitudes to radians

        lat = [np.radians(latcoord) for latcoord in lat]
        lon = [np.radians(loncoord) for loncoord in lon]

        # 2. Transform geodetic to authalic latitudes
        fact1 = e ** 2 / 3 + 31 * e ** 4 / 180 + 59 * e ** 6 / 560
        fact2 = 17 * e ** 4 / 360 + 61 * e ** 6 / 1260
        fact3 = 383 * e ** 6 / 45360

        authlat = [
            latcoord - fact1 * math.sin(2 * latcoord) + fact2 * math.sin(4 * latcoord) - fact3 * math.sin(6 * latcoord) for
            latcoord in lat]

        # 3. Get authalic radius
        if e > 0:
            f1 = a ** 2 / 2
            f2 = (1 - e ** 2) / (2 * e)
            f3 = math.log((1 + e) / (1 - e))
            authRad = math.sqrt(f1 * (1 + f2 * f3))
        else:
            authRad = a

        # 5. Initialize origin (arbitrary) coordinates
        lat0 = 0.
        lon0 = 0.

        colat = []
        az = []

        for latcoords, loncoords in zip(authlat, lon):
            if lat0 <= -np.pi / 2 or latcoords >= np.pi / 2:
                a = 0.
            elif latcoords <= -np.pi / 2 or lat0 >= np.pi / 2:
                a = np.pi
            else:
                a = math.atan2(math.cos(latcoords) * math.sin(loncoords - lon0),
                               math.cos(lat0) * math.sin(latcoords) - math.sin(lat0) * math.cos(latcoords) * math.cos(
                                   loncoords - lon0))

            a = a % (2 * np.pi)

            az.append(a)

            r = 1
            b = math.sin((latcoords - lat0) / 2) ** 2 + math.cos(lat0) * math.cos(latcoords) * math.sin(
                (loncoords - lon0) / 2.) ** 2
            if b < 0:
                b = 0
            elif b > 1:
                b = 1
            colat.append(r * 2 * math.atan2(math.sqrt(b), math.sqrt(1 - b)))

        daz = np.diff(np.array(az))
        for i in range(len(daz)):
            daz[i] = (daz[i] + np.pi) % (2 * np.pi) - np.pi

        deltas = np.diff(colat) / 2
        colat.pop()
        colat = np.array(colat) + deltas

        integrands = []

        for i in range(len(colat)):
            integrands.append((1 - math.cos(colat[i])) * daz[i])
        area = np.abs(sum(integrands)) / (4 * np.pi)
        area = min(area, 1 - area)
        return area * 4 * np.pi * authRad ** 2
