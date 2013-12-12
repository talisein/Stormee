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

from datetime import datetime
from datetime import timedelta
from dateutil import parser as dateparser
import dateutil
import logging 
import base64
import re
import utils
from dateutil import zoneinfo

DEFAULT_EXPIRES = timedelta(hours=24) # 24 hours

Log = logging.getLogger()

def unicodeToDatetime(text):
    #2002-05-24T16:49:00-07:00
    return dateparser.parse(text).astimezone(zoneinfo.gettz('UTC'))

class Alert:
        
    STATUS_ACTUAL = u'Actual' # Actionable by all targeted recipients
    STATUS_EXERCISE = u'Exercise' # Actionable only by designated exercise participants; exercise identifier should appear in <note>  
    STATUS_SYSTEM = u'System' # For messages that support alert network internal functions.
    STATUS_TEST = u'Test' # Technical testing only, all recipients disregard 
    STATUS_DRAFT = u'Draft' # A preliminary template or draft, not actionable in its current form. 
    
    MSGTYPE_ALERT = u'Alert' # - Initial information requiring attention by targeted recipients
    MSGTYPE_UPDATE = u'Update' # Updates and supercedes the earlier message(s) identified in <references>
    MSGTYPE_CANCEL = u'Cancel' # Cancels the earlier message(s) identified in <references>
    MSGTYPE_ACK = u'Ack' # Acknowledges receipt and acceptance of the message(s)) identified in <references>
    MSGTYPE_ERROR = u'Error' # ” indicates rejection of the message(s) identified in <references>; explanation SHOULD appear in <note>
    
    SCOPE_PUBLIC = u'Public'
    SCOPE_RESTRICTED = u'Restricted'
    SCOPE_PRIVATE = u'Private'
    
    def __init__(self):
        self.hasError = False
        self.codes = list()
        self.references = list()
        self.infos = list()
        self.id = None
        self.version = None
        self.sender = None
        self.sent = None
        self.status = None
        self.msgType = None
        self.source = None
        self.scope = None
        self.restriction = None
        self.addresses = None
        self.note = None
        self.incidents = None
        
    def getTitle(self):
        for info in self.infos:
            if info.vtec is not None and info.vtec.hasPVTEC:
                return str.format("{0} {1}", info.vtec.phenomena, info.vtec.significance)
            elif 'SAME' in info.eventCodes:
                return NWIS.expandNWIS(info.eventCodes['SAME'])
            elif info.event is not None:
                return info.event
            elif self.note is not None:
                return self.note[0:90]
            else:
                return self.id

    def __cmp__(self, other):
        if other.sent > self.sent:
            return -1
        elif other.sent < self.sent:
            return 1
        else:
            return 0
            
        
    def __hash__(self):
        if self.id is not None:
            return self.id.__hash__() ^ self.sent.__hash__()
        else:
            Log.debug("Hash got called on an alert without id...")
            return self.codes.__hash__()

    def match(self, alert):
        if self.incidents is not None and alert.incidents is not None and self.incidents == alert.incidents:
            return True
        for info in self.infos:
            for ainfo in alert.infos:
                if info.vtec is not None and ainfo.vtec is not None:
                    if info.vtec.match(ainfo.vtec):
                        return True
        return False

    def checkArea(self, type, code):
        for info in self.infos:
            for area in info.areas:
                if type in area.geoCodes:
                    if code in area.geoCodes[type]:
                        return True
        return False

    def checkUGC(self, state='CA', fips='06000', nws_zone='000'):
        for info in self.infos:
            for area in info.areas:
                if 'UGC' in area.geoCodes:
                    for ugc_string in area.geoCodes['UGC']:
                        if UGC.matchUGC(ugc_string, state, fips, nws_zone):
                            return True
                if 'FIPS6' in area.geoCodes:
                    for x in area.geoCodes['FIPS6']:
                        if len(x) > 5:
                            x = x[len(x)-5:len(x)]
                            if x == fips:
                                return True
                if 'FIPS' in area.geoCodes:
                    for x in area.geoCodes['FIPS']:
                        if len(x) > 5:
                            x = x[len(x)-5:len(x)]
                            if x == fips:
                                return True
        return False

    def checkCoords(self, coords):
        for info in self.infos:
            for area in info.areas:
                for circle in area.circles:
                    x, y, radius = circle
                    if utils.distance((x,y), coords) < radius:
                        return True
                for polygon in area.polygons:
                    x, y = coords
                    if utils.point_inside_polygon(x, y, polygon):
                        return True
        return False
        
    def setId(self, id):
        if id is not None:
            self.id = id.strip()
    
    @staticmethod
    def aboutId():
        return u'A number or string uniquely identifying this message, assigned by the sender.'
    
    def setVersion(self, namespace):
        elems = namespace.split(':')
        self.version = elems[len(elems)-1]
        if elems[0] != 'urn' or elems[1] != 'oasis' or elems[2] != 'names' or elems[3] != 'tc' or elems[4] != 'emergency' or elems[5] != 'cap':
            Log.warn("Unexpected namespace %s" % namespace)

    def setSender(self, sender):
        if sender is not None:
            self.sender = sender.strip()
        
    @staticmethod
    def aboutSender():
        return u'Identifies the originator of this alert. Guaranteed by assigner to be unique globally; e.g., may be based on an Internet domain name.'
        
    def setSent(self, sent):
        if type(sent) is unicode or type(sent) is str:
            self.sent = unicodeToDatetime(sent)
        elif type(sent) is datetime:
            self.sent = sent
        else:
            Log.error( _("Invalid datatype for sent (%s)") % sent.type  )
            self.hasError = True
    
    @staticmethod
    def aboutSent():
        return u'The time and date of the origination of the alert message.'
    
    def setStatus(self, status):
        if status is not None:
            status = status.strip()
            if status == u'Actual':
                self.status = Alert.STATUS_ACTUAL
            elif status == u'Exercise':
                self.status = Alert.STATUS_EXERCISE
            elif status == u'System':
                self.status = Alert.STATUS_SYSTEM
            elif status == u'Test':
                self.status = Alert.STATUS_TEST
            elif status == u'Draft':
                self.status = Alert.STATUS_DRAFT
            else:
                Log.error("Unknown CAP status \"%s\"" % status)
                self.hasError = True
            
    @staticmethod
    def aboutStatus(type=None):
        if type is None:
            return u'The code denoting the appropriate handling of the alert message.'
        elif type is Alert.STATUS_ACTUAL:
            return u'Actionable by all targeted recipients'
        elif type is Alert.STATUS_DRAFT:
            return u'Actionable only by designated exercise participants; exercise identifier should appear in <note>'
        elif type is Alert.STATUS_SYSTEM:
            return u'For messages that support alert network internal functions.'
        elif type is Alert.STATUS_TEST:
            return u'Technical testing only, all recipients disregard'
        elif type is Alert.STATUS_DRAFT:
            return u'A preliminary template or draft, not actionable in its current form.'
        else:
            return u'Invalid type'
        
    def setMsgType(self, msgType):
        if msgType is not None:
            msgType = msgType.strip()
            if msgType == u'Alert':
                self.msgType = Alert.MSGTYPE_ALERT
            elif msgType == u'Update':
                self.msgType = Alert.MSGTYPE_UPDATE
            elif msgType == u'Cancel':
                self.msgType = Alert.MSGTYPE_CANCEL
            elif msgType == u'Ack':
                self.msgType = Alert.MSGTYPE_ACK
            elif msgType == u'Error':
                self.msgType = Alert.MSGTYPE_ERROR
            else:
                Log.error("Unknown CAP message type \"%s\"" % msgType)
                self.hasError = True
        
    @staticmethod
    def aboutMsgType(type=None):
        if type is None:
            return u'The code denoting the nature of the alert message.'
        elif type is Alert.MSGTYPE_ALERT:
            return u'Initial information requiring attention by targeted recipients.'
        elif type is Alert.MSGTYPE_UPDATE:
            return u'Updates and supercedes the earlier message(s) identified in <references>.'
        elif type is Alert.MSGTYPE_CANCEL:
            return u'Cancels the earlier message(s) identified in <references>.'
        elif type is Alert.MSGTYPE_ACK:
            return u'Acknowledges receipt and acceptance of the message(s)) identified in <references>.'
        elif type is Alert.MSGTYPE_ERROR:
            return u'Indicates rejection of the message(s) identified in <references>; explanation should appear in <note>.'
        else:
            return u'Invalid type'
        
    def setSource(self, source):
        if source is not None:
            self.source = source.strip()
        
    @staticmethod
    def aboutSource():
        return u'The particular source of this alert; e.g., an operator or a specific device.'
    
    def setScope(self, scope):
        if scope is not None:
            scope = scope.strip()
            if scope == u'Public':
                self.scope = Alert.SCOPE_PUBLIC
            elif scope == u'Restricted':
                self.scope = Alert.SCOPE_RESTRICTED
            elif scope == u'Private':
                self.scope = Alert.SCOPE_PRIVATE
            else:
                Log.error("Unknown CAP scope \"%s\" % scope")
                self.hasError = True
            
    @staticmethod
    def aboutScope(scope=None):
        if scope is None:
            return u'The code denoting the intended distribution of the alert message.'
        elif scope is Alert.SCOPE_PUBLIC:
            return u'For general dissemination to unrestricted audience.'
        elif scope is Alert.SCOPE_RESTRICTED:
            return u'For dissemination only to users with a known operational requirement (see <restriction>).'
        elif scope is Alert.SCOPE_PRIVATE:
            return u'For dissemination only to specified addresses (see <address>).'
        else:
            return u'Invalid scope.'
        
    def setRestriction(self, restriction):
        if restriction is not None:
            self.restriction = restriction.strip()

    @staticmethod
    def aboutRestriction():
        return u'The text describing the rule for limiting distribution of the restricted alert message.'
        
    def setAddresses(self, addresses):
        # Multiple space-delimited addresses MAY be included.  Addresses including whitespace MUST be enclosed in double-quotes.
        if addresses is not None:
            addresses = addresses.strip()
            if unicode.count(addresses, u'"') > 0:
                Log.warning("CAP contains addresses with quotes. Parsing is unimplemented.")
            else:
                self.addresses = addresses.split(' ');
            self.addresses = addresses
        
    @staticmethod
    def aboutAddresses():
        return u'The group listing of intended recipients of the private alert message.'
        
    def addCode(self, code):
        if code is not None:
            #  Multiple instances MAY occur within a single <info> block
            self.codes.append(code.strip())
        
    @staticmethod
    def aboutCode():
        return u'The code denoting the special handling of the alert message.'
        
    def setNote(self, note):
        # The message note is primarily intended for use with  <status> “Exercise” and <msgType> “Error
        if note is not None:
            self.note = note.strip()

    @staticmethod
    def aboutNote():
        return u'The text describing the purpose or significance of the alert message.'
        
    def setReferences(self, references):
        #  The extended message identifier(s) (in the form sender,identifier,sent) of an earlier CAP message or messages referenced by this one.
        # If multiple messages are referenced, they SHALL be separated by whitespace.
        if references is None:
            return
        else:
            for reference in references.strip().split(' '):
                if reference.count(',') is 2:
                    (sender,identifier,sent) = reference.split(',')
                    self.references.append(identifier)
                else:
                    self.references.append(reference)
                    Log.warning("Reference '{0}' not valid to CAP 1.2 specification".format(reference))
                    
    @staticmethod
    def aboutReferences():
        return u'The group listing identifying earlier message(s) referenced by the alert message.'
        
    def setIncidents(self, incidents):
        # Used to collate multiple messages referring to different aspects of the same incident
        #  If multiple incident identifiers are referenced, they SHALL be separated by whitespace.  Incident names including whitespace SHALL be surrounded by double-quote
        if incidents is not None:
            self.incidents = incidents.strip()
        
    @staticmethod 
    def aboutIncidents():
        return u'The group listing naming the referent incident(s) of the alert message.'
        
    def addInfo(self, info):
        if info is not None:
            self.infos.append(info)

    def isExpired(self):
        for info in self.infos:
            if not info.isExpired():
                return False
        return True
            
