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

import heapq
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
        spaceTag = gtk.Label()
        hbox = gtk.HBox()
        
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
        
        spaceTag.set_single_line_mode(True)
        valueTag.set_sensitive(True)
        if keyTooltip is not None:
            keyTag.set_tooltip_text(keyTooltip)
        if valueTooltip is not None:
            valueTag.set_tooltip_text(valueTooltip)
        self.rows += 1
        self.resize(self.rows, self.columns)
        hbox.pack_start(valueTag, False, True)
 #       hbox.pack_start(spaceTag, True, True)
        self.attach(keyTag, 0, 1, self.rows - 1, self.rows, xoptions=gtk.FILL, yoptions=gtk.FILL, xpadding=3)
        self.attach(hbox, 1, 2, self.rows -1, self.rows, xoptions=gtk.EXPAND|gtk.FILL, xpadding=5)
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

    def alert_titleData(self, column, cell, model, iter, user_data=None):
        alert = model.get_value(iter, 0)
        if alert is not None:
            title = alert.getTitle().strip()
            cell.set_property('text', str.format("{0}", title))


    def alert_statusData(self, column, cell, model, iter, user_data=None):
        alert = model.get_value(iter, 0)
        if alert is not None:
            status = alert.status
            cell.set_property('text', str.format("{0}",alert.status))
            if status in Window.__COLOR_MAP:
                cell.set_property('foreground', Window.__COLOR_MAP[status] )
            else:
                cell.set_property('foreground', Window.__COLOR_BLACK)

    def alert_msgTypeData(self, column, cell, model, iter, user_data=None):
        alert = model.get_value(iter, 0)
        if alert is not None:
            msgType = alert.msgType
            cell.set_property('text', str.format("{0}",alert.msgType))
            if msgType in Window.__COLOR_MAP:
                cell.set_property('foreground', Window.__COLOR_MAP[msgType] )
            else:
                cell.set_property('foreground', Window.__COLOR_BLACK)

    def alert_urgencyData(self, column, cell, model, iter, user_data=None):
        alert = model.get_value(iter, 0)
        if alert is not None:
    
            if len(alert.infos) > 0:
                urgency = alert.infos[0].urgency
            else:
                urgency = cap.Info.URGENCY_UNKNOWN
            cell.set_property('text', str.format("{0}",urgency))
    
            if urgency in Window.__COLOR_MAP:
                cell.set_property('foreground', Window.__COLOR_MAP[urgency] )
            else:
                cell.set_property('foreground', Window.__COLOR_BLACK)
            
    def alert_severityData(self, column, cell, model, iter, user_data=None):
        alert = model.get_value(iter, 0)
        if alert is not None:
            if len(alert.infos) > 0:
                severity = alert.infos[0].severity
            else:
                severity = cap.Info.SEVERITY_UNKNOWN
            cell.set_property('text', str.format("{0}",severity))
    
            if severity in Window.__COLOR_MAP:
                cell.set_property('foreground', Window.__COLOR_MAP[severity] )
            else:
                cell.set_property('foreground', Window.__COLOR_BLACK)

    def alert_slashData(self, column, cell, model, iter, user_data=None):
        cell.set_property('text', '/')
        
    def alert_treeSort(self, treemodel, iter1, iter2, user_data=None):
        a1 = treemodel.get_value(iter1, 0).getTitle()
        a2 = treemodel.get_value(iter2, 0).getTitle()
        ret = 0
        if a1 < a2:
            ret = -1
        if a1 > a2:
            ret = 1
        return ret

    def __init_combobox2(self, builder):
        self.comboBox2 = builder.get_object("comboBox2")
        self.treeStore = gtk.TreeStore(object)
        self.comboBox2.set_model(self.treeStore)
        title_cr = gtk.CellRendererText()
        status_cr = gtk.CellRendererText()
        msgType_cr = gtk.CellRendererText()
        urgency_cr = gtk.CellRendererText()
        severity_cr = gtk.CellRendererText()
        slash1_cr = gtk.CellRendererText()
        slash2_cr = gtk.CellRendererText()
        slash3_cr = gtk.CellRendererText()
        self.comboBox2.pack_start(title_cr, True)
        self.comboBox2.pack_start(status_cr, False)
        self.comboBox2.pack_start(slash1_cr, False)
        self.comboBox2.pack_start(msgType_cr, False)
        self.comboBox2.pack_start(slash2_cr, False)
        self.comboBox2.pack_start(urgency_cr, False)
        self.comboBox2.pack_start(slash3_cr, False)
        self.comboBox2.pack_start(severity_cr, False)
        self.comboBox2.set_cell_data_func(title_cr, self.alert_titleData)
        self.comboBox2.set_cell_data_func(status_cr, self.alert_statusData)
        self.comboBox2.set_cell_data_func(msgType_cr, self.alert_msgTypeData)
        self.comboBox2.set_cell_data_func(urgency_cr, self.alert_urgencyData)
        self.comboBox2.set_cell_data_func(severity_cr, self.alert_severityData)
        self.comboBox2.set_cell_data_func(slash1_cr, self.alert_slashData)
        self.comboBox2.set_cell_data_func(slash2_cr, self.alert_slashData)
        self.comboBox2.set_cell_data_func(slash3_cr, self.alert_slashData)
        self.treeStore.set_default_sort_func(self.alert_treeSort)
        self.treeStore.set_sort_column_id(-1, gtk.SORT_ASCENDING)

    def __init__(self, tray):
        self.alerts = dict()
        self.ids = list()
        self.parents = set()
        self.parentiters = dict()
        self.tray = tray
        
        self.index = -1
        builder = gtk.Builder()
        builder.add_from_file('../glade/CAPViewer.glade')
        builder.connect_signals(self)
        self.window = builder.get_object("mainWindow")
        
        self.__init_combobox(builder)
        self.__init_combobox2(builder)
        self.keyValueWindow = builder.get_object("keyValueScrolledWindow")
        self.keyValueWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.viewport = gtk.Viewport()
        self.keyTable = KeyTable() 
        self.keyValueWindow.add_with_viewport(self.keyTable)
        
        self.notebook = builder.get_object("notebook")
        self.window.show_all()

        

    def changepage_cb(self, notebook, page, page_num, data=None):
        p = self.notebook.get_nth_page(page_num)
        return True

    def combobox_changed_cb(self, combobox):
        active = combobox.get_active()
        if active >= 0:
            self.populateCap(self.alerts[self.ids[active]])
            self.index = active

    def comboBox2_changed_cb(self, combobox):
        active = combobox.get_active_iter()
        alert = self.treeStore.get_value(active, 0)
        self.populateCap(alert)

    def on_mainWindow_destroy(self, widget, data=None):
        Log.debug("Window killed, removing...")
        self.tray.window_quit_cb(self)

    def removeCap(self, alert):
        # TODO: Implement removal
        pass

    def acceptCap(self, alert):
        if isinstance(alert, cap.Alert):
            self.alerts[alert.id] = alert
            self.ids.append(alert.id)
            if len(alert.infos) > 0:
                self.comboBoxListStore.append((alert.getTitle(), alert.status, alert.msgType, alert.infos[0].urgency, alert.infos[0].severity, '/'))
            else:
                self.comboBoxListStore.append((alert.getTitle(), alert.status, alert.msgType, cap.Info.URGENCY_UNKNOWN, cap.Info.SEVERITY_UNKNOWN))

            p = filter(alert.match, self.parents)
            if len(p) is 0:
                iter = self.treeStore.append(None, [alert])
                self.parents.add(alert)
                self.parentiters[alert] = iter
            else:
                if len(p) is 1:
                    self.treeStore.append(self.parentiters[p[0]], [alert])
                else:
                    Log.warning("Multiple parents for CAP {0}! Splitting off...".format(alert.id))
                    self.treeStore.append(None, [alert])
                    self.parents.add(alert)
                    self.parentiters[alert] = iter
                    
                    
            if self.comboBox2.get_active() is -1:
                self.comboBox2.set_active(0)
                self.comboBox2_changed_cb(self.comboBox2)

        else:
            Log.error("Invalid class passed to acceptCap(): %s" % type(alert))

    def onNextClick(self, e):
        active = self.comboBox2.get_active_iter()
        next = self.treeStore.iter_next(active)
        if next is not None:
            alert = self.treeStore.get_value(next, 0)
            self.populateCap(alert)
            self.comboBox2.set_active_iter(next)

    def onPrevClick(self, e):
        active = self.comboBox2.get_active()
        if (active - 1) >= 0:
            self.comboBox2.set_active(active - 1)
            self.populateCap(self.treeStore.get_value(self.comboBox2.get_active_iter(), 0))
    
    def __populatePVTEC(self, info):
        if info.vtec is not None:
            if info.vtec.hasPVTEC:
                self.__alert('P-VTEC', str.format("{0} {1}", info.vtec.phenomena, info.vtec.significance))
                self.__alert('P-VTEC Class', info.vtec.product_class)
                self.__alert('P-VTEC Actions', info.vtec.actions)
                self.__alert('P-VTEC Office ID', info.vtec.office_id, url=str.format('http://www.wrh.noaa.gov/{0}/',info.vtec.office_id[len(info.vtec.office_id)-3:len(info.vtec.office_id)].lower()))
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
                if info.vtec.hasPVTEC:
                    self.__alert('H-VTEC Location ID', info.vtec.location_id, url=str.format('http://water.weather.gov/ahps2/hydrograph.php?wfo={0}&gage={1}',info.vtec.office_id[len(info.vtec.office_id)-3:len(info.vtec.office_id)],info.vtec.location_id))
                else:
                    self.__alert('H-VTEC Location ID', info.vtec.location_id)
                self.__alert('H-VTEC Flood Severity', info.vtec.flood_severity)
                self.__alert('H-VTEC Immediate Cause', info.vtec.immediate_cause)
                self.__alert('H-VTEC Flood Record Status', info.vtec.flood_record_status)
                
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
                tv.set_wrap_mode(gtk.WRAP_WORD)
                tv.set_editable(False)
                
                
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
                #file = open('../marker-simple.html')
                
#                self.webview.load_html_string(file.read(),'http://localhost/testing')
                for area in info.areas:
                    for polygon in area.polygons:
                        webview = webkit.WebView()
                        label = gtk.Label('Map')
                        pn = self.notebook.append_page(webview, label)
                        webview.show()
                        if hasattr(area,'areaDesc'):
                            webview.load_html_string(utils.mapPolygon(polygon, areaDesc=area.areaDesc),'http://localhost/testing')
                        else:
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
            self.__alert('Source CAP URL', alert.url, url=alert.url)
                        
        except AttributeError:
            Log.error("Attribute error while populating window from CAP {0}.".format(alert.id), exc_info=True)
        except:
            Log.error("Unexpected error while populating window from CAP {0}".format(alert.id), exc_info=True)            
