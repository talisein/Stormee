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

import pygtk
pygtk.require('2.0')
import urllib2
from lxml import objectify
import logging 
import utils
import cap


MAX_ALERT_DISTANCE = 1000 # km.
Log = logging.getLogger()


class Entry:
    def __init__(self):
        self.caplink = None
        self.fips = list()
        self.summary = None
        self.coords = None
        self.polygon = None
        self.fromFeed = None
        
    def addFips(self, fips):
        if len(fips) is 0:
            return
        elif ' ' in fips:
            for x in fips.split(' '):
                self.fips.append(x)
        else:
            self.fips.append(fips)

    def checkFips(self, fips):
        '''
        fips: 5 digit string
        '''
        assert len(fips) is 5
        for fip in self.fips:
            assert len(fip) is 6
            if fip[1:6] == fips:
                return True
        return False
    
    def addCapLink(self, link):
        self.caplink = link
        
    def addSummary(self, summary):
        self.summary = summary
    
    def addCoords(self, coords):
        self.coords = coords
        
    def checkCoords(self, coords, kilos=MAX_ALERT_DISTANCE):
        if self.coords is not None: 
            return utils.distance(coords, self.coords) < kilos
        elif self.polygon is not None:
            x, y = coords
            return utils.point_inside_polygon(x, y, self.polygon)
        else:
            return False
    
    def addPoly(self, poly):
        self.polygon = poly
    
def feedParser(file):
    entries = list()
    try:
        feed = urllib2.urlopen(file)
    except:
        Log.error("Unexpected error fetching feed {0}.".format(file), exc_info=True)
        return entries
    
    try:
        tree = objectify.parse(feed)
    except:
        Log.error("Unexpected error parsing feed {0}.".format(file), exc_info=True)
        return entries

    
    try:
        root = tree.getroot()
        if hasattr(root, 'entry'):
            for entry in root.entry:
                e = Entry()
                e.fromFeed = str(file)
                if hasattr(entry, 'id'):
                    e.addCapLink(entry.id.text)
                if hasattr(entry, 'summary'):
                    e.addSummary(entry.summary.text.strip())
                elif hasattr(entry, 'title'):
                    e.addSummary(entry.title.text.strip())
                for geocode in entry.findall('{urn:oasis:names:tc:emergency:cap:1.1}geocode'):
                    for child in geocode.getchildren():
                        if child.tag.endswith('valueName'):
                            if child.text == 'FIPS6':
                                e.addFips(child.getnext().text)
                            else:
                                Log.warning("Unparsed geoCode of type %s" % child.text)
                for latLonBox in entry.findall('{http://www.alerting.net/namespace/index_1.0}latLonBox'):
                    c1, c2 = latLonBox.text.split(' ')
                    c1x, c1y = c1.split(',')
                    c2x, c2y = c2.split(',')
                    c1x = float(c1x)
                    c1y = float(c1y)
                    c2x = float(c2x)
                    c2y = float(c2y)
                    poly = list()
                    poly.append((c1x, c1y))
                    poly.append((c1x, c2y))
                    poly.append((c2x, c2y))
                    poly.append((c2x, c1y))
                    poly.append((c1x, c1y))
                    e.addPoly(poly)
                entries.append(e)
        elif hasattr(root, 'channel'):
            # USGS Earthquake feed
            for item in root.channel.item:
                e = Entry()
                e.addCapLink(item.link.text)
                e.addSummary(item.title.text)
                lat = item.find('{http://www.w3.org/2003/01/geo/wgs84_pos#}lat')
                long = item.find('{http://www.w3.org/2003/01/geo/wgs84_pos#}long')
                if lat is not None and long is not None:
                    lat = lat.text
                    long = long.text
                else:
                    Log.warning("Feed {0} has entry '{1}' with no geographical focus. Skipping the entry.".format(file, item.title.text))
                    continue
                e.addCoords((float(lat), float(long)))
                entries.append(e)
        else:
            Log.warning("Unable to find valid root element of feed {0}. Skipping this feed.".format(file))
        return entries
    except AttributeError:
        Log.error("Feed {0} missing expected field.".format(file), exc_info=True)
        return entries
    except:
        Log.error("Unexpected error parsing feed {0}".format(file), exc_info=True)
        return entries
    