class Info:
    # In addition to the specified subelements, MAY contain one or more <resource> blocks and/or one or more <area> blocks
    CATEGORY_GEO = 'Geo'
    CATEGORY_MET = 'Met'
    CATEGORY_SAFETY = 'Safety'
    CATEGORY_SECURITY = 'Security'
    CATEGORY_RESCUE = 'Rescue'
    CATEGORY_FIRE = 'Fire'
    CATEGORY_HEALTH = 'Health'
    CATEGORY_ENV = 'Env'
    CATEGORY_TRANSPORT = 'Transport'
    CATEGORY_INFRA = 'Infra'
    CATEGORY_CBRNE = 'CBRNE'
    CATEGORY_OTHER = 'Other'

    CATEGORIES = dict({
                       'Geo': CATEGORY_GEO,
                       'Met': CATEGORY_MET,
                       'Safety': CATEGORY_SAFETY,
                       'Security': CATEGORY_SECURITY,
                       'Rescue': CATEGORY_RESCUE,
                       'Fire': CATEGORY_FIRE,
                       'Health': CATEGORY_HEALTH,
                       'Env': CATEGORY_ENV,
                       'Transport': CATEGORY_TRANSPORT,
                       'Infra': CATEGORY_INFRA,
                       'CBRNE': CATEGORY_CBRNE,
                       'Other': CATEGORY_OTHER,
                       })

    ABOUT_CATEGORIES = dict({
                       None: 'The code denoting the category of the subject event of the alert message.',
                       CATEGORY_GEO: 'Geophysical (inc. landslide)',
                       CATEGORY_MET: 'Meteorological (inc. flood)',
                       CATEGORY_SAFETY: 'General emergency and public safety',
                       CATEGORY_SECURITY: 'Law enforcement, military, homeland and local/private security',
                       CATEGORY_RESCUE: 'Rescue and recovery',
                       CATEGORY_FIRE: 'Fire suppression and rescue',
                       CATEGORY_HEALTH: 'Medical and public health',
                       CATEGORY_ENV: 'Pollution and other environmental',
                       CATEGORY_TRANSPORT: 'Public and private transportation',
                       CATEGORY_INFRA: 'Utility, telecommunication, other non-transport infrastructure',
                       CATEGORY_CBRNE: 'Chemical, Biological, Radiological, Nuclear or High-Yield Explosive threat or attack',
                       CATEGORY_OTHER: 'Other events',
                       })

    RESPONSE_SHELTER = 'Shelter'
    RESPONSE_EVACUATE = 'Evacuate'
    RESPONSE_PREPARE = 'Prepare'
    RESPONSE_EXECUTE = 'Execute'
    RESPONSE_AVOID = 'Avoid'
    RESPONSE_MONITOR = 'Monitor'
    RESPONSE_ASSESS = 'Assess'
    RESPONSE_ALLCLEAR = 'All Clear'
    RESPONSE_NONE = 'None'

    RESPONSES = dict({
                      'Shelter': RESPONSE_SHELTER,
                      'Evacuate': RESPONSE_EVACUATE,
                      'Prepare': RESPONSE_PREPARE,
                      'Execute': RESPONSE_EXECUTE,
                      'Avoid': RESPONSE_AVOID,
                      'Monitor': RESPONSE_MONITOR,
                      'Assess': RESPONSE_ASSESS,
                      'All Clear': RESPONSE_ALLCLEAR,
                      'None': RESPONSE_NONE,
                      })
    
    ABOUT_RESPONSES = dict({
                            None: 'The code denoting the type of action recommended for the target audience.',
                            RESPONSE_SHELTER: 'Take shelter in place or per <instruction>',
                            RESPONSE_EVACUATE: 'Relocate as instructed in the <instruction>',
                            RESPONSE_PREPARE: 'Make preparations per the <instruction>',
                            RESPONSE_EXECUTE: 'Execute a pre-planned activity identified in <instruction>',
                            RESPONSE_AVOID: 'Avoid the subject event as perthe <instruction>',
                            RESPONSE_MONITOR: 'Attend to information sources as described in <instruction>',
                            RESPONSE_ASSESS: 'Evaluate the information in this message',
                            RESPONSE_ALLCLEAR: 'The subject event no longer poses a threat or concern and any follow on action is described in <instruction>',
                            RESPONSE_NONE: 'No action recommended',
                            })
    
    URGENCY_IMMEDIATE = u'Immediate'
    URGENCY_EXPECTED = u'Expected'
    URGENCY_FUTURE = u'Future'
    URGENCY_PAST = u'Past'
    URGENCY_UNKNOWN = u'Unknown'
    
    SEVERITY_EXTREME = u'Extreme'
    SEVERITY_SEVERE = u'Severe'
    SEVERITY_MODERATE = u'Moderate'
    SEVERITY_MINOR = u'Minor'
    SEVERITY_UNKNOWN = u'Unknown'
    
    CERTAINTY_OBSERVED = u'Observed'
    CERTAINTY_LIKELY = u'Likely'
    CERTAINTY_POSSIBLE = u'Possible'
    CERTAINTY_UNLIKELY = u'Unlikely'
    CERTAINTY_UNKNOWN = u'Unknown'
    
    def __init__(self):
        self.language = u'en-US'
        self.categories = set()
        self.responseTypes = set()
        self.eventCodes = dict()
        self.parameters = dict()
        self.resources = list()
        self.areas = list()
        self.event = None
        self.urgency = None
        self.severity = None
        self.certainty = None
        self.audience = None
        self.effective = None
        self.onset = None
        self.expires = None
        self.senderName = None
        self.headline = None
        self.description = None
        self.instruction = None
        self.web = None
        self.contact = None
        self.vtec = None
        
    def setLanguage(self, language):
        if len(language) > 0:
            self.language = language.strip()
        else:
            self.language = u'en-US'
            
    @staticmethod
    def aboutLanguage():
        return u'The code denoting the language of the info subelement of the alert message'


    def addCategory(self, category):
        if category is not None:
            category = category.strip()
            if category in Info.CATEGORIES:
                self.categories.add(Info.CATEGORIES[category])
            else:
                Log.error("Unknown category {0}".format(category))

    @staticmethod
    def aboutCategory(category=None):
        if category in Info.ABOUT_CATEGORIES:
            return Info.ABOUT_CATEGORIES[category]
        else:
            return "No explanation for category {0}".format(category)

    def setEvent(self, event):
        if event is not None:
            self.event = event.strip()

    @staticmethod
    def aboutEvent():
        return u'The text denoting the type of the subject event of the alert message.'


    def addResponseType(self, responseType):
        if responseType is not None:
            responseType = responseType.strip()
            if responseType in Info.RESPONSES:
                self.responseTypes.add(Info.RESPONSES[responseType])
            else:
                Log.error("Invalid reponseType \"%s\"" % responseType)
    
    @staticmethod
    def aboutResponseType(responseType=None):
        if responseType in Info.ABOUT_RESPONSES:
            return Info.ABOUT_RESPONSES[responseType]
        else:
            return "No explanation for category {0}".format(responseType)
        
    def setUrgency(self, urgency):
        if urgency is not None:
            urgency = urgency.strip()
            if urgency == u'Immediate':
                self.urgency = Info.URGENCY_IMMEDIATE
            elif urgency == u'Expected':
                self.urgency = Info.URGENCY_EXPECTED
            elif urgency == u'Future':
                self.urgency = Info.URGENCY_FUTURE
            elif urgency == u'Past':
                self.urgency = Info.URGENCY_PAST
            elif urgency == u'Unknown':
                self.urgency = Info.URGENCY_UNKNOWN
            else:
                Log.error("Invalid urgency \"%s\"" % urgency)
            
    @staticmethod
    def aboutUrgency(urgency=None):
        if urgency is None:
            return u'The code denoting the urgency of the subject event of the alert message.'
        elif urgency is Info.URGENCY_IMMEDIATE:
            return u'Responsive action should be taken immediately.'
        elif urgency is Info.URGENCY_EXPECTED:
            return u' Responsive action should be taken soon (within next hour).'
        elif urgency is Info.URGENCY_FUTURE:
            return u'Responsive action should be taken in the near future.'
        elif urgency is Info.URGENCY_PAST:
            return u'Responsive action is no longer required.'
        elif urgency is Info.URGENCY_UNKNOWN:
            return u'Urgency not known.'
        else:
            return "Unknown urgency \"%s|"" % urgency"
        
    def setSeverity(self, severity):
        if severity is not None:
            severity = severity.strip()
            if severity == u'Extreme':
                self.severity = Info.SEVERITY_EXTREME
            elif severity == u'Severe':
                self.severity = Info.SEVERITY_SEVERE
            elif severity == u'Moderate':
                self.severity = Info.SEVERITY_MODERATE
            elif severity == u'Minor':
                self.severity = Info.SEVERITY_MINOR
            elif severity == u'Unknown':
                self.severity = Info.SEVERITY_UNKNOWN
            else:
                Log.error("Invalid severity \"%s\"" % severity)
            
    @staticmethod
    def aboutSeverity(severity=None):
        if severity is None:
            return u'The code denoting the severity of the subject event of the alert message.'
        elif severity is Info.SEVERITY_EXTREME:
            return u'Extraordinary threat to life or property.'
        elif severity is Info.SEVERITY_SEVERE:
            return u'Significant threat to life or property.'
        elif severity is Info.SEVERITY_MODERATE:
            return u'Possible threat to life or property.'
        elif severity is Info.SEVERITY_MINOR:
            return u'Minimal to no known threat to life or property.'
        elif severity is Info.SEVERITY_UNKNOWN:
            return u'Severity unknown.'
        else:
            return "Unknown severity \"%s\"" % severity

    def setCertainty(self, certainty):
        if certainty is not None:
            certainty = certainty.strip()
            if certainty == u'Observed':
                self.certainty = Info.CERTAINTY_OBSERVED
            elif certainty == u'Likely':
                self.certainty = Info.CERTAINTY_LIKELY
            elif certainty == u'Possible':
                self.certainty = Info.CERTAINTY_POSSIBLE
            elif certainty == u'Unlikely':
                self.certainty = Info.CERTAINTY_UNLIKELY
            elif certainty == u'Unknown':
                self.certainty = Info.CERTAINTY_UNKNOWN
            elif certainty == u'Very Likely' or certainty == u'VeryLikely':
                self.certainty = Info.CERTAINTY_LIKELY
            else:
                Log.error("Invalid certainty \"%s\"" % certainty)
            
    @staticmethod
    def aboutCertainty(certainty=None):
        if certainty is None:
            return u'The code denoting the certainty of the subject event of the alert message.'
        elif certainty is Info.CERTAINTY_OBSERVED:
            return u'Determined to have occurred or to be ongoing.'
        elif certainty is Info.CERTAINTY_LIKELY:
            return u'Likely (p > ~50%).'
        elif certainty is Info.CERTAINTY_POSSIBLE:
            return u'Possible but not likely (p <= ~50%).'
        elif certainty is Info.CERTAINTY_UNLIKELY:
            return u'Not expected to occur (p ~ 0).'
        elif certainty is Info.CERTAINTY_UNKNOWN:
            return u'Certainty unknown.'
        else:
            return "Unknown certainty \"%s\"" % certainty


    def setAudience(self,audience):
        if audience is not None:
            self.audience = audience.strip()
        
    @staticmethod
    def aboutAudience():
        return u'The text describing the intended audience of the alert message.'

    def addEventCode(self, key, value):
        if key is not None and value is not None:
            self.eventCodes[key.strip()] = value.strip()

    @staticmethod
    def aboutEventCode():
        return u'A system specific code identifying the event type of the alert message.'
    
    def setEffective(self, effective):
        self.effective = unicodeToDatetime(effective)
        
    @staticmethod
    def aboutEffective():
        return u'The effective time of the information of the alert message.'

    def setOnset(self, onset):
        self.onset = unicodeToDatetime(onset)
        
    @staticmethod
    def aboutOnset():
        return u'The expected time of the beginning of the subject event of the alert message.'

    def setExpires(self, expires):
        self.expires = unicodeToDatetime(expires)
    
    def isExpired(self):
        return datetime.now(zoneinfo.gettz('UTC')) > self.expires.astimezone(zoneinfo.gettz('UTC'))

    @staticmethod
    def aboutExpires():
        return u'The expiry time of the information of the alert message.'

    def setDefaultExpires(self):
        self.expires = self.effective + DEFAULT_EXPIRES

    def setSenderName(self, senderName):
        if senderName is not None:
            self.senderName = senderName.strip()

    @staticmethod
    def aboutSenderName():
        return u'The human-readable name of the agency or authority issuing this alert.'

    def setHeadline(self, headline):
        if headline is not None:
            self.headline = headline.strip()

    @staticmethod
    def aboutHeadline():
        return u'A brief human-readable headline.'

    def setDescription(self, description):
        if description is not None and len(description) > 0:
            self.description = description.strip()
        else:
            self.description = "NO DESCRIPTION"

    @staticmethod
    def aboutDescription():
        return u'An extended human readable description of the hazard or event that occasioned this message.'
    
    def setInstruction(self, instruction):
        if instruction is not None and len(instruction) > 0:
            self.instruction = instruction.strip()
        else:
            self.instruction = "NO INSTRUCTIONS"
            
    @staticmethod
    def aboutInstruction():
        return u'An extended human readable instruction to targeted recipients.'
    
    def setWeb(self, web):
        if web is not None:
            self.web = web.strip()
            
    @staticmethod
    def aboutWeb():
        return u'A full, absolute URI for an HTML page or other text resource with additional or reference information regarding this alert.'
    
    def setContact(self, contact):
        if contact is not None:
            self.contact = contact.strip()
    
    @staticmethod
    def aboutContact():
        return u'The text describing the contact for follow-up and confirmation of the alert message'
    
    def addParameter(self, key, value):
        # TODO:
        # Messages intended for EAS and/or HazCollect dissemination MUST include an instance of  <parameter> with a <valueName> of "EAS-ORG" with a <value> of the originator’s  SAME organization code.  
        # Messages invoking the "Gubernatorial Must-Carry" rule MUST include a <parameter> with <valueName> of "EAS-Must-Carry" and value of "TRUE" for gubernatorial alerts.
        # Messages intended for CMAS dissemination MAY include an instance of <parameter> with a <valueName> of "CMAMtext" and a <value> containing free form text limited in length to 90 English characters.

        # TODO: 
        # WMOHEADER info: http://www.weather.gov/tg/headef.html
        if key is not None and value is not None:
            self.parameters[key.strip()] = value.strip()

    
    @staticmethod
    def aboutParameter():
        return u'A system specific additional parameter associated with the alert message'

    def setVTEC(self, vtec):
        self.vtec = VTEC(vtec)
        
    def addResource(self, resource):
        if resource is not None:
            self.resources.append(resource.strip())

    def addArea(self, area):
        self.areas.append(area)
        
