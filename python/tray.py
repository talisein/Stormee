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
import heapq

import pynotify
import logging
import parse
import cap
from window import Window


Log = logging.getLogger()


LATLONG_COORDS = (38.56513,-121.75156)
STATECODE = 'CA'
FIPSCODE = '06113'
UGCCODE = '017'

class CAPTray:

    def __init__(self):
        self.caps = []
        self.rssfeeds = set()
        self.seen = set()
        self.windows = list()

#        self.rssfeeds.add('http://www.usgs.gov/hazard_alert/alerts/landslides.rss')

#        self.rssfeeds.add('http://alerts.weather.gov/cap/ca.php?x=0')
        self.rssfeeds.add('http://edis.oes.ca.gov/index.atom')
#        self.rssfeeds.add('http://earthquake.usgs.gov/eqcenter/recenteqsww/catalogs/caprss7days5.xml')
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
    
	self.execute_cb(None, None, None)

    def execute_cb(self, widget, event, data=None):
        window = Window(self)
        self.windows.append(window)
        
        localcaps = list(self.caps)
        for i in range(len(localcaps)):
            window.acceptCap(heapq.heappop(localcaps))
    
    def window_quit_cb(self, window):
        self.windows.remove(window)
    
    def quit_cb(self, widget, data=None):
        gtk.main_quit()

    def startup_cb(self):
        self.rssTimer_cb(True)
        return False
    
    def rssTimer_cb(self, isInitial=False):
        Log.info("Hitting up RSS Feeds.")
        entries = list()
        for rssfeed in self.rssfeeds:
            entries.extend(filter(lambda entry: entry.caplink not in self.seen, parse.feedParser(rssfeed)))
        
        for newEntry in entries:
            self.seen.add(newEntry.caplink)
            if newEntry.checkFips(FIPSCODE) or newEntry.checkCoords(LATLONG_COORDS) or True:
                Log.info("New alert from feed {0}: {1}".format(newEntry.fromFeed, newEntry.summary))
                alert = parse.ReadCAP(newEntry.caplink)
                if alert is None:
                    continue
                
                if alert.checkUGC(STATECODE, FIPSCODE, UGCCODE) or alert.checkCoords(LATLONG_COORDS) or alert.checkArea('FIPS6', '000000') or True:
                    if not alert.isExpired():
                        heapq.heappush(self.caps,alert)
                        for window in self.windows:
                            window.acceptCap(alert)
                            
                        if not isInitial:
                            if len(alert.infos) is 0:
                                Log.debug("Alert %s had no info." % alert.id)
                                continue
                            if alert.infos[0].description is None:
                                alert.infos[0].description = "NO DESCRIPTION"
                            if not pynotify.is_initted():
                                pynotify.init("GNOME Common Alerting Protocol Viewer")
                            n = pynotify.Notification(alert.getTitle(), "<a href='{0}'>Link</a>\n{1}".format(alert.url, alert.infos[0].description[0:120]))
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
                    else:
                        Log.info("... but it is already expired.")
        Log.info("Done checking RSS feeds.")
        self.ejectExpired()
#        self.caps['Testing 1'] = parse.ReadCAP('../alert.cap')
#        self.caps['Testing 2'] = parse.ReadCAP('../alert2.cap')
#        self.caps['Testing 3'] = parse.ReadCAP('../alert3.cap')
#        self.caps['Testing 4'] = parse.ReadCAP('../alert4.cap')
        return True
    
    def ejectExpired(self):
        for cap in self.caps:
            if cap.isExpired():
                Log.info("CAP {0} has expired.".format(cap))
                self.caps.remove(cap)
        heapq.heapify(self.caps)

    def popup_menu_cb(self, widget, button, time, data=None):
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, gtk.status_icon_position_menu, 3, time, self.statusIcon)
