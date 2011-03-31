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
    __COLOR_BLACK = gtk.gdk.color_parse("black") 
    __COLOR_GREEN = gtk.gdk.color_parse("ForestGreen") 
    __COLOR_BLUE = gtk.gdk.color_parse("blue")
    __COLOR_ORANGE = gtk.gdk.color_parse("orange")
    __COLOR_GRAY = gtk.gdk.color_parse("gray")
    __COLOR_RED = gtk.gdk.color_parse("red")

    __COLOR_MAP = dict({
                        cap.Alert.STATUS_ACTUAL: __COLOR_BLACK,
                        cap.Alert.STATUS_DRAFT: __COLOR_GREEN,
                        cap.Alert.STATUS_EXERCISE: __COLOR_BLUE,
                        cap.Alert.STATUS_SYSTEM: __COLOR_ORANGE,
                        cap.Alert.STATUS_TEST: __COLOR_BLACK,
                        cap.Alert.MSGTYPE_ALERT: __COLOR_BLACK,
                        cap.Alert.MSGTYPE_UPDATE: __COLOR_BLACK,
                        cap.Alert.MSGTYPE_CANCEL: __COLOR_GRAY,
                        cap.Alert.MSGTYPE_ERROR: __COLOR_RED,
                        cap.Alert.MSGTYPE_ACK: __COLOR_BLACK,
                        cap.Info.URGENCY_IMMEDIATE: __COLOR_RED,
                        cap.Info.URGENCY_EXPECTED: __COLOR_ORANGE,
                        cap.Info.URGENCY_FUTURE: __COLOR_BLACK,
                        cap.Info.URGENCY_PAST: __COLOR_GREEN,
                        cap.Info.URGENCY_UNKNOWN: __COLOR_GRAY,
                        cap.Info.SEVERITY_EXTREME: __COLOR_RED,
                        cap.Info.SEVERITY_SEVERE: __COLOR_ORANGE,
                        cap.Info.SEVERITY_MODERATE: __COLOR_BLACK,
                        cap.Info.SEVERITY_MINOR: __COLOR_GREEN,
                        cap.Info.SEVERITY_UNKNOWN: __COLOR_GRAY,
                        })
    
    def __alert(self, tag, text, keyTooltip=None, valueTooltip=None, url=None):
        if text is not None:
            self.keyTable.add(tag + ':', text, keyTooltip, valueTooltip, url)
               
    def __alerttz(self, tag, time, keyTooltip=None, valueTooltip=None, url=None):
        if time is not None and isinstance(time, datetime.datetime):
            self.keyTable.add(tag + ':', time.astimezone(dateutil.tz.tzlocal()).strftime("%A (%b %d), %I:%M:%S %p %Z"), keyTooltip, valueTooltip, url)

    def status_data_func(self, celllayout, cell, model, iter, user_data=None):
        status = model.get_value(iter, 1)
        cell.set_property('text', str.format("{0}",status))
        if status in Window.__COLOR_MAP:
            cell.set_property('foreground', Window.__COLOR_MAP[status] )
        else:
            cell.set_property('foreground', Window.__COLOR_BLACK)

    def msgType_data_func(self, celllayout, cell, model, iter, user_data=None):
        msgType = model.get_value(iter, 2)
        cell.set_property('text', str.format("{0}",msgType))
        
        if msgType in Window.__COLOR_MAP:
            cell.set_property('foreground', Window.__COLOR_MAP[msgType] )
        else:
            cell.set_property('foreground', Window.__COLOR_BLACK )
            
    def urgency_data_func(self, celllayout, cell, model, iter, user_data=None):
        urgency = model.get_value(iter, 3)
        cell.set_property('text', str.format("{0}",urgency))
        
        if urgency in Window.__COLOR_MAP:
            cell.set_property('foreground', Window.__COLOR_MAP[urgency] )
        else: 
            cell.set_property('foreground', Window.__COLOR_BLACK )

    def severity_data_func(self, celllayout, cell, model, iter, user_data=None):
        severity = model.get_value(iter, 4)
        cell.set_property('text', str.format("{0}",severity))
        if severity in Window.__COLOR_MAP:
            cell.set_property('foreground', Window.__COLOR_MAP[severity] )
        else:
            cell.set_property('foreground', Window.__COLOR_BLACK )
    
    def __init_combobox(self, builder):
        self.comboBoxListStore = builder.get_object("comboBoxListStore")
        self.comboBox = builder.get_object("comboBox")
        title_cr = gtk.CellRendererText()
        status_cr = gtk.CellRendererText()
        msgType_cr = gtk.CellRendererText()
        urgency_cr = gtk.CellRendererText()
        severity_cr = gtk.CellRendererText()
        slash1_cr = gtk.CellRendererText()
        slash2_cr = gtk.CellRendererText()
        slash3_cr = gtk.CellRendererText()
        self.comboBox.pack_start(title_cr, True)
        self.comboBox.pack_start(status_cr, False)
        self.comboBox.pack_start(slash1_cr, False)
        self.comboBox.pack_start(msgType_cr, False)
        self.comboBox.pack_start(slash2_cr, False)
        self.comboBox.pack_start(urgency_cr, False)
        self.comboBox.pack_start(slash3_cr, False)
        self.comboBox.pack_start(severity_cr, False)
        self.comboBox.add_attribute(title_cr, 'text', 0)
        self.comboBox.add_attribute(status_cr, 'text', 1)
        self.comboBox.add_attribute(msgType_cr, 'text', 2)
        self.comboBox.add_attribute(urgency_cr, 'text', 3)
        self.comboBox.add_attribute(severity_cr, 'text', 4)
        self.comboBox.add_attribute(slash1_cr, 'text', 5)
        self.comboBox.add_attribute(slash2_cr, 'text', 5)
        self.comboBox.add_attribute(slash3_cr, 'text', 5)
        self.comboBox.set_cell_data_func(status_cr, self.status_data_func)
        self.comboBox.set_cell_data_func(msgType_cr, self.msgType_data_func)
        self.comboBox.set_cell_data_func(urgency_cr, self.urgency_data_func)
        self.comboBox.set_cell_data_func(severity_cr, self.severity_data_func)


    def __init__(self):
        self.alerts = dict()
        self.ids = list()
        self.index = -1
        builder = gtk.Builder()
        builder.add_from_file('../glade/CAPViewer.glade')
        builder.connect_signals(self)
        self.window = builder.get_object("mainWindow")
        
        self.__init_combobox(builder)

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

    def combobox_changed_cb(self, combobox):
        pass
        active = combobox.get_active()
        if active >= 0:
            self.populateCap(self.alerts[self.ids[active]])
            self.index = active

    def on_mainWindow_destroy(self, widget, data=None):
        pass


    def acceptCap(self, alert):
        if isinstance(alert, cap.Alert):
            self.alerts[alert.id] = alert
            self.ids.append(alert.id)
            if len(alert.infos) > 0:
                self.comboBoxListStore.append((alert.getTitle(), alert.status, alert.msgType, alert.infos[0].urgency, alert.infos[0].severity, '/'))
            else:
                self.comboBoxListStore.append((alert.getTitle(), alert.status, alert.msgType, cap.Info.URGENCY_UNKNOWN, cap.Info.SEVERITY_UNKNOWN))
            if self.index is -1:
                self.populateCap(alert)
                self.index = 0
            self.comboBox.set_active(self.index)

        else:
            Log.error("Invalid class passed to acceptCap(): %s" % type(alert))

    def onNextClick(self, e):
        if len(self.ids) is not 0:
            if (self.index+1) < len(self.ids):
                self.index += 1
            else:
                self.index = 0

            self.populateCap(self.alerts[self.ids[self.index]])
            self.comboBox.set_active(self.index)

    def onPrevClick(self, e):
        if len(self.ids) is not 0:
            if self.index is not 0:
                self.index -= 1
            else:
                self.index = len(self.ids) - 1
            self.populateCap(self.alerts[self.ids[self.index]])
            self.comboBox.set_active(self.index)
    
    def __populatePVTEC(self, info):
        if info.vtec is not None:
            if info.vtec.hasPVTEC:
                self.__alert('P-VTEC Class', info.vtec.product_class)
                self.__alert('P-VTEC Actions', info.vtec.actions)
                self.__alert('P-VTEC Office ID', info.vtec.office_id)
                self.__alert('P-VTEC Phenomena', info.vtec.phenomena)
                self.__alert('P-VTEC Significance', info.vtec.significance)
                self.__alert('P-VTEC Event Tracking Number', info.vtec.event_tracking_number)
                if info.vtec.begin is not None:
                    self.__alerttz('P-VTEC Event Beginning', info.vtec.begin)
                else:
                    self.__alert('P-VTEC Event Beginning', 'Ongoing')

                if info.vtec.end is not None:
                    self.__alerttz('P-VTEC Event End', info.vtec.end)
                else:
                    self.__alert('P-VTEC Event End', 'Until Further Notice')
            
    def __populateHVTEC(self, info):
        if info.vtec is not None:
            if info.vtec.hasHVTEC:
                self.__alert('H-VTEC NWS Location Id', info.vtec.location_id)
                self.__alert('H-VTEC Flood Severity', info.vtec.flood_severity)
                self.__alert('H-VTEC Immediate Cause', info.vtec.immediate_cause)
                
                if info.vtec.flood_begin is not None:
                    self.__alerttz('H-VTEC Flood Begin Time', info.vtec.flood_begin)
                else:
                    self.__alerttz('H-VTEC Flood Begin Time', 'Ongoing')

                if info.vtec.flood_crest is not None:
                    self.__alerttz('H-VTEC Flood Crest Time', info.vtec.flood_crest)

                if info.vtec.flood_end is not None:
                    self.__alerttz('H-VTEC Flood End Time', info.vtec.flood_end)
                else:
                    self.__alert('H-VTEC Flood End Time', 'Until Further Notice')
                    
                self.__alert('H-VTEC Flood Record Status', info.vtec.flood_record_status)
        
    def populateCap(self, alert):
        try:
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
                self.__alert('Urgency', info.urgency, cap.Info.aboutUrgency(), cap.Info.aboutUrgency(info.urgency))
                self.__alert('Severity', info.severity, cap.Info.aboutSeverity(), cap.Info.aboutSeverity(info.severity))
                self.__alert('Certainty', info.certainty, cap.Info.aboutCertainty(), cap.Info.aboutCertainty(info.certainty))
                for e in info.responseTypes:
                    self.__alert('Response Type', e, cap.Info.aboutResponseType(), cap.Info.aboutResponseType(e))
                self.__alert('Audience', info.audience, cap.Info.aboutAudience())
                for code in info.eventCodes:
                    if code == 'SAME':
                        self.__alert(code, cap.NWIS.expandNWIS(info.eventCodes[code]))
                    else:
                        self.__alert(code, info.eventCodes[code], cap.Info.aboutEventCode())
                self.__alerttz('Effective', info.effective, cap.Info.aboutEffective())
                self.__alerttz('Onset', info.onset, cap.Info.aboutOnset())
                self.__alerttz('Expires', info.expires, cap.Info.aboutExpires())
                self.__populatePVTEC(info)
                self.__populateHVTEC(info)
                self.__alert('Web', info.web, cap.Info.aboutWeb(), url=info.web)
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
                self.__alert('Reference', reference, cap.Alert.aboutReferences())
            self.__alert('Sender', alert.sender,cap.Alert.aboutSender())
            self.__alerttz('Sent', alert.sent,cap.Alert.aboutSent())
            self.__alert('Version', alert.version)
            self.__alert('Message ID', alert.id, cap.Alert.aboutId())
                        
        except AttributeError:
            Log.error("Attribute error while populating window from CAP {0}.".format(alert.id), exc_info=True)
        except:
            Log.error("Unexpected error while populating window from CAP {0}".format(alert.id), exc_info=True)            