class Resource:
    def setResourceDesc(self, resourceDesc):
        if resourceDesc is not None:
            self.resourceDesc = resourceDesc.strip()
            Log.info("A resource is attached to this CAP.")

    @staticmethod
    def aboutResourceDesc():
        return u'The human-readable text describing the type and content, such as “map” or “photo”, of the resource file.'
    
    def setMimeType(self, mimeType):
        if mimeType is not None:
            self.mimeType = mimeType.strip()

    @staticmethod
    def aboutMimeType():
        return u'The identifier of the MIME content type and sub-type describing the resource file'
    
    def setSize(self, size):
        self.size = long(size)
    
    @staticmethod
    def aboutSize():
        return u'Approximate size of the resource file in bytes.'
    
    def setUri(self, uri):
        if uri is not None:
            self.uri = uri.strip()

    @staticmethod
    def aboutUri():
        return u'A full absolute URI, typically a Uniform Resource Locator that can be used to retrieve the resource over the Internet OR a relative URI to name the content of a <derefUri> element if one is present in this resource block'
    
    def setDerefUri(self, derefUri):
        self.derefUri = base64.b64decode(derefUri)
    
    @staticmethod
    def aboutDerefUri():
        return u'The data content of the resource file.'
    
    def setDigest(self, digest):
        self.digest = digest
        
    @staticmethod
    def aboutDigest():
        return u'The code representing the digital digest (“hash”) computed from the resource file. Computed using SHA-1.'
    
