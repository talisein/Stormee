# -*- coding: utf-8 -*-
#
#    Copyright (C) 2011 Andrew G. Potter
#    This file is part of the GNOME Common Alerting Protocol Viewer.
# 
#    GNOME Common Alerting Protocol Viewer is free software: you can
#    redistribute it and/or modify it under the terms of the GNU General 
#    Public License as published by the Free Software Foundation, either 
#    version 3 of the License, or (at your option) any later version.
# 
#    GNOME Common Alerting Protocol Viewer is distributed in the hope 
#    that it will be useful, but WITHOUT ANY WARRANTY; without even the 
#    implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
#    PURPOSE.  See the    GNU General Public License for more details.
# 
#    You should have received a copy of the GNU General Public License
#    along with GNOME Common Alerting Protocol Viewer.  
#    If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import logging
Log = logging.getLogger()
import glineenc as polylines
import math

def point_inside_polygon(x,y,poly):
    '''
    Credit: http://www.ariel.com.au/a/python-point-int-poly.html
    '''
    
    n = len(poly)
    inside =False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside


def mapPolygon(polygon, markerCoords='38.56513,-121.75156'):
    (farin, farout) = polylines.encode_pairs(polygon)
    baselink = 'http://maps.google.com/maps/api/staticmap?size=800x600&sensor=false'
    markerlink = '&markers=' + markerCoords
    pathlink = '&path=color:0x0000ff|weight:5|enc:'
    Log.debug(baselink +markerlink + pathlink + farin)
    return baselink + markerlink + pathlink + farin


def mapCircle(circle, markerCoords='38.56513,-121.75156'):
    x, y, radius = circle
    
    baselink = 'http://maps.google.com/maps/api/staticmap?size=800x600&sensor=false'
    markerlink = '&markers=' + markerCoords + '|' + str(x) + ',' + str(y)
    pathlink = '&path=color:0x0000ff|weight:5|enc:'
    lat = y
    lng = x
    d2r = 3.14159 / 180
    r2d = 180/3.14159
    clat = radius/6371 * r2d
    clng = clat/math.cos(lat*d2r)
    poly = list()
    for z in range(20):
        theta = 3.14159 * (float(z) / 10)
        Cx = lng + (clng * math.cos(theta))
        Cy = lat + (clat * math.sin(theta))
        poly.append((Cx,Cy))
    poly.append(poly[0])
    (farin, farout) = polylines.encode_pairs(poly)

    Log.debug(baselink +markerlink + pathlink + farin)
    return baselink + markerlink + pathlink + farin

def distance(origin, destination):
    '''
    Haversine formula example in Python
    Author: Wayne Dyck
    '''
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d
