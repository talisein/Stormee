# -*- coding: utf-8 -*-
#
#    Copyright (C) 2011 Andrew G. Potter
#    This file is part of the GNOME Common Alerting Protocol Viewer.
# 
#    GNOME Common Alerting Protocol Viewer is free software: you can r
#    edistribute it and/or modify it under the terms of the GNU General 
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

from xml.sax import saxutils
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces
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


class ReadRSS(saxutils.DefaultHandler):
    def __init__(self):
        self.inGeocode = 0
        self.inValueName = 0
        self.inValue = 0
        self.inFips = 0
        self.link = ""
        self.value = ""
        self.valueName = ""
        self.geocodes = set()
        self.caps = list()
        self.summary = ""
        self.inSummary = 0

    def startElement(self, name, attrs):
        if name == 'link':
            self.link = attrs.get('href')
        elif name == "cap:geocode":
            self.inGeocode = 1
        elif name == "valueName":
            self.inValueName = 1
            self.valueName = ""
        elif name == "value":
            self.inValue = 1
            self.value = ""
        elif name == 'entry':
            self.geocodes = set()
            self.link = ""
        elif name == 'summary':
            self.inSummary = 1
            self.summary = ""

    def characters(self, ch):
        if self.inGeocode:
            if self.inValueName:
                self.valueName = self.valueName + ch
            elif self.inValue:
                self.value = self.value + ch
        elif self.inSummary:
            self.summary = self.summary + ch

    def endElement(self, name):
        if name == 'entry':
            if '006113' in self.geocodes:
                self.caps.append((self.link, self.summary))
        elif name == "cap:geocode":
            self.inGeocode = 0
        elif name == "valueName":
            self.inValueName = 0
            if self.valueName == "FIPS6":
                self.inFips = 1
        elif name == "value":
            if self.inFips:
                self.inFips = 0
                for x in self.value.split(' '):
                    self.geocodes.add(x)
        elif name == "summary":
            self.inSummary = 0

def moreInfo_cb(n, action, zzz):
    print "ID: %s" % zzz.identifier
    print "Sender: %s" % zzz.sender
    print "Sent: %s" % zzz.sent
    print "Status: %s" % zzz.status
    print "MsgType: %s" % zzz.msgType
    print "Scope: %s" % zzz.scope
    print "Note: %s" % zzz.note
    print "References: %s" % zzz.references
    print "Severity: %s" % zzz.severity
    print "Certainty: %s" % zzz.certainty
    print "SAME: %s" % zzz.same
    print "Headline: %s" % zzz.headline
    print "Description: %s" % zzz.description
    print "Instruction: %s" % zzz.instruction
    print "UGC: %s" % zzz.ugc
    print "Vtec: %s" % zzz.vtec
    print "TML: %s" % zzz.tml
    print "Effective: %s" % zzz.effective
    print "Expires: %s" % zzz.expires
    print "AreaDesc: %s" % zzz.areaDesc
    n.close()

def secondParser(file):
    alert = cap.Alert()
    
    schemafile = open('/home/talisein/waether/CAP-v1.1.xsd')
    schema = etree.XMLSchema(file=schemafile)
    parser = objectify.makeparser(remove_blank_text=True, schema=schema)
#    parser = etree.XMLParser(remove_blank_text=True)
    tree = objectify.parse(file, parser)
    
    root = tree.getroot()
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
            Log.debug("Got alert.code %s" % x.text)
    if hasattr(root, 'references'):
        alert.setReferences(root.references.text)
        Log.debug("Got alert.references %s" % root.references.text)
    if hasattr(root,'incidents'):
        alert.setIncidents(root.incidents.text)
        Log.debug("Got alert.incidents %s" % root.incidents.text)
    
    
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
                i.addParameter(parameter.valueName.text, parameter.value.text)
        
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
                
#    print etree.tostring(tree['alert'], pretty_print=True)

if __name__ == '__main__':
    urls = list()
    urls.append('http://edis.oes.ca.gov/index.atom')
    urls.append('http://alerts.weather.gov/cap/ca.php?x=0')
    urls.append('http://earthquake.usgs.gov/eqcenter/recenteqsww/catalogs/caprss7days5.xml')
    rssfeed = urllib.urlopen('http://alerts.weather.gov/cap/ca.php?x=0') 
    
    # Create a parser
    rssparser = make_parser()
    
    # Tell the parser we are not interested in XML namespaces
    rssparser.setFeature(feature_namespaces, 0)
    
    # Create the handler
    rss = ReadRSS()
    
    # Tell the parser to use our handler
    rssparser.setContentHandler(rss)
    
    rssparser.parse(rssfeed)
    rss.caps.reverse()

    for (caplink, capsummary) in rss.caps:
        
        alert = secondParser(caplink)
        
        if alert.checkArea('FIPS6','006113') or alert.checkArea('UGC','CAZ017'):
            n = pynotify.Notification(alert.infos[0].event, "<a href='%s'>Link</a>\n%s" % (caplink, capsummary))
            n.set_urgency(pynotify.URGENCY_NORMAL)
            n.set_timeout(0)
            n.set_category("device")
            helper = gtk.Button()
     
        
            if alert.infos[0].severity is cap.Info.SEVERITY_MODERATE:
                i = gtk.STOCK_DIALOG_WARNING
            elif alert.infos[0].severity is cap.Info.SEVERITY_MINOR:
                i = gtk.STOCK_DIALOG_INFO
            elif alert.infos[0].severity is cap.Info.SEVERITY_SEVERE:
                i = gtk.STOCK_DIALOG_ERROR
            else:
                i = gtk.STOCK_DIALOG_QUESTION
            
            icon = helper.render_icon(i, gtk.ICON_SIZE_DIALOG)
            n.set_icon_from_pixbuf(icon)
            
            n.add_action("more info", "More Info", moreInfo_cb, user_data=alert)
            n.show()
