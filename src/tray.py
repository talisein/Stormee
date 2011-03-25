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

import gobject
import gtk
import pygtk
pygtk.require("2.0")

import pynotify
import datetime
import logging
import parse
import cap
from window import Window

Log = logging.getLogger()


LATLONG_COORDS = (38.56513,-121.75156)
FIPSCODE = '006113'
UGCCODE = 'CAZ017'

class CAPTray:

    def __init__(self):
        self.caps = dict()
        self.rssfeeds = set()
        self.seen = set()

        self.rssfeeds.add('http://alerts.weather.gov/cap/ca.php?x=0')
        self.rssfeeds.add('http://edis.oes.ca.gov/index.atom')
        self.rssfeeds.add('http://earthquake.usgs.gov/eqcenter/recenteqsww/catalogs/caprss7days5.xml')
        self.mycoords = LATLONG_COORDS
        
        self.statusIcon = gtk.StatusIcon()
        self.statusIcon.set_from_stock(gtk.STOCK_DIALOG_WARNING)
        self.statusIcon.set_visible(True)
        self.statusIcon.set_tooltip("Common Alerting Protocol Viewer")
        
        self.menu = gtk.Menu()
        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_EXECUTE)
        self.menuItem.connect('activate', self.execute_cb, self.statusIcon)
        self.menu.append(self.menuItem)
        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.menuItem.connect('activate', self.quit_cb, self.statusIcon)
        self.menu.append(self.menuItem)
        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_CONNECT)
        self.menuItem.connect('activate', self.rssTimer_cb, self.statusIcon)
        
        self.statusIcon.connect('popup-menu', self.popup_menu_cb, self.menu)
        self.statusIcon.set_visible(1)

        gobject.timeout_add_seconds(60*10, self.rssTimer_cb)
        gobject.timeout_add(100, self.startup_cb)
    
    def execute_cb(self, widget, event, data=None):
        window = Window()
        for cap in self.caps:
            window.acceptCap(self.caps[cap])
    
    def quit_cb(self, widget, data=None):
        gtk.main_quit()

    def startup_cb(self):
        self.rssTimer_cb(True)
        return False
    
    def rssTimer_cb(self, isInitial=False):
        Log.debug("Hitting up RSS Feeds at %s" % datetime.datetime.now())
        entries = list()
        for rssfeed in self.rssfeeds:
            entries.extend(filter(lambda entry: entry.caplink not in self.seen, parse.feedParser(rssfeed)))
        
        for newEntry in entries:
            self.seen.add(newEntry.caplink)
            if newEntry.checkFips(FIPSCODE) or newEntry.checkCoords(LATLONG_COORDS):
                Log.debug("New alert from feed %s: %s" % (newEntry.fromFeed, newEntry.summary))
                alert = parse.ReadCAP(newEntry.caplink)
                if alert is None:
                    continue
                
                if alert.checkArea('FIPS6',FIPSCODE) or alert.checkArea('UGC',UGCCODE) or alert.checkCoords(LATLONG_COORDS):
                    if not alert.isExpired():
                        self.caps[newEntry.caplink] = alert
                        if not isInitial:
                            if len(alert.infos) is 0:
                                Log.debug("Alert %s had no info." % alert.id)
                                continue
                            if alert.infos[0].description is None:
                                alert.infos[0].description = "NO DESCRIPTION"
                            if alert.infos[0].event is None:
                                alert.infos[0].event = "UNTITLED EVENT"
                            n = pynotify.Notification(alert.infos[0].event, "<a href='%s'>Link</a>\n%s" % (newEntry.caplink, alert.infos[0].description[0:120]))
                            n.set_urgency(pynotify.URGENCY_NORMAL)
                            n.set_category("device")
                        
                            if alert.infos[0].severity is cap.Info.SEVERITY_MODERATE:
                                i = gtk.STOCK_DIALOG_WARNING
                            elif alert.infos[0].severity is cap.Info.SEVERITY_MINOR:
                                i = gtk.STOCK_DIALOG_INFO
                            elif alert.infos[0].severity is cap.Info.SEVERITY_SEVERE or alert.infos[0].severity is cap.Info.SEVERITY_EXTREME:
                                i = gtk.STOCK_DIALOG_ERROR
                            else:
                                i = gtk.STOCK_DIALOG_QUESTION
                            helper = gtk.Button()
                            icon = helper.render_icon(i, gtk.ICON_SIZE_DIALOG)
                            n.set_icon_from_pixbuf(icon)
                            
                            n.show()
        Log.debug("Done checking RSS feeds at %s" % datetime.datetime.now())
        self.ejectExpired()
        return True
    
    def ejectExpired(self):
        for cap in self.caps:
            if self.caps[cap].isExpired():
                self.caps.pop(cap)

    def popup_menu_cb(self, widget, button, time, data=None):
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, gtk.status_icon_position_menu, 3, time, self.statusIcon)
