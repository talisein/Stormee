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

class HellowWorldGTK:
    """This is an Hello World GTK application"""

    def __init__(self):
        
        #Set the Glade file
        self.gladefile = "../glade/CAPViewer.glade"  
        self.wTree = gtk.glade.XML(self.gladefile) 
        
        #Get the Main Window, and connect the "destroy" event
        self.window = self.wTree.get_widget("mainWindow")
        if (self.window):
            self.window.connect("destroy", gtk.main_quit)


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

class Entry:
    def __init__(self):
        self.caplink = None
        self.fips = list()
        self.summary = None
        
    def addFips(self, fips):
        if len(fips) is 0:
            return
        elif ' ' in fips:
            for x in fips.split(' '):
                self.fips.append(x)
        else:
            self.fips.append(fips)

    def checkFips(self, fips):
        if fips in self.fips:
            return True
        else:
            return False

    def addCapLink(self, link):
        self.caplink = link
        
    def addSummary(self, summary):
        self.summary = summary
        
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
            for geocode in entry.findall('{urn:oasis:names:tc:emergency:cap:1.1}geocode'):
                for child in geocode.getchildren():
                    if child.tag.endswith('valueName'):
                        if child.text == 'FIPS6':
                            e.addFips(child.getnext().text)
                        else:
                            Log.warning("Unparsed geoCode of type %s" % child.text)
            if len(e.fips) is 0:
                Log.warning("Parsed zero geoCodes.")
            entries.append(e)
    return entries

def ReadCAP(file):
    alert = cap.Alert()
    
    parser = objectify.makeparser()
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
        alert.setNote(root.note)
        
    
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
    urls.append('http://alerts.weather.gov/cap/ca.php?x=0')
    urls.append('http://edis.oes.ca.gov/index.atom')
    urls.append('http://alerts.weather.gov/cap/ca.php?x=0')
    urls.append('http://earthquake.usgs.gov/eqcenter/recenteqsww/catalogs/caprss7days5.xml')
    rssfeed = urllib.urlopen('http://alerts.weather.gov/cap/ca.php?x=0') 
    window = Window()
    
    mycoords = (38.56513,-121.75156)
    #===========================================================================
    # alert = ReadCAP('../alert2.cap')
    # window.acceptCap(alert)
    # gtk.main()
    # sys.exit()
    #===========================================================================
    entries = feedParser(rssfeed)
  
    filtered = list()
    for entry in entries:
        if entry.checkFips('006113'):
            filtered.append(entry)


    for entry in filtered:
        
        alert = ReadCAP(entry.caplink)
        window.acceptCap(alert)

        if alert.checkArea('FIPS6','006113') or alert.checkArea('UGC','CAZ017'):
            n = pynotify.Notification(alert.infos[0].event, "<a href='%s'>Link</a>\n%s" % (entry.caplink, entry.summary))
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
    gtk.main()
