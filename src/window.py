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
import webkit


Log = logging.getLogger()

class KeyTable(gtk.Table):
    def __init__(self, rows=1, columns=2, homo=False):
        gtk.Table.__init__(self, rows, columns, homo)
        self.rows = rows
        self.columns = columns
        self.set_sensitive(True)
        
    def add(self, key, value, keyTooltip=None, valueTooltip=None, url=None):
        keyTag = gtk.Label()
        valueTag = gtk.Label()
        keyTag.set_alignment(1.0, 0.5)

        if url is not None:
            valueTag = gtk.LinkButton(url)
            valueTag.set_relief(gtk.RELIEF_NONE)
            valueTag.set_label(value)
        else:
            valueTag.set_selectable(True)
            valueTag.set_single_line_mode(True)
            valueTag.set_text(value)
            
        valueTag.set_alignment(0.0, 0.5)
        keyTag.set_single_line_mode(True)
        keyTag.set_text(key)
        valueTag.set_sensitive(True)
        if keyTooltip is not None:
            keyTag.set_tooltip_text(keyTooltip)
        if valueTooltip is not None:
            valueTag.set_tooltip_text(valueTooltip)
        self.rows += 1
        self.resize(self.rows, self.columns)
        self.attach(keyTag, 0, 1, self.rows - 1, self.rows, xoptions=gtk.FILL, yoptions=gtk.FILL, xpadding=3)
        self.attach(valueTag, 1, 2, self.rows -1, self.rows, xpadding=5)
        self.show_all()

    def clear(self):
        self.resize(1, 2)
        self.foreach(self.__delChild)

    def __delChild(self, child):
        self.remove(child)
        
