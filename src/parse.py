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

 
class ReadCAP(saxutils.DefaultHandler):
    def __init__(self, summary):
        self.alert = cap.Alert()
        
        self.summary = summary
        self.inAlert = 0
        self.inIdentifier = 0
        self.inSender = 0
        self.inSent = 0
        self.inStatus = 0
        self.inMsgType = 0
        self.inScope = 0
        self.inNote = 0
        self.inReferences = 0
        self.inInfo = 0
        self.inCategory = 0
        self.inEvent = 0
        self.inUrgency = 0
        self.inSeverity = 0
        self.inCertainty = 0
        self.inEventCode = 0
        self.inValueName = 0
        self.inValue = 0
        self.inEffective = 0
        self.inExpires = 0
        self.inSenderName = 0
        self.inHeadline = 0
        self.inDescription = 0
        self.inInstruction = 0
        self.inParameter = 0
        self.inArea = 0
        self.inAreaDesc = 0
        self.inPolygon = 0
        self.inGeocode = 0
        self.inSame = 0
        self.inWmoHeader = 0
        self.inUgc = 0
        self.inVtec = 0
        self.inTml = 0
        self.inFips = 0
        self.inGeoUgc = 0
        self.inSource = 0
        self.inRestriction = 0
        self.inAddresses = 0
        self.inCode = 0
        self.inIncidents = 0
        self.inLanguage = 0
        self.inResponseType = 0
        self.inAudience = 0
        self.inOnset = 0
        self.inWeb = 0
        self.inContact = 0
        
        self.identifier = ""      
        self.sender = ""
        self.sent = ""
        self.msgType = ""
        self.msgType = ""
        self.scope = ""
        self.note = ""
        self.references = ""
        self.category = ""
        self.event = ""
        self.urgency = ""
        self.severity = ""
        self.certainty = "" 
        self.expires = ""
        self.senderName = ""
        self.headline = ""
        self.description = ""
        self.instruction = ""
        self.areaDesc = ""
        self.same = ""
        self.wmoHeader = ""
        self.ugc = ""
        self.vtec = ""
        self.tml = ""
        self.status = ""
        self.polygon = ""
        self.fipsgeocodes = set()
        self.ugcgeocodes = set()
        self.source = ""
        self.restriction = ""
        self.addresses = ""
        self.code = ""
        self.incidents = ""
        self.language = ""
        self.responseType = ""
        self.audience = ""
        self.onset = ""
        self.web = ""
        self.contact = ""
        
    def startElement(self, name, attrs):
        if name == 'alert':
            self.xmlns = attrs.get('xmlns')
            self.inAlert = 1
        elif name == 'identifier':
            self.inIdentifier = 1
        elif name == 'sender': 
            self.inSender = 1
        elif name == 'sent':
            self.inSent = 1
        elif name == 'status':
            self.inStatus = 1
        elif name == 'msgType':
            self.inMsgType = 1
        elif name == 'scope':
            self.inScope = 1
        elif name == 'note':
            self.inNote = 1
        elif name == 'references':
            self.inReferences = 1
        elif name == 'info':
            self.inInfo = 1
            self.info = cap.Info()
        elif name == 'category':
            self.inCategory = 1
            self.category = ""
        elif name == 'event':
            self.inEvent = 1
            self.event = ""
        elif name == 'urgency':
            self.inUrgency = 1
            self.urgency = ""
        elif name == 'severity':
            self.inSeverity = 1
            self.severity = ""
        elif name == 'certainty':
            self.inCertainty = 1
            self.certainty = ""
        elif name == 'eventCode':
            self.inEventCode = 1
        elif name == 'valueName':
            self.inValueName = 1
            self.valueName = ""
        elif name == 'value':
            self.inValue = 1
            self.value = ""
        elif name == 'effective':
            self.inEffective = 1
            self.effective = ""
        elif name == 'expires':
            self.inExpires = 1
            self.expires = ""
        elif name == 'senderName':
            self.inSenderName = 1
            self.senderName = ""
        elif name == 'headline':
            self.inHeadline = 1
            self.headline = ""
        elif name == 'description':
            self.inDescription = 1
            self.description = ""
        elif name == 'instruction':
            self.inInstruction = 1
        elif name == 'parameter':
            self.inParameter = 1
        elif name == 'area':
            self.inArea = 1
        elif name == 'areaDesc':
            self.inAreaDesc = 1
        elif name == 'polygon':
            self.inPolygon = 1
        elif name == 'geocode':
            self.inGeocode = 1
        elif name == 'source':
            self.inSource = 1
        elif name == 'restriction':
            self.inRestriction = 1
        elif name == 'addresses':
            self.inAddresses = 1
        elif name == 'code':
            self.inCode = 1
        elif name == 'incidents':
            self.inIncidents = 1
        elif name == 'language':
            self.inLanguage = 1
            self.language = ""
        elif name == 'responseType':
            self.inResponseType = 1
            self.responseType = ""
        elif name == 'audience':
            self.inAudience = 1
            self.audience = ""
        elif name == 'onset':
            self.inOnset = 1
            self.onset = ""
        elif name == 'web':
            self.inWeb = 1
            self.web = ""
        elif name == 'contact':
            self.inContact = 1
            self.contact = ""
        else:
            print 'Warning: Unknown Tag %s:\t%s' % (name, attrs.items())
 
    def characters(self, ch):
        if self.inIdentifier:
            self.identifier = self.identifier + ch
        elif self.inSender:
            self.sender = self.sender + ch
        elif self.inSent:
            self.sent = self.sent + ch
        elif self.inStatus:
            self.status = self.status + ch
        elif self.inMsgType:
            self.msgType = self.msgType + ch
        elif self.inScope:
            self.scope = self.scope + ch
        elif self.inNote:
            self.note = self.note + ch
        elif self.inReferences:
            self.references = self.references + ch
        elif self.inCategory:
            self.category = self.category + ch
        elif self.inEvent:
            self.event = self.event + ch
        elif self.inUrgency:
            self.urgency = self.urgency + ch
        elif self.inSeverity:
            self.severity = self.severity + ch
        elif self.inCertainty:
            self.certainty = self.certainty + ch
        elif self.inEventCode:
            if self.inValueName:
                self.valueName = self.valueName + ch
            elif self.inValue:
                self.value = self.value + ch
                if self.inSame:
                    self.same = self.same + ch
            else:
                if len(ch) > 1:
                    Log.warning("Unexpected text in CAP eventCode: %s" % ch)
        elif self.inEffective:
            self.effective = self.effective + ch
        elif self.inExpires:
            self.expires = self.expires + ch
        elif self.inSenderName:
            self.senderName = self.senderName + ch
        elif self.inHeadline:
            self.headline = self.headline + ch
        elif self.inDescription:
            self.description = self.description + ch
        elif self.inInstruction:
            self.instruction = self.instruction + ch
        elif self.inSource:
            self.source = self.source + ch
        elif self.inRestriction:
            self.restriction = self.restriction + ch
        elif self.inAddresses:
            self.addresses = self.addresses + ch
        elif self.inCode:
            self.code = self.code + ch
        elif self.inIncidents:
            self.incidents = self.incidents + ch
        elif self.inLanguage:
            self.language = self.language + ch
        elif self.inResponseType:
            self.responseType = self.responseType + ch
        elif self.inAudience:
            self.audience = self.audience + ch
        elif self.inOnset:
            self.onset = self.onset + ch
        elif self.inWeb:
            self.web = self.web + ch
        elif self.inContact:
            self.contact = self.contact + ch
        elif self.inParameter:
            if self.inValueName:
                self.valueName = self.valueName + ch
            elif self.inValue:
                self.value = self.value + ch
                if self.inWmoHeader:
                    self.wmoHeader = self.wmoHeader + ch
                elif self.inUgc:
                    self.ugc = self.ugc + ch
                elif self.inVtec:
                    self.vtec = self.vtec + ch
                elif self.inTml:
                    self.tml = self.tml + ch
        elif self.inArea:
            if self.inAreaDesc:
                self.areaDesc = self.areaDesc + ch
            elif self.inPolygon:
                # +38.18,-121.56 +38.13,-121.95 +39.73,-122.44 +40.45,-122.55 +40.62,-122.22 +39.13,-120.92 +38.13,-120.41 +37.85,-120.12 +37.28,-121.36 +38.18,-121.56
                self.polygon = self.polygon + ch
            elif self.inGeocode:
                if self.inValueName:
                    self.valueName = self.valueName + ch
                elif self.inValue:
                    self.value = self.value + ch
                    if self.inFips:
                        self.fipsgeocodes.add(ch)
                    elif self.inGeoUgc:
                        self.ugcgeocodes.add(ch)
     
    def endElement(self, name):
        if name == 'identifier':
            self.inIdentifier = 0
            self.alert.setId(self.identifier)
        elif name == 'alert':
            self.inAlert = 0
            self.alert.setVersion(self.xmlns)
        elif name == 'sender':
            self.inSender = 0
            self.alert.setSender(self.sender)
        elif name == 'sent':
            self.inSent = 0
            self.alert.setSent(self.sent)
        elif name == 'status':
            self.inStatus = 0
            self.alert.setStatus(self.status)
        elif name == 'msgType':
            self.inMsgType = 0
            self.alert.setMsgType(self.msgType)
        elif name == 'scope':
            self.inScope = 0
            self.alert.setScope(self.scope)
        elif name == 'note':
            self.inNote = 0
            self.alert.setNote(self.note)
        elif name == 'references':
            self.inReferences = 0
            self.alert.setReferences(self.references)
        elif name == 'info':
            self.inInfo = 0
            self.alert.addInfo(self.info)
        elif name == 'category':
            self.inCategory = 0
            self.info.addCategory(self.category)
        elif name == 'event':
            self.inEvent = 0
            self.info.setEvent(self.event)
        elif name == 'urgency':
            self.inUrgency = 0
            self.info.setUrgency(self.urgency)
        elif name == 'severity':
            self.inSeverity = 0
            self.info.setSeverity(self.severity)
        elif name == 'certainty':
            self.inCertainty = 0
            self.info.setCertainty(self.certainty)
        elif name == 'eventCode':
            self.inEventCode = 0
        elif name == 'valueName':
            self.inValueName = 0
            if self.valueName == 'SAME':
                self.inSame = 1
            elif self.inParameter:
                if self.valueName == 'WMOHEADER':
                    self.inWmoHeader = 1
                elif self.valueName == 'UGC':
                    self.inUgc = 1
                elif self.valueName == 'VTEC':
                    self.inVtec = 1
                elif self.valueName == 'TIME...MOT...LOC':
                    self.inTml = 1
                else:
                    print "Warning: Unknown parameter \"%s\"" % self.valueName
            elif self.inGeocode:
                if self.valueName == 'FIPS6':
                    self.inFips = 1
                elif self.valueName == 'UGC':
                    self.inGeoUgc = 1
                else:
                    print "Warning: Unknown geoCode \"%s\"" % self.valueName
            else:
                print "Warning: Unknown valueName \"%s\"" % self.valueName
 
        elif name == 'value':
            self.inValue = 0
            if self.inParameter:
                self.info.addParameter(self.valueName, self.value)
            if self.inEventCode:
                self.info.addEventCode(self.valueName, self.value)
            if self.inGeocode:
                if self.inFips:
                    self.fipsgeocodes.add(self.value)
                elif self.inGeoUgc:
                    self.ugcgeocodes.add(self.value)
            if self.inSame:
                self.inSame = 0
            if self.inWmoHeader:
                self.inWmoHeader = 0
            if self.inUgc:
                self.inUgc = 0
            if self.inVtec:
                self.inVtec = 0
            if self.inTml:
                self.inTml = 0
            if self.inFips:
                self.inFips = 0
            if self.inGeoUgc:
                self.inGeoUgc = 0
        elif name == 'effective':
            self.inEffective = 0
            self.info.setEffective(self.effective)
        elif name == 'expires':
            self.inExpires = 0
            self.info.setExpires(self.expires)
        elif name == 'senderName':
            self.inSenderName = 0
            self.info.setSenderName(self.senderName)
        elif name == 'headline':
            self.inHeadline = 0
            self.info.setHeadline(self.headline)
        elif name == 'description':
            self.inDescription = 0
            self.info.setDescription(self.description)
        elif name == 'instruction':
            self.inInstruction = 0
            self.info.setInstruction(self.instruction)
        elif name == 'parameter':
            self.inParameter = 0
        elif name == 'area':
            self.inArea = 0
        elif name == 'areaDesc':
            self.inAreaDesc = 0
        elif name == 'polygon':
            self.inPolygon = 0
        elif name == 'geocode':
            self.inGeocode = 0
        elif name == 'source':
            self.inSource = 0
            self.alert.setSource(self.source)
        elif name == 'restriction':
            self.inRestriction = 0
            self.alert.setRestriction(self.restriction)
        elif name == 'addresses':
            self.inAddresses = 0
            self.alert.setAddresses(self.addresses)
        elif name == 'code':
            self.inCode = 0
            self.alert.addCode(self.code)
        elif name == 'incidents':
            self.inIncidents = 0
            self.alert.setIncidents(self.incidents)
        elif name == 'language':
            self.inLanguage = 0
            self.info.setLanguage(self.language)
        elif name == 'responseType':
            self.inResponseType = 0
            self.info.addResponseType(self.responseType)
        elif name == 'audience':
            self.inAudience = 0
            self.info.setAudience(self.audience)
        elif name == 'onset':
            self.inOnset = 0
            self.info.setOnset(self.onset)
        elif name == 'web':
            self.inWeb = 0
            self.info.setWeb(self.web)
        elif name == 'contact':
            self.inContact = 0
            self.info.setContact(self.contact)
            


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
