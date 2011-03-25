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
import gtk
import pynotify
import urllib
import cap
import sys, os
import logging 
from lxml import etree
from lxml import objectify
import inspect
import glineenc as polylines
import gtk
import gtk.glade
from window import Window
import utils

MAX_ALERT_DISTANCE = 1000 # km.
Log = logging.getLogger()
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
Log.addHandler(ch)
Log.setLevel(logging.DEBUG)

class HelloTray:

    def __init__(self):
        self.statusIcon = gtk.StatusIcon()
        self.statusIcon.set_from_stock(gtk.STOCK_ABOUT)
        self.statusIcon.set_visible(True)
        self.statusIcon.set_tooltip("Hello World")
        
        self.menu = gtk.Menu()
        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_EXECUTE)
        self.menuItem.connect('activate', self.execute_cb, self.statusIcon)
        self.menu.append(self.menuItem)
        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.menuItem.connect('activate', self.quit_cb, self.statusIcon)
        self.menu.append(self.menuItem)
        
        self.statusIcon.connect('popup-menu', self.popup_menu_cb, self.menu)
        self.statusIcon.set_visible(1)
        
        gtk.main()
    
    def execute_cb(self, widget, event, data=None):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_border_width(10)
        
        button = gtk.Button("Hello World")
        button.connect_object("clicked", gtk.Widget.destroy, window)
        
        window.add(button)
        button.show()
        window.show()
    
    def quit_cb(self, widget, data=None):
        gtk.main_quit()
    
    def popup_menu_cb(self, widget, button, time, data=None):
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, gtk.status_icon_position_menu, 3, time, self.statusIcon)

class Entry:
    def __init__(self):
        self.caplink = None
        self.fips = list()
        self.summary = None
        self.coords = None
        self.polygon = None
        
    def addFips(self, fips):
        if len(fips) is 0:
            return
        elif ' ' in fips:
            for x in fips.split(' '):
                self.fips.append(x)
        else:
            self.fips.append(fips)

    def checkFips(self, fips):
        return fips in self.fips
    
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
    tree = objectify.parse(file)
    root = tree.getroot()
    entries = list()
    
    if hasattr(root, 'entry'):
        for entry in root.entry:
            e = Entry()
            if hasattr(entry, 'id'):
                e.addCapLink(entry.id.text)
            if hasattr(entry, 'summary'):
                e.addSummary(entry.summary.text)
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
            lat = item.find('{http://www.w3.org/2003/01/geo/wgs84_pos#}lat').text
            long = item.find('{http://www.w3.org/2003/01/geo/wgs84_pos#}long').text
            e.addCoords((float(lat), float(long)))

            entries.append(e)
    return entries

def ReadCAP(file):
    alert = cap.Alert()
    
    parser = objectify.makeparser()
    try:
        tree = objectify.parse(file, parser)
        
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
                    try:
                        i.addParameter(parameter.valueName.text, parameter.value.text)
                    except AttributeError:
                        # is this a USGS feed?
                        if parameter.text.count('=') is 1:
                            valueName, value = parameter.text.split('=')
                            i.addParameter(valueName, value)
                        else:
                            raise
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
                    else:
                        Log.debug("No polygon")
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
    except etree.XMLSyntaxError as e:
        Log.error("Broken link %s" % file) 
#    print etree.tostring(tree['alert'], pretty_print=True)

if __name__ == '__main__':
    urls = list()
    urls.append('http://alerts.weather.gov/cap/ca.php?x=0')
    urls.append('http://edis.oes.ca.gov/index.atom')
    urls.append('http://alerts.weather.gov/cap/ca.php?x=0')
    urls.append('http://earthquake.usgs.gov/eqcenter/recenteqsww/catalogs/caprss7days5.xml')
    rssfeed = urllib.urlopen('http://edis.oes.ca.gov/index.atom') 
    window = Window()
    
    mycoords = (38.56513,-121.75156)
 #   mycoords = (-15,-171)
    #===========================================================================
    # file = open('../alert3.cap')
    # alert = ReadCAP(file)
    # window.acceptCap(alert)
    # gtk.main()
    # sys.exit()
    #===========================================================================
    entries = feedParser(rssfeed)
  
    filtered = list()
    for entry in entries:
        if entry.checkFips('006113'):
            filtered.append(entry)
        if entry.checkCoords(mycoords):
            filtered.append(entry)

    
    #===========================================================================
    # filtered = list()
    # a = Entry()
    # a.addCoords(mycoords)
    # a.addCapLink('../alert3.cap')
    # a.addSummary('Testing only')
    # filtered.append(a)
    #===========================================================================
    for entry in filtered:
        
        alert = ReadCAP(entry.caplink)
        if alert is None:
            continue
        
        if alert.checkArea('FIPS6','006113') or alert.checkArea('UGC','CAZ017') or alert.checkCoords(mycoords):
            window.acceptCap(alert)
            if alert.infos[0].description is None:
                continue
            if alert.infos[0].event is None:
                alert.infos[0].event = "UNTITLED EVENT"
            n = pynotify.Notification(alert.infos[0].event, "<a href='%s'>Link</a>\n%s" % (entry.caplink, alert.infos[0].description[0:400]))
            n.set_urgency(pynotify.URGENCY_NORMAL)
            #n.set_timeout(0)
            n.set_category("device")
            helper = gtk.Button()
     
        
            if alert.infos[0].severity is cap.Info.SEVERITY_MODERATE:
                i = gtk.STOCK_DIALOG_WARNING
            elif alert.infos[0].severity is cap.Info.SEVERITY_MINOR:
                i = gtk.STOCK_DIALOG_INFO
            elif alert.infos[0].severity is cap.Info.SEVERITY_SEVERE or alert.infos[0].severity is cap.Info.SEVERITY_EXTREME:
                i = gtk.STOCK_DIALOG_ERROR
            else:
                i = gtk.STOCK_DIALOG_QUESTION
            
            icon = helper.render_icon(i, gtk.ICON_SIZE_DIALOG)
            n.set_icon_from_pixbuf(icon)
            
            #n.show()
    gtk.main()