class Window:
    def __alert(self, tag, text, keyTooltip=None, valueTooltip=None, url=None):
        if text is not None:
            self.keyTable.add(tag + ':', text, keyTooltip, valueTooltip, url)
               
    def __alerttz(self, tag, time, keyTooltip=None, valueTooltip=None, url=None):
        if time is not None and isinstance(time, datetime.datetime):
            self.keyTable.add(tag + ':', time.astimezone(dateutil.tz.tzlocal()).strftime("%A (%b %d), %I:%M:%S %p %Z"), keyTooltip, valueTooltip, url)

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
        self.viewport = gtk.Viewport()
        self.keyTable = KeyTable() 
        self.keyValueWindow.add_with_viewport(self.keyTable)
       
        self.notebook = builder.get_object("notebook")
        self.notebook.show()
        self.window.show()
        
    def changepage_cb(self, notebook, page, page_num, data=None):
        p = self.notebook.get_nth_page(page_num)
        return True
        
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
    
    def populatePVTEC(self, vtec):
        vtec = vtec.strip(' /')
        
        self.__alert('P-VTEC Class', cap.VTEC.getProductClass(vtec[0]))
        self.__alert('P-VTEC Actions', cap.VTEC.getActions(vtec[2:5]))
        self.__alert('P-VTEC Office ID', vtec[6:10])
        self.__alert('P-VTEC Phenomena', cap.VTEC.getPhenomena(vtec[11:13]))
        self.__alert('P-VTEC Significance', cap.VTEC.getSignificance(vtec[14:15]))
        self.__alert('P-VTEC Event Tracking Number', vtec[16:20])

        try:
            if vtec[21:33] != '000000T0000Z':
                beginning = datetime.datetime.strptime(vtec[21:33],"%y%m%dT%H%MZ").replace(tzinfo=dateutil.tz.gettz('UTC'))
                self.__alerttz('P-VTEC Event Beginning', beginning)
        except:
            Log.error("Invalid P-VTEC Event Beginning {0}".format(vtec[21:33]))
            
        try:
            if vtec[34:46] != '000000T0000Z':
                end = datetime.datetime.strptime(vtec[34:46],"%y%m%dT%H%MZ").replace(tzinfo=dateutil.tz.gettz('UTC'))
                self.__alerttz('P-VTEC Event End', end)
        except:
            Log.error("Invalid P-VTEC Event End {0}".format(vtec[34:46]))
            
    def populateHVTEC(self, vtec):
        vtec = vtec.strip(' /')
        self.__alert('H-VTEC NWS Location Id', vtec[0:5])
        self.__alert('H-VTEC Flood Severity', cap.VTEC.getFloodSeverity(vtec[6]))
        self.__alert('H-VTEC Immediate Cause', cap.VTEC.getImmediateCause(vtec[8:10]))
        
        try:
            if vtec[11:23] != '000000T0000Z':
                begin = datetime.datetime.strptime(vtec[11:23],"%y%m%dT%H%MZ").replace(tzinfo=dateutil.tz.gettz('UTC'))
                self.__alerttz('H-VTEC Flood Begin Time', begin)
        except:
            Log.error("Invalid H-VTEC Crest Begin Time {0}".format(vtec[11:23]))
        
        try:
            if vtec[24:36] != '000000T0000Z':
                crest = datetime.datetime.strptime(vtec[24:36],"%y%m%dT%H%MZ").replace(tzinfo=dateutil.tz.gettz('UTC'))   
                self.__alerttz('H-VTEC Flood Crest Time', crest)
        except:
            Log.error("Invalid H-VTEC Flood Crest Time {0}".format(vtec[24:36]))
        try:
            if vtec[37:49] != '000000T0000Z':
                end = datetime.datetime.strptime(vtec[37:49],"%y%m%dT%H%MZ").replace(tzinfo=dateutil.tz.gettz('UTC'))
                self.__alerttz('H-VTEC Flood End Time', end)
        except:
            Log.error("Invalid H-VTEC Flood End Time {0}".format(vtec[37:49]))
            
        self.__alert('H-VTEC Flood Record Status', cap.VTEC.getFloodRecordStatus(vtec[50:52]))
        
    def populateCap(self, alert):
        try:
            self.capTitleBuffer.set_text(alert.id)
            self.keyTable.clear()
            while self.notebook.get_n_pages() > 0:
                self.notebook.remove_page(-1)
            self.__alert('Note', alert.note, cap.Alert.aboutNote())
            self.__alert('Message Type', alert.msgType, cap.Alert.aboutMsgType(), cap.Alert.aboutMsgType(alert.msgType))
            self.__alert('Incidents', alert.incidents, cap.Alert.aboutIncidents())
            self.__alert('Status', alert.status, cap.Alert.aboutStatus(), cap.Alert.aboutStatus(alert.status))
            self.__alert('Scope', alert.scope, cap.Alert.aboutScope(), cap.Alert.aboutScope(alert.scope))
            self.__alert('Addresses', alert.addresses, cap.Alert.aboutAddresses())
            self.__alert('Restriction', alert.restriction, cap.Alert.aboutRestriction())
            self.__alert('Source', alert.source, cap.Alert.aboutSource())
            
            for info in alert.infos:
                tb = gtk.TextBuffer()
                tv = gtk.TextView(tb)
                label = gtk.Label('Info')
                pn = self.notebook.append_page(tv, label)
                self.notebook.set_current_page(pn)
                self.notebook.show()
                tv.show()
                self.__alert('Sender Name', info.senderName, cap.Info.aboutSenderName())
                for c in info.categories:
                    self.__alert('Category', c, cap.Info.aboutCategory(), cap.Info.aboutCategory(c))
                if info.event is not None and info.event is not 'UNTITLED EVENT':
                    self.__alert('Event', info.event, cap.Info.aboutEvent())
                    self.capTitleBuffer.set_text(info.event)
                self.__alert('Urgency', info.urgency, cap.Info.aboutUrgency(), cap.Info.aboutUrgency(info.urgency))
                self.__alert('Severity', info.severity, cap.Info.aboutSeverity(), cap.Info.aboutSeverity(info.severity))
                self.__alert('Certainty', info.certainty, cap.Info.aboutCertainty(), cap.Info.aboutCertainty(info.certainty))
                for e in info.responseTypes:
                    self.__alert('Response Type', e, cap.Info.aboutResponseType(), cap.Info.aboutResponseType(e))
                self.__alert('Audience', info.audience, cap.Info.aboutAudience())
                for code in info.eventCodes:
                    self.__alert(code, info.eventCodes[code], cap.Info.aboutEventCode())
                self.__alerttz('Effective', info.effective, cap.Info.aboutEffective())
                self.__alerttz('Onset', info.onset, cap.Info.aboutOnset())
                self.__alerttz('Expires', info.expires, cap.Info.aboutExpires())
                self.__alert('Web', info.web, cap.Info.aboutWeb(), url=info.web)
                self.__alert('Contact', info.contact, cap.Info.aboutContact())
                for p in info.parameters:
                    if p == 'P-VTEC':
                        self.populatePVTEC(info.parameters[p])
                        continue
                    if p == 'H-VTEC':
                        self.populateHVTEC(info.parameters[p])
                        continue
                    if p == 'VTEC':
                        for chunk in info.parameters[p].split('/'):
                            if len(chunk) is 46:
                                self.populatePVTEC(chunk)
                            elif len(chunk) is 52:
                                self.populateHVTEC(chunk)
                        continue
                    
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
                self.__alert('Language', info.language, cap.Info.aboutLanguage())

                tb.set_text(helper)
                file = open('../marker-simple.html')
                
#                self.webview.load_html_string(file.read(),'http://localhost/testing')
                for area in info.areas:
                    for polygon in area.polygons:
                        webview = webkit.WebView()
                        label = gtk.Label('Map')
                        pn = self.notebook.append_page(webview, label)
                        webview.show()
                        webview.load_html_string(utils.mapPolygon(polygon),'http://localhost/testing')
                    for circle in area.circles:
                        webview = webkit.WebView()
                        label = gtk.Label('Map')
                        pn = self.notebook.append_page(webview, label)
                        webview.show()
                        webview.load_html_string(utils.mapCircle(circle),'http://localhost/testing')
            for code in alert.codes:
                self.__alert('Code', code, cap.Alert.aboutCode())
            for reference in alert.references:
                self.__alert(reference, cap.Alert.aboutReferences())
            self.__alert('Sender', alert.sender,cap.Alert.aboutSender())
            self.__alerttz('Sent', alert.sent,cap.Alert.aboutSent())
            self.__alert('Version', alert.version)
            self.__alert('Message ID', alert.id, cap.Alert.aboutId())
                        
        except AttributeError:
            Log.error("Attribute error while populating window from CAP {0}.".format(alert.id), exc_info=True)
        except:
            Log.error("Unexpected error while populating window from CAP {0}".format(alert.id), exc_info=True)            
