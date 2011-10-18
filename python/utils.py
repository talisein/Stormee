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

import math
import logging
Log = logging.getLogger()

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


def mapPolygon(polygon, markerCoords='38.56513, -121.75156', areaDesc=' ', markerTitle=' '):
    p1 = open('html/poly1.html').read().replace('ORIGIN', markerCoords).replace('MARKER_TITLE',markerTitle)
    for x in range(len(polygon)):
        if x is not len(polygon) - 1:
            lat, long = polygon[x]
            p1 +='new google.maps.LatLng(' + str(lat) + ', ' + str(long) + '),\n'
        else:
            p1 +='new google.maps.LatLng(' + str(lat) + ', ' + str(long) + ')\n'
    p1 += open('html/poly2.html').read().replace('INFOWINDOW_CONTENT',str(areaDesc).strip().replace("\n",'<br />'))
    return p1


def mapCircle(circle, markerCoords='38.56513,-121.75156', areaDesc=' ', markerTitle=' '):
    x, y, radius = circle
    radius = radius * 1000 # meters
    p1 =  open('html/circle1.html').read().replace('ORIGIN', markerCoords).replace('RADIUSMETERS', str(radius)).replace('CENTER', str(x) + ', ' + str(y).replace('MARKER_TITLE',markerTitle))
    p1.replace('INFOWINDOW_CONTENT',areaDesc.strip().replace("\n",'<br /'))
    
    return p1

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