class Area:
    def __init__(self):
        self.polygons = list()
        self.circles = list()
        self.geoCodes = dict()
        self.areaDesc = None
        
    def setAreaDesc(self, areaDesc):
        self.areaDesc = areaDesc

    @staticmethod
    def aboutAreaDesc():
        return u'A text description of the affected area.'
    
    def addPolygon(self, polygon):
        if polygon is not None:
            p = list()
            for x in polygon.split(' '):
                count = x.count(',')
                if count is 1:
                    (lat,longitude) = x.split(',')
                    p.append((float(lat),float(longitude)))
                elif count is 0:
                    pass
                else:
                    Log.warning("Found too many commas in coordinates for polygon '{0}' at {1}".format(polygon, x))
            self.polygons.append(p)
             
    @staticmethod
    def aboutPolygon():
        return u'The geographic polygon is represented by a whitespace-delimited list of [WGS 84] coordinate pairs.'    
    
    def addCircle(self, circle):
        if circle is not None:
            (coords,radius) = circle.split(' ')
            (lat,longitude) = coords.split(',')
            self.circles.append((float(lat),float(longitude), float(radius)))

    @staticmethod
    def aboutCircle():
        return u'The circular area is represented by a central point given as a [WGS 84] coordinate pair followed by a space character and a radius value in kilometers.'
        
    def addGeoCode(self, key, value):
        # TODO:
        # (1) At least one instance of <geocode> with a <valueName> of “SAME” and a value of a SAME 6-digit location (extended FIPS) SHOULD be used. 
        # (2) The more precise geospatial representations of the area, <polygon> and <circle>, SHOULD also be used whenever possible.
        # (3) A SAME value of “000000” refers to ALL United States territory or territories.
        if key in self.geoCodes:
            x = self.geoCodes[key]
            x.append(value)
            self.geoCodes[key] = x
        else:
            x = list()
            x.append(value)
            self.geoCodes[key] = x
    
    @staticmethod
    def aboutGeoCode():
        return u'Any geographically-based code to describe a message target area'
    
    def setAltitude(self, altitude):
        self.altitude = long(altitude)
        
    @staticmethod
    def aboutAltitude():
        return u'If used with the <ceiling> element this value is the lower limit of a range. Otherwise, this value specifies a specific altitude. The altitude measure is in feet above mean sea level per the [WGS 84] datum.'
    
    def setCeiling(self, ceiling):
        self.ceiling = long(ceiling)
        
    @staticmethod
    def aboutCeiling():
        return u'The maximum altitude of the affected area of the alert message.'
    