def ReadCAP(file):
    alert = cap.Alert()
    

    try:
        feed = urllib2.urlopen(file)
    except ValueError:
        Log.warning("Input '{0}' not a valid url type. Assuming it is a filename.".format(file))
        feed = file
    except:
        Log.error("Unexpected error fetching CAP {0}".format(file), exc_info=True)

    try:
        parser = objectify.makeparser()
        tree = objectify.parse(feed, parser)
    except:
        Log.error("Unexpected error parsing CAP {0}".format(file), exc_info=True)
        return None
    
    try:
        root = tree.getroot()
        assert root.tag.endswith('alert')
        alert.setId(root.identifier.text)
        alert.setSender(root.sender.text)
        alert.setSent(root.sent.text)
        alert.setStatus(root.status.text)
        alert.setMsgType(root.msgType.text)
    
        if hasattr(root, 'source'):
            alert.setSource(root.source)
            Log.debug("Got alert.source %s" % root.source.text)
        alert.setScope(root.scope.text)
        if hasattr(root, 'restriction'):
            alert.setRestriction(root.restriction.text)
            Log.debug("Got alert.restriction %s" % root.restriction.text)
        if hasattr(root, 'addresses'):
            alert.setAddresses(root.addresses.text)
            Log.debug("Got alert.addresses %s" % root.addresses.text)
        if hasattr(root, 'code'):
            for x in root.code:
                alert.addCode(x.text)
        if hasattr(root, 'references'):
            alert.setReferences(root.references.text)
        if hasattr(root,'incidents'):
            alert.setIncidents(root.incidents.text)
        if hasattr(root,'note'):
            alert.setNote(root.note.text)
            
        
        for info in root.info:
            i = cap.Info()
            if hasattr(info, 'language'):
                i.setLanguage(info.language.text)
            for category in info.category:
                i.addCategory(category.text)
            i.setEvent(info.event.text)
            if hasattr(info, 'responseType'):
                for x in info.responseType:
                    i.addResponseType(x.text)
            i.setUrgency(info.urgency.text)
            i.setSeverity(info.severity.text)
            i.setCertainty(info.certainty.text)
            if hasattr(info, 'audience'):
                i.setAudience(info.audience.text)
            if hasattr(info, 'eventCode'):
                for x in info.eventCode:
                    i.addEventCode(x.valueName.text, x.value.text)
            if hasattr(info, 'effective'):
                i.setEffective(info.effective.text)
            else:
                i.setEffective(root.sent.text)
            if hasattr(info, 'onset'):
                i.setOnset(info.onset.text)
            if hasattr(info, 'expires'):
                i.setExpires(info.expires.text)
            else:
                i.setDefaultExpires()    
                Log.info("No expiration for CAP %s. Assuming 24 hours." % alert.id)
            if hasattr(info, 'senderName'):
                i.setSenderName(info.senderName.text)
            if hasattr(info, 'headline'):
                i.setHeadline(info.headline.text)
            if hasattr(info, 'description'):
                i.setDescription(info.description.text)
            if hasattr(info, 'instruction'):
                i.setInstruction(info.instruction.text)
            if hasattr(info, 'web'):
                i.setWeb(info.web.text)
            if hasattr(info, 'contract'):
                i.setContact(info.contract.text)
            if hasattr(info, 'parameter'):
                for parameter in info.parameter:
                    if hasattr(parameter, 'valueName'):
                        if parameter.valueName.text is not None:
                            if parameter.valueName.text.count('VTEC'):
                                i.setVTEC(parameter.value.text)
                            else:
                                i.addParameter(parameter.valueName.text, parameter.value.text)
                    else:
                        # is this a USGS feed?
                        if parameter.text.count('=') is 1:
                            valueName, value = parameter.text.split('=')
                            if valueName.count('VTEC'):
                                i.setVTEC(value)
                            else:   
                                i.addParameter(valueName, value)
                        else:
                            Log.error("Error parsing parameter {0}".format(parameter.text))
            if hasattr(info, 'resource'):
                for resource in info.resource:
                    res = cap.Resource()
                    res.setResourceDesc(resource.resourceDesc.text)
                    res.setMimeType(resource.mimeType.text)
                    if hasattr(resource, 'size'):
                        res.setSize(resource.size.text)
                    if hasattr(resource, 'uri'):
                        res.setUri(resource.uri.text)
                    if hasattr(resource, 'derefUri'):
                        res.setDerefUri(resource.derefUri.text)
                    if hasattr(resource, 'digest'):
                        res.setDigest(resource.digest.text)
                    i.addResource(res)
            
            if hasattr(info, 'area'):
                for area in info.area:
                    a = cap.Area()
                    a.setAreaDesc(area.areaDesc.text)
                    if hasattr(area, 'polygon'):
                        for polygon in area.polygon:
                            a.addPolygon(polygon.text)
                    if hasattr(area, 'circle'):
                        for circle in area.circle:
                            a.addCircle(circle.text)
                    if hasattr(area, 'geocode'):
                        for geocode in area.geocode:
                            a.addGeoCode(geocode.valueName.text, geocode.value.text)
                    if hasattr(area, 'altitude'):
                        a.setAltitude(area.altitude.text)
                    if hasattr(area, 'ceiling'):
                        a.setCeiling(area.ceiling.text)    
                    i.addArea(a)
            alert.addInfo(i)
        return alert
    except AttributeError:
        Log.error("CAP {0} missing required field.".format(file), exc_info=True)
        return None
    except:
        Log.error("Unexpected error parsing CAP {0}".format(file), exc_info=True)
        return None
