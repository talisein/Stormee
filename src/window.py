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
import webkit
import pango
import glib


Log = logging.getLogger()

class KeyTable(gtk.Table):
    def __init__(self, rows=1, columns=2, homo=False):
        gtk.Table.__init__(self, rows, columns, homo)
        self.rows = rows
        self.columns = columns
        self.set_sensitive(True)
        
        
    def add(self, key, value, keyTooltip=None, valueTooltip=None, markup=None):
        keyTag = gtk.Label()
        valueTag = gtk.Label()
        keyTag.set_alignment(1.0, 0.5)
        valueTag.set_alignment(0.0, 0.5)
        valueTag.set_selectable(True)
#        valueTag.set_ellipsize(pango.ELLIPSIZE_END)
        
        valueTag.set_use_markup(markup is not None)
        valueTag.set_single_line_mode(True)
        keyTag.set_single_line_mode(True)
        keyTag.set_text(key)
        valueTag.set_text(value)
        if markup is not None:
            valueTag.set_markup(glib.markup_escape_text(markup))
            valueTag.set_use_markup(True)
        valueTag.set_sensitive(True)
        if keyTooltip is not None:
            keyTag.set_tooltip_text(keyTooltip)
        if valueTooltip is not None:
            valueTag.set_tooltip_text(valueTooltip)
        self.rows += 1
        self.resize(self.rows, self.columns)
        self.attach(keyTag, 0, 1, self.rows - 1, self.rows, xoptions=gtk.FILL, xpadding=5)
        self.attach(valueTag, 1, 2, self.rows -1, self.rows, xpadding=5)
        self.show_all()

    def clear(self):
        self.resize(1, 2)
        self.foreach(self.__delChild)

    def __delChild(self, child):
        self.remove(child)
        
class Window:
    def __alert(self, tag, text, keyTooltip=None, valueTooltip=None, markup=None):
        if text is not None:
            self.keyTable.add(tag + ':', text, keyTooltip, valueTooltip, markup)
               
    def __alerttz(self, tag, time, keyTooltip=None, valueTooltip=None, markup=None):
        if time is not None and isinstance(time, datetime.datetime):
            self.keyTable.add(tag + ':', time.astimezone(dateutil.tz.tzlocal()).strftime("%A (%b %d), %I:%M:%S %p %Z"), keyTooltip, valueTooltip, markup)

    def __init__(self):
        self.alerts = dict()
        self.ids = list()
        self.index = -1
        builder = gtk.Builder()
        builder.add_from_file('../glade/CAPViewer.glade')
        builder.connect_signals(self)
        self.window = builder.get_object("mainWindow")
        
        self.capTitleBuffer = builder.get_object("capTitleBuffer")

        self.keyValueWindow = builder.get_object("keyValueScrolledWindow")
        self.keyTable = KeyTable() 
        self.keyValueWindow.add_with_viewport(self.keyTable)
       
        self.infoTextBuffer = builder.get_object("infoTextBuffer")
        
        self.midLeftVbox = builder.get_object("midLeftVbox")
        self.webview = webkit.WebView()
        
        self.midLeftVbox.pack_start(self.webview, False, True, 1)
        self.webview.show()
                
        self.window.show()
        
        
        
            
    def on_mainWindow_destroy(self, widget, data=None):
        pass
    
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
            self.keyTable.clear()
            self.__alert('Message ID', alert.id, cap.Alert.aboutId())
            self.__alert('Version', alert.version)
            self.__alert('Sender', alert.sender,cap.Alert.aboutSender())
            self.__alerttz('Sent', alert.sent,cap.Alert.aboutSent())
            self.__alert('Status', alert.status, cap.Alert.aboutStatus(), cap.Alert.aboutStatus(alert.status))
            self.__alert('Message Type', alert.msgType, cap.Alert.aboutMsgType(), cap.Alert.aboutMsgType(alert.msgType))
            self.__alert('Source', alert.source, cap.Alert.aboutSource())
            self.__alert('Scope', alert.scope, cap.Alert.aboutScope(), cap.Alert.aboutScope(alert.scope))
            self.__alert('Restriction', alert.restriction, cap.Alert.aboutRestriction())
            self.__alert('Addresses', alert.addresses, cap.Alert.aboutAddresses())
            self.__alert('Note', alert.note, cap.Alert.aboutNote())
            self.__alert('Incidents', alert.incidents, cap.Alert.aboutIncidents())
            for code in alert.codes:
                self.__alert('Code', code, cap.Alert.aboutCode())
            for reference in alert.references:
                self.__alert(reference, cap.Alert.aboutReferences())
            
            for info in alert.infos:
                self.__alert('Language', info.language, cap.Info.aboutLanguage())
                for c in info.categories:
                    self.__alert('Category', c, cap.Info.aboutCategory(), cap.Info.aboutCategory(c))
                if info.event is not None:
                    self.__alert('Event', info.event, cap.Info.aboutEvent())
                    self.capTitleBuffer.set_text(info.event)
                for e in info.responseTypes:
                    self.__alert('Response Type', e, cap.Info.aboutResponseType(), cap.Info.aboutResponseType(e))
                self.__alert('Urgency', info.urgency, cap.Info.aboutUrgency(), cap.Info.aboutUrgency(info.urgency))
                self.__alert('Severity', info.severity, cap.Info.aboutSeverity(), cap.Info.aboutSeverity(info.severity))
                self.__alert('Certainty', info.certainty, cap.Info.aboutCertainty(), cap.Info.aboutCertainty(info.certainty))
                self.__alert('Audience', info.audience, cap.Info.aboutAudience())
                self.__alerttz('Effective', info.effective, cap.Info.aboutEffective())
                for code in info.eventCodes:
                    self.__alert(code, info.eventCodes[code], cap.Info.aboutEventCode())
                self.__alerttz('Onset', info.onset, cap.Info.aboutOnset())
                self.__alerttz('Expires', info.expires, cap.Info.aboutExpires())
                self.__alert('Sender Name', info.senderName, cap.Info.aboutSenderName())
                self.__alert('Web', info.web, cap.Info.aboutWeb())
                self.__alert('Contact', info.contact, cap.Info.aboutContact())
                for p in info.parameters:
                    self.__alert(p, info.parameters[p], cap.Info.aboutParameter())
                
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
                        m = '<a href="' + utils.mapPolygon(polygon) + '">%s</a>'
                        self.__alert('Map link', 'Google Maps', markup=m)
                        self.webview.open(utils.mapPolygon(polygon))
                    for circle in area.circles:
                        self.__alert('Map link', utils.mapCircle(circle))
                        self.webview.open(utils.mapCircle(circle))

        except AttributeError as detail:
            Log.debug('Invalid class passed to populateCap %s' % type(alert))
            print detail
        except:
            raise
            