class NWIS:
    # per NATIONAL WEATHER SERVICE INSTRUCTION 10-518
    # http://www.weather.gov/directives/sym/pd01005018curr.pdf
    # and FCC EAS Rules 47 CFR 11.31, EAS Protocol
    # http://ecfr.gpoaccess.gov/cgi/t/text/text-idx?c=ecfr&sid=e95bd2661c20ee82ede21961e6f2f3bd&rgn=div5&view=text&node=47:1.0.1.1.11&idno=47#47:1.0.1.1.11.2.239.1
    # Note there are Spanish translations for some of these at http://www.weather.gov/directives/010/pd01017012c.pdf
    nwis = dict({'ADR': 'Administrative Message',
                 'AVA': 'Avalanche Warning',
                 'AVW': 'Avalanche Watch',
                 'CAE': 'Child Abduction Emergency',
                 'CDW': 'Civil Danger Warning',
                 'CEM': 'Civil Emergency Message',
                 'EQW': 'Earthquake Warning',
                 'EVI': 'Evacuate Immediate',
                 'FRW': 'Fire Warning',
                 'RWT': 'Required Weekly Test',
                 'NPT': 'National Periodic Test',
                 'HMW': 'Hazardous Materials Warning',
                 'LEW': 'Law Enforcement Warning',
                 'LAE': 'Local Area Emergency',
                 'NUW': 'Nuclear Power Plant Warning',
                 'RHW': 'Radiological Hazard Warning',
                 'SPW': 'Shelter In Place Warning',
                 'TOE': '911 Telephone Outage Warning',
                 'VOW': 'Volcano Warning',
                 'DMO': 'Practice/Demo Warning',
                 'RMT': 'Required Monthly Test',
                 'NST': 'National Silent Test',
                 'NMN': 'Network Message Notification', # End NWSI 10-518
                 'EAN': 'Emergency Action Notification (National only)',
                 'EAT': 'Emergency Action Termination (National only)',
                 'NIC': 'National Information Center',
                 'RMT': 'Required Monthly Test',
                 'BZW': 'Blizzard Warning',
                 'CFW': 'Coastal Flood Watch',
                 'CFA': 'Coastal Flood Advisory',
                 'DSW': 'Dust Storm Watch',
                 'FFW': 'Flash Flood Warning',
                 'FFA': 'Flash Flood Watch',
                 'FFS': 'Flash Flood Statement',
                 'FLW': 'Flood Warning',
                 'FLA': 'Flood Watch',
                 'FLS': 'Flood Statement',
                 'HWW': 'High Wind Warning',
                 'HWA': 'High Wind Watch',
                 'HUW': 'Hurricane Warning',
                 'HUA': 'Hurricane Watch',
                 'HLS': 'Hurricane Statement',
                 'SVR': 'Severe Thunderstorm Warning',
                 'SVA': 'Severe Thunderstorm Watch',
                 'SVS': 'Severe Weather Statement',
                 'SMW': 'Special Marine Warning',
                 'SPS': 'Special Weather Statement',
                 'TOR': 'Tornado Warning',
                 'TOA': 'Tornado Watch',
                 'TRW': 'Tropical Storm Warning',
                 'TRA': 'Tropical Storm Watch',
                 'TSW': 'Tsunami Warning',
                 'TSA': 'Tsunami Watch',
                 'WSW': 'Winter Storm Warning',
                 'WSA': 'Winter Storm Watch',
                 'LAE': 'Local Area Emergency',
                 'TXF': 'Transmitter Carrier Off', # TX? should never be seen. But just in case...
                 'TXO': 'Transmitter Carrier On',
                 'TXB': 'Transmitter Backup On',
                 'TXP': 'Transmitter Primary On',
                 'X5': 'Attempt to Locate Missing Person', # Can't find official source for this code!
                 })
    
    nwis_detail = dict({'ADR': 'A non-emergency message providing updated information about an event in progress, an event that has expired or concluded early, pre-event preparation or mitigation activities, post-event recovery operations, or other administrative matters pertaining to the Emergency Alert System.',
                        'AVA': 'A message issued by authorized officials when conditions are forecast to become favorable for natural or human-triggered avalanches that could affect roadways, structures, or backcountry activities.',
                        'AVW': 'A warning of current or imminent avalanche activity when  avalanche danger is considered high or extreme.',
                        'CAE': 'An emergency message, based on established criteria, about a missing child believed to be abducted.',
                        'CDW': 'A warning of an event that presents a danger to a significant civilian population.',
                        'CEM': 'An emergency message regarding an in-progress or imminent significant threat(s) to public safety and/or property.',
                        'EQW': 'A warning of current or imminent earthquake activity.',
                        'EVI': 'A warning where immediate evacuation is recommended or ordered according to state law or local ordinance.',
                        'FRW': 'A warning of a spreading structural fire or wildfire that threatens a populated area.',
                        'HMW': 'A warning of the release of a non-radioactive hazardous material (such as a flammable gas, toxic chemical, or biological agent) that may recommend evacuation (for an explosion, fire or oil spill hazard) or shelter-in-place (for a toxic fume hazard).',
                        'LEW': 'A warning of a bomb explosion, riot, or other criminal event (e.g. a jailbreak).',
                        'LAE': 'An emergency message that defines an event that, by itself, does not pose a significant threat to public safety and/or property.',
                        'NMN': 'Not yet defined and not in suite of products for relay by NWS.',
                        'TOE': 'An emergency message that defines a local or state 9-1-1 telephone network outage by geographic area or telephone exchange',
                        'NUW': 'A warning of an event at a nuclear power plant classified as a Site Area Emergency or General Emergency by the Nuclear Regulatory Commission (NRC)',
                        'RHW': 'A warning of the loss, discovery, or release of a radiological hazard.',
                        'SPW': 'A warning of an event where the public is recommended to shelter in place (go inside, close doors and windows, turn off air conditioning or heating systems, and turn on the radio or TV for more information)',
                        'VOW': 'A warning of current or imminent volcanic activity.',
                        })
    
    same_definitions = dict({'Warning': 'Warning messages are issued for those events that alone pose a significant threat to public safety and/or property, probability of occurrence and location is high, and the onset time is relatively short.',
                             'Watch': 'Watch messages are issued for those events that meet the classification of a warning, but either the onset time, probability of occurrence, or location is uncertain.',
                             'Emergency': 'Emergency messages are issued for those events that by themselves would not kill or injure or do property damage but indirectly may cause other things to happen that result in a hazard. For example, a major power or telephone loss in a large city alone is not a direct hazard but disruption to other critical services could create a variety of conditions that could directly threaten public safety.',
                             'Statement': 'Statements messages contain follow up information for warning, watch, or emergency messages.',
                             })
    @staticmethod
    def aboutNWIS(nwis):
        if nwis.upper() in NWIS.nwis_detail:
            return NWIS.nwis_detail[nwis.upper()]
        else:
            if len(nwis) is 3:
                if nwis[2] == 'W':
                    return NWIS.same_definitions['Warning']
                elif nwis[2] == 'A':
                    return NWIS.same_definitions['Watch']
                elif nwis[2] == 'E':
                    return NWIS.same_definitions['Emergency']
                elif nwis[2] == 'S':
                    return NWIS.same_definitions['Statement']
            return 'No detail available for this message type.'
        
    @staticmethod
    def expandNWIS(nwis):
        if nwis.upper() in NWIS.nwis:
            return NWIS.nwis[nwis.upper()]
        else:
            return nwis
