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

import gtk
import pygtk
pygtk.require("2.0")

import cap
import utils
import logging
import datetime
import dateutil
import sys

Log = logging.getLogger()


class Window:
    def __alert(self, tag, text):
        if text is not None:
            self.alertListStore.append([tag, text])      
               
    def __alerttz(self, tag, time):
        if time is not None and isinstance(time, datetime.datetime):
            self.alertListStore.append([tag, time.astimezone(dateutil.tz.tzlocal()).strftime("%A (%b %d), %I:%M:%S %p %Z")])

    def __init__(self):
        self.alerts = dict()
        self.ids = list()
        self.index = -1
        builder = gtk.Builder()
        builder.add_from_file('../glade/CAPViewer.glade')
        builder.connect_signals(self)
        self.window = builder.get_object("mainWindow")
        
        self.capTitleBuffer = builder.get_object("capTitleBuffer")

        self.alertTreeView = builder.get_object("alertTreeview")
        self.alertTagColumn = gtk.TreeViewColumn('Tag')
        self.alertTextColumn = gtk.TreeViewColumn('Text')
        self.alertTagRenderer = gtk.CellRendererText()
        self.alertTextRenderer = gtk.CellRendererText()
        self.alertTextColumn.pack_start(self.alertTextRenderer, True)
        self.alertTagColumn.pack_start(self.alertTagRenderer, True)
        self.alertTextColumn.set_attributes(self.alertTextRenderer, text=1)
        self.alertTagColumn.set_attributes(self.alertTagRenderer, text=0)
#        self.alertTagColumn.set_attributes(self.alertTagRenderer, sensitive=1)
        
        self.alertListStore = gtk.ListStore(str, str)
        self.alertTreeView.append_column(self.alertTagColumn)
        self.alertTreeView.append_column(self.alertTextColumn)
        self.alertTreeView.set_model(self.alertListStore)

        self.alertTagColumn.set_clickable(True)
        
        self.infoTextBuffer = builder.get_object("infoTextBuffer")
        self.window.show()
        
            
    def on_mainWindow_destroy(self, widget, data=None):
        gtk.main_quit()
        
    def acceptCap(self, alert):
        if isinstance(alert, cap.Alert):
            self.alerts[alert.id] = alert
            self.ids.append(alert.id)
            if self.index is -1:
                self.populateCap(alert)
                self.index = 0
        else:
            Log.error("Invalid class passed to acceptCap(): %s" % type(alert))

    def onNextClick(self, e):
        if len(self.ids) is not 0:
            if (self.index+1) < len(self.ids):
                self.index += 1
            else:
                self.index = 0
            self.populateCap(self.alerts[self.ids[self.index]])

    def onPrevClick(self, e):
        if len(self.ids) is not 0:
            if self.index is not 0:
                self.index -= 1
            else:
                self.index = len(self.ids) - 1
            self.populateCap(self.alerts[self.ids[self.index]])
            
    def populateCap(self, alert):
        try:
            self.capTitleBuffer.set_text(alert.id)
            self.alertListStore.clear()
            self.__alert('Version', alert.version)
            self.__alert('Sender', alert.sender)
            self.__alerttz('Sent', alert.sent)
            self.__alert('Status', alert.status)
            self.__alert('Message Type', alert.msgType)
            self.__alert('Source', alert.source)
            self.__alert('Scope', alert.scope)
            self.__alert('Restriction', alert.restriction)
            self.__alert('Addresses', alert.addresses)
            self.__alert('Note', alert.note)
            self.__alert('Incidents', alert.incidents)
            for code in alert.codes:
                self.__alert('Code', code)
            for reference in alert.references:
                self.__alert(reference)
            
            for info in alert.infos:
                self.__alert('Language', info.language)
                for c in info.categories:
                    self.__alert('Category', c)
                if info.event is not None:
                    self.__alert('Event', info.event)
                    self.capTitleBuffer.set_text(info.event)
                for e in info.responseTypes:
                    self.__alert('Response Type', e)
                self.__alert('Urgency', info.urgency)
                self.__alert('Severity', info.severity)
                self.__alert('Certainty', info.certainty)
                self.__alert('Audience', info.audience)
                self.__alerttz('Effective', info.effective)
                for code in info.eventCodes:
                    self.__alert(code, info.eventCodes[code])
                self.__alerttz('Onset', info.onset)
                self.__alerttz('Expires', info.expires)
                self.__alert('Sender Name', info.senderName)
                self.__alert('Web', info.web)
                self.__alert('Contact', info.contact)
                for p in info.parameters:
                    self.__alert(p, info.parameters[p])
                
                helper = str()
                if info.headline is not None:
                    helper += info.headline + '\n\n'
                helper += 'Description:\n\n'
                if info.description is not None:
                    helper += info.description + '\n\n'
                helper += 'Instructions:\n\n'
                if info.instruction is not None:
                    helper += info.instruction
                self.infoTextBuffer.set_text(helper)
                
                for area in info.areas:
                    for polygon in area.polygons:
                        self.__alert('Map link', utils.mapPolygon(polygon))
                    for circle in area.circles:
                        self.__alert('Map link', utils.mapCircle(circle))

        except AttributeError as detail:
            Log.debug('Invalid class passed to populateCap %s' % type(alert))
            print detail
        except:
            raise
            