class VTEC:
    # http://www.weather.gov/om/vtec/
    PRODUCT_CLASSES = dict({'O': 'Operational Product',
                  'T': 'Test Product',
                  'E': 'Experimental Product',
                  'X': 'Experimental VTEC in an Operational Product'
        })
    SIGNIFICANCES = dict({'W': 'Warning',
                         'A': 'Watch',
                         'Y': 'Advisory',
                         'S': 'Statement',
                         'F': 'Forecast',
                         'O': 'Outlook',
                         'N': 'Synopsis',
                         })
    ACTIONS = dict({'NEW': 'New Event',
                    'CON': 'Event Continued',
                    'EXT': 'Event Extended (Time)',
                    'EXA': 'Event Extended (Area)',
                    'EXB': 'Event Extended (Time and Area)',
                    'UPG': 'Upgraded',
                    'CAN': 'Event Canceled',
                    'EXP': 'Event Expired',
                    'COR': 'Correction',
                    'ROU': 'Routine',
                    })
    PHENOMENAS = dict({
                      'AF': 'Ashfall',
                      'AS': 'Air Stagnation',
                      'BS': 'Blowing Snow',
                      'BW': 'Brisk Wind',
                      'BZ': 'Blizzard',
                      'CF': 'Coastal Flood',
                      'DS': 'Dust Storm',
                      'DU': 'Blowing Dust',
                      'EC': 'Extreme Cold',
                      'EH': 'Extreme Heat',
                      'EW': 'Extreme Wind',
                      'FA': 'Areal Flood',
                      'FF': 'Flash Flood',
                      'FG': 'Dense Fog',
                      'FL': 'Flood',
                      'FR': 'Frost',
                      'FW': 'Fire Weather',
                      'FZ': 'Freeze',
                      'GL': 'Gale',
                      'HF': 'Hurricane Force Wind',
                      'HI': 'Inland Hurricane',
                      'HS': 'Heavy Snow',
                      'HT': 'Heat',
                      'HU': 'Hurricane',
                      'HW': 'High Wind',
                      'HY': 'Hydrologic',
                      'HZ': 'Hard Freeze',
                      'IP': 'Sleet',
                      'IS': 'Ice Storm',
                      'LB': 'Lake Effect Snow and Blowing Snow',
                      'LE': 'Lake Effect Snow',
                      'LO': 'Low Water',
                      'LS': 'Lakeshore Flood',
                      'LW': 'Lake Wind',
                      'MA': 'Marine',
                      'RB': 'Small Craft for Rough Bar',
                      'SB': 'Snow and Blowing Snow',
                      'SC': 'Small Craft',
                      'SE': 'Hazardous Seas',
                      'SI': 'Small Craft for Winds',
                      'SM': 'Dense Smoke',
                      'SN': 'Snow',
                      'SR': 'Storm',
                      'SU': 'High Surf',
                      'SV': 'Severe Thunderstorm',
                      'SW': 'Small Craft for Hazardous Seas',
                      'TI': 'Inland Tropical Storm',
                      'TO': 'Tornado',
                      'TR': 'Tropical Storm',
                      'TS': 'Tsunami',
                      'TY': 'Typhoon',
                      'UP': 'Ice Accretion',
                      'WC': 'Wind Chill',
                      'WI': 'Wind',
                      'WS': 'Winter Storm',
                      'WW': 'Winter Weather',
                      'ZF': 'Freezing Fog',
                      'ZR': 'Freezing Rain',
                      })
    
    FLOOD_SEVERITIES = dict({
                           'N': 'None',
                           '0': 'Areal Flood or Flash Flood Product',
                           '1': 'Minor',
                           '2': 'Moderate',
                           '3': 'Major',
                           'U': 'Unknown'
                           })
    
    IMMEDIATE_CAUSES = dict({
                            'ER': 'Excessive Rain',
                            'SM': 'Snow Melt',
                            'RS': 'Rain and Snow Melt',
                            'DM': 'Dam or Levee Failure',
                            'IJ': 'Ice Jam',
                            'GO': 'Glacier-Dammed Lake Outburst',
                            'IC': 'Rain and/or Snowmelt and/or Ice Jam',
                            'FS': 'Upstream Flooding plus Storm Surge',
                            'FT': 'Upstream Flooding plus Tidal Effects',
                            'ET': 'Elevated Upstream Flow plus Tidal Effects',
                            'WT': 'Wind and/or Tidal Effects',
                            'DR': 'Upstream Dam or Reservior Release',
                            'MC': 'Multiple Causes',
                            'OT': 'Other Effects',
                            'UU': 'Unknown'
                            })
    
    FLOOD_RECORD_STATUSES = dict({
                                'NO': 'A record flood is not expected',
                                'NR': 'Near record or record flood expected',
                                'UU': 'Flood without a period of record to compare',
                                'OO': 'For areal flood warnings, areal flash flood products, and flood advisories (point and real)'
                                })
    @staticmethod
    def getProductClass(pc):
        if pc is not None:
            if pc.upper() in VTEC.PRODUCT_CLASSES:
                return VTEC.PRODUCT_CLASSES[pc.upper()]
            else:
                Log.warning('Unknown VTEC product class {0}'.format(pc))
        return 'Unknown Product Class'
    
    @staticmethod
    def getSignificance(sig):
        if sig is not None:
            if sig.upper() in VTEC.SIGNIFICANCES:
                return VTEC.SIGNIFICANCES[sig.upper()]
            else:
                Log.warning('Unknown VTEC SIGNIFICANCES {0}'.format(sig))
        return 'Unknown Significance'
    
    @staticmethod
    def getActions(act):
        if act is not None:
            if act.upper() in VTEC.ACTIONS:
                return VTEC.ACTIONS[act.upper()]
            else:
                Log.warning('Unknown VTEC action {0}'.format(act))
        return 'Unknown Actions'
    
    @staticmethod
    def getPhenomena(pp):
        if pp is not None:
            if pp.upper() in VTEC.PHENOMENAS:
                return VTEC.PHENOMENAS[pp.upper()]
            else:
                Log.warning('Unknown VTEC phenomena {0}'.format(pp))
        return 'Unknown Phenomena'
    
    @staticmethod
    def getFloodSeverity(sev):
        if sev is not None:
            if sev in VTEC.FLOOD_SEVERITIES:
                return VTEC.FLOOD_SEVERITIES[sev]
            else:
                Log.warning('Unknown VTEC Flood Severity {0}'.format(sev))
        return 'Unknown Severity'
    
    @staticmethod
    def getImmediateCause(ic):
        if ic is not None:
            if ic.upper() in VTEC.IMMEDIATE_CAUSES:
                return VTEC.IMMEDIATE_CAUSES[ic.upper()]
            else:
                Log.warning("Unknown VTEC Immediate Cause {0}".format(ic))
        return "Unknown Cause"
    
    @staticmethod
    def getFloodRecordStatus(frs):
        if frs is not None:
            if frs.upper() in VTEC.FLOOD_RECORD_STATUSES:
                return VTEC.FLOOD_RECORD_STATUSES[frs.upper()]
            else:
                Log.warning("Unknown Flood Record Status {0}".format(frs))
        return 'Unknown record status'
    
    def __init__(self, vtec=""):
        self.hasPVTEC = False
        self.hasHVTEC = False
        self.populateVTEC(vtec)
        
    def match(self, vtec):
        if vtec is not None:
            if self.hasPVTEC and vtec.hasPVTEC:
                return self.office_id == vtec.office_id and self.phenomena == vtec.phenomena and self.significance == vtec.significance and self.event_tracking_number == vtec.event_tracking_number
            elif self.hasHVTEC and vtec.hasHVTEC:
                pass # TODO
                Log.debug("Comparing VTECs that don't have PVTEC but do have HVTEC!")
            else:
                return False
        return False
    
    def populatePVTEC(self, vtec):
        vtec = vtec.strip(' /')
        pclass, actions, self.office_id, phenomena, significance, self.event_tracking_number, begin, end = re.split('[.-]',vtec)
        self.product_class = VTEC.getProductClass(pclass)
        self.actions = VTEC.getActions(actions)
        self.phenomena = VTEC.getPhenomena(phenomena)
        self.significance = VTEC.getSignificance(significance)
        self.begin = None
        self.end = None
        
        try:
            if begin != '000000T0000Z':
                self.begin = datetime.strptime(begin,"%y%m%dT%H%MZ").replace(tzinfo=dateutil.tz.gettz('UTC'))
        except:
            Log.error("Invalid P-VTEC Event Beginning {0}".format(begin))
            
        try:
            if end != '000000T0000Z':
                self.end = datetime.strptime(end,"%y%m%dT%H%MZ").replace(tzinfo=dateutil.tz.gettz('UTC'))
        except:
            Log.error("Invalid P-VTEC Event End {0}".format(end))
        self.hasPVTEC = True
            
    def populateHVTEC(self, vtec):
        vtec = vtec.strip(' /')
        self.location_id = vtec[0:5]
        self.flood_severity =  VTEC.getFloodSeverity(vtec[6])
        self.immediate_cause =  VTEC.getImmediateCause(vtec[8:10])
        self.flood_begin = None
        self.flood_crest = None
        self.flood_end = None
        
        try:
            if vtec[11:23] != '000000T0000Z':
                self.flood_begin = datetime.strptime(vtec[11:23],"%y%m%dT%H%MZ").replace(tzinfo=dateutil.tz.gettz('UTC'))
            else:
                self.flood_begin = None
        except:
            Log.error("Invalid H-VTEC Crest Begin Time {0}".format(vtec[11:23]))
        
        try:
            if vtec[24:36] != '000000T0000Z':
                self.flood_crest = datetime.strptime(vtec[24:36],"%y%m%dT%H%MZ").replace(tzinfo=dateutil.tz.gettz('UTC'))   
            else:
                self.flood_crest = None
        except:
            Log.error("Invalid H-VTEC Flood Crest Time {0}".format(vtec[24:36]))

        try:
            if vtec[37:49] != '000000T0000Z':
                self.flood_end = datetime.strptime(vtec[37:49],"%y%m%dT%H%MZ").replace(tzinfo=dateutil.tz.gettz('UTC'))
            else:
                self.flood_end = None
        except:
            Log.error("Invalid H-VTEC Flood End Time {0}".format(vtec[37:49]))
            
        self.flood_record_status = VTEC.getFloodRecordStatus(vtec[50:52])
        self.hasHVTEC = True

    def populateVTEC(self, vtec):
        if vtec is not None:
            for chunk in vtec.split('/'):
                if len(chunk) is 46:
                    self.populatePVTEC(chunk)
                elif len(chunk) is 52:
                    self.populateHVTEC(chunk)
        return self.hasHVTEC or self.hasPVTEC
    
    def combine(self, vtec):
        if not self.hasHVTEC and vtec.hasHVTEC:
            self.location_id = vtec.location_id
            self.flood_severity =  vtec.flood_severity
            self.immediate_cause =  vtec.immediate_cause
            self.flood_begin = vtec.flood_begin
            self.flood_crest = vtec.flood_crest
            self.flood_end = vtec.flood_end
            self.flood_record_status = vtec.flood_record_status
            self.hasHVTEC = True
        if not self.hasPVTEC and vtec.hasPVTEC:
            self.product_class = vtec.product_class
            self.actions = vtec.actions
            self.phenomena = vtec.phenomena
            self.significance = vtec.significance
            self.begin = vtec.begin
            self.end = vtec.end
            self.hasPVTEC = True
            self.office_id = vtec.office_id
            self.event_tracking_number = vtec.event_tracking_number

class UGC:
    FORMAT_FIPS = object()
    FORMAT_ZONE = object()
    FORMATS = dict({
                    'C': FORMAT_FIPS,
                    'Z': FORMAT_ZONE
                    })
    
    @staticmethod
    def matchUGC(ugc, state, FIPS='000', nws_zone='000'):
        '''
        ugc: Full UGC string
        state: 2 letter string, post office ugc_state abbreviation
        '''
        if len(FIPS) > 3:
            FIPS = FIPS[len(FIPS)-3:len(FIPS)]
        ugc_state = None
        ugc_format = None
        if ugc is not None:
            for segment in ugc.split('-'):
                if segment[0:2].isalpha():
                    ugc_state = segment[0:2]
                    if state != ugc_state:
                        continue
                    if segment[3:6] is 'ALL' or segment[3:6] is '000':
                        return True
                    ugc_format = UGC.FORMATS[segment[2]]
                    if len(segment) is 6:
                        if ugc_format is UGC.FORMAT_FIPS:
                            if segment[3:6] == FIPS:
                                return True
                            else:
                                continue
                        elif ugc_format is UGC.FORMAT_ZONE:
                            if segment[3:6] == nws_zone:
                                return True
                            else:
                                continue
                        else:
                            Log.error('Error parsing UGC code {0} at segment {1}'.format(ugc, segment))
                    elif len(segment) is 10:                        
                        start, end = segment[3:10].split('>')
                        start = int(start)
                        end = int(end)
                        if ugc_format is UGC.FORMAT_FIPS:
                            target = int(FIPS)
                        elif ugc_format is UGC.FORMAT_ZONE:
                            target = int(nws_zone)
                        if target >= start and target <= end:
                            return True
                        else:
                            continue
                    else:
                        Log.error('Error parsing UGC code {0} at segment {1}'.format(ugc, segment))
                elif len(segment) is 3:
                    if state != ugc_state:
                        continue
                    if ugc_format is UGC.FORMAT_FIPS:
                        if segment == FIPS:
                            return True
                        else:
                            continue
                    elif ugc_format is UGC.FORMAT_ZONE:
                        if segment == nws_zone:
                            return True
                        else:
                            continue
                    else:
                        Log.error('Error parsing UGC code {0} at segment {1}'.format(ugc, segment))
                elif len(segment) is 7:
                    if state != ugc_state:
                        continue
                    start, end = segment.split('>')
                    start = int(start)
                    end = int(end)
                    if ugc_format is UGC.FORMAT_FIPS:
                        target = int(FIPS)
                    elif ugc_format is UGC.FORMAT_ZONE:
                        target = int(nws_zone)
                    if target >= start and target <= end:
                        return True
                    else:
                        continue
                elif len(segment) is 6:
                    #Log.debug('Found UGC datetime {0} in UGC {1}'.format(segment, ugc))
                    continue
                else:
                    if len(segment) > 0:
                        Log.error('Unexpected UGC segment {0} in {1}'.format(segment, ugc))
                    continue
        return False
                        
class WFO:
    WEBSITES = dict({
                     # Western Region
                     #   Arizona
                     'FGZ': 'http://www.wrh.noaa.gov/fgz/',
                     'PSR': 'http://www.wrh.noaa.gov/psr/',
                     'TWC': 'http://www.wrh.noaa.gov/twc/',
                     #   California
                     'EKA': 'http://www.wrh.noaa.gov/eka/',
                     'LOX': 'http://www.wrh.noaa.gov/lox/',
                     'STO': 'http://www.wrh.noaa.gov/sto/',
                     'SGX': 'http://www.wrh.noaa.gov/sgx/',
                     'MTR': 'http://www.wrh.noaa.gov/mtr/',
                     'HNX': 'http://www.wrh.noaa.gov/hnx/',
                     #   Idaho
                     'BOI': 'http://www.wrh.noaa.gov/boi/',
                     'PIH': 'http://www.wrh.noaa.gov//',
                     #   Montana
                     'BYZ': 'http://www.wrh.noaa.gov/byz/',
                     'GGW': 'http://www.wrh.noaa.gov/ggw/',
                     'TFX': 'http://www.wrh.noaa.gov/tfx/',
                     'MSO': 'http://www.wrh.noaa.gov/mso/',
                     #   Nevada
                     'LKN': 'http://www.wrh.noaa.gov/lkn/',
                     'VEF': 'http://www.wrh.noaa.gov/vef/',
                     'REV': 'http://www.wrh.noaa.gov/rev/',
                     #   Oregon
                     'MFR': 'http://www.wrh.noaa.gov/mfr/',
                     'PDT': 'http://www.wrh.noaa.gov/pdt/',
                     'PQR': 'http://www.wrh.noaa.gov/pqr/',
                     #   Utah
                     'SLC': 'http://www.wrh.noaa.gov/slc/',
                     #   Washington
                     'SEW': 'http://www.wrh.noaa.gov/sew/',
                     'OTX': 'http://www.wrh.noaa.gov/otx/',
                     # Southern Region
                     #==========================================================
                     # 'BMX'
                     # 'HUN'
                     # 'MOB'
                     # 'LZK'
                     # 'JAX'
                     # 'KEY'
                     # 'MLB'
                     # 'MFL'
                     # 'TLH'
                     # 'TBW'
                     # 'FFC'
                     # 'LCH'
                     # 'LIX'
                     # 'SHV'
                     # 'JAN'
                     # 'ABQ'
                     # 'OUN'
                     # 'TSA'
                     # 'SJU'
                     # 'MEG'
                     # 'MRX'
                     # 'BNA'
                     # 'AMA'
                     # 'EWX'
                     # 'BRO'
                     # 'CRP'
                     # 'FWD'
                     # 'ELP'
                     # 'HGX'
                     # 'LUB'
                     # 'MAF'
                     # 'SJT'
                     # # Pacific Region
                     # 'STU'
                     # 'GUM'
                     # 'HNL'
                     # # Eastern Region
                     # 'CAR'
                     # 'GYX'
                     # 'LWX'
                     # 'BOX'
                     # 'PHI'
                     # 'ALY'
                     # 'BGM'
                     # 'BUF'
                     # 'OKX'
                     # 'MHX'
                     # 'RAH'
                     # 'ILM'
                     # 'CLE'
                     # 'ILN'
                     # 'PIT'
                     # 'CTP'
                     # 'CHS'
                     # 'CAE'
                     # 'GSP'
                     # 'BVT'
                     # 'RNK'
                     # 'AKQ'
                     # 'RLX'
                     # # Alaskan Region
                     # 'AFC'
                     # 'AFG'
                     # 'AJK'
                     # # Central Region
                     # 'DEN'
                     # 'GJT'
                     # 'PUB'
                     # 'LOT'
                     # 'ILX'
                     # 'IND'
                     # 'IWX'
                     # 'DVN'
                     # 'DMX'
                     # 'DDC'
                     # 'GLD'
                     # 'TOP'
                     # 'ICT'
                     # 'JKL'
                     # 'LMK'
                     # 'PAH'
                     # 'DTX'
                     # 'APX'
                     # 'GRR'
                     # 'MQT'
                     # 'DLH'
                     # 'MPX'
                     # 'EAX'
                     # 'SGF'
                     # 'LSX'
                     # 'GID'
                     # 'LBF'
                     # 'OAX'
                     # 'BIS'
                     # 'FGF'
                     # 'ABR'
                     # 'UNR'
                     # 'FSD'
                     # 'GRB'
                     # 'ARX'
                     # 'MKX'
                     # 'CYS'
                     # 'RIW'
                     #==========================================================
                     })
