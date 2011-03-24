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
import logging 
import base64
import glineenc as polylines
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
        
    def checkArea(self, type, code):
        for info in self.infos:
            for area in info.areas:
                if code in area.geoCodes[type]:
                    return True
        return False
    
    def setId(self, id):
        self.id = id
    
    @staticmethod
    def aboutId():
        return u'A number or string uniquely identifying this message, assigned by the sender.'
    
    def setVersion(self, namespace):
        elems = namespace.split(':')
        self.version = elems[len(elems)-1]
        if elems[0] != 'urn' or elems[1] != 'oasis' or elems[2] != 'names' or elems[3] != 'tc' or elems[4] != 'emergency' or elems[5] != 'cap':
            Log.warn("Unexpected namespace %s" % namespace)

    def setSender(self, sender):
        self.sender = sender
        
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
            return u'- Technical testing only, all recipients disregard'
        elif type is Alert.STATUS_DRAFT:
            return u'A preliminary template or draft, not actionable in its current form.'
        else:
            return u'Invalid type'
        
    def setMsgType(self, msgType):
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
        self.source = source
        
    @staticmethod
    def aboutSource():
        return u'The particular source of this alert; e.g., an operator or a specific device.'
    
    def setScope(self, scope):
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
        self.restriction = restriction
    
    @staticmethod
    def aboutRestriction():
        return u'The text describing the rule for limiting distribution of the restricted alert message.'
        
    def setAddresses(self, addresses):
        # Multiple space-delimited addresses MAY be included.  Addresses including whitespace MUST be enclosed in double-quotes.
        if unicode.count(addresses, u'"') > 0:
            Log.warning("CAP contains addresses with quotes. Parsing is unimplemented.")
        else:
            self.addresses = addresses.split(' ');
        self.addresses = addresses
        
    @staticmethod
    def aboutAddresses():
        return u'The group listing of intended recipients of the private alert message.'
        
    def addCode(self, code):
        #  Multiple instances MAY occur within a single <info> block
        self.codes.append(code)
        
    @staticmethod
    def aboutCode():
        return u'The code denoting the special handling of the alert message.'
        
    def setNote(self, note):
        # The message note is primarily intended for use with  <status> “Exercise” and <msgType> “Error
        self.note = note
        
    @staticmethod
    def aboutNote():
        return u'The text describing the purpose or significance of the alert message.'
        
    def setReferences(self, references):
        #  The extended message identifier(s) (in the form sender,identifier,sent) of an earlier CAP message or messages referenced by this one.
        # If multiple messages are referenced, they SHALL be separated by whitespace.
        if references is None:
            return
        else:
            for reference in references.split(' '):
                if reference.count(',') is 2:
                    (sender,identifier,sent) = reference.split(references,',')
                    self.references.append(identifier)
                else:
                    if len(reference) > 0:
                        Log.error("Failure to parse references. \"%s\"" % references)
                    
    @staticmethod
    def aboutReferences():
        return u'The group listing identifying earlier message(s) referenced by the alert message.'
        
    def setIncidents(self, incidents):
        # Used to collate multiple messages referring to different aspects of the same incident
        #  If multiple incident identifiers are referenced, they SHALL be separated by whitespace.  Incident names including whitespace SHALL be surrounded by double-quote
        self.incidents = incidents
        
    @staticmethod 
    def aboutIncidents():
        return u'The group listing naming the referent incident(s) of the alert message.'
        
    def addInfo(self, info):
        self.infos.append(info)
        
            
class Info:
    # In addition to the specified subelements, MAY contain one or more <resource> blocks and/or one or more <area> blocks
    CATEGORY_GEO = u'Geo'
    CATEGORY_MET = u'Met'
    CATEGORY_SAFETY = u'Safety'
    CATEGORY_SECURITY = u'Security'
    CATEGORY_RESCUE = u'Rescue'
    CATEGORY_FIRE = u'Fire'
    CATEGORY_HEALTH = u'Health'
    CATEGORY_ENV = u'Env'
    CATEGORY_TRANSPORT = u'Transport'
    CATEGORY_INFRA = u'Infra'
    CATEGORY_CBRNE = u'CBRNE'
    CATEGORY_OTHER = u'Other'

    RESPONSE_SHELTER = u'Shelter'
    RESPONSE_EVACUATE = u'Evacuate'
    RESPONSE_PREPARE = u'Prepare'
    RESPONSE_EXECUTE = u'Execute'
    RESPONSE_MONITOR = u'Monitor'
    RESPONSE_ASSESS = u'Assess'
    RESPONSE_NONE = u'None'
    RESPONSE_ALLCLEAR = u'All Clear'
    
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
    def setLanguage(self, language):
        if len(language) > 0:
            self.language = language
        else:
            self.language = u'en-US'
            
    @staticmethod
    def aboutLanguage():
        return u'The code denoting the language of the info subelement of the alert message'

    def addCategory(self, category):
        if category == u'Geo':
            self.categories.add(Info.CATEGORY_GEO)
        elif category == u'Met':
            self.categories.add(Info.CATEGORY_MET)
        elif category == u'Safety':
            self.category.add(Info.CATEGORY_SAFETY)
        elif category == u'Security':
            self.category.add(Info.CATEGORY_SECURITY)
        elif category == u'Rescue':
            self.category.add(Info.CATEGORY_RESCUE)
        elif category == u'Fire':
            self.category.add(Info.CATEGORY_FIRE)
        elif category == u'Health':
            self.category.add(Info.CATEGORY_HEALTH)
        elif category == u'Env':
            self.category.add(Info.CATEGORY_ENV)
        elif category == u'Transport':
            self.category.add(Info.CATEGORY_TRANSPORT)
        elif category == u'Infra':
            self.category.add(Info.CATEGORY_INFRA)
        elif category == u'CBRNE':
            self.category.add(Info.CATEGORY_CBRNE)
        elif category == u'Other':
            self.category.add(Info.CATEGORY_OTHER)
        else:
            Log.error("Unknown category \"%s\"" % category)

    @staticmethod
    def aboutCategory(category=None):
        if category is None:
            return u'The code denoting the category of the subject event of the alert message.'
        elif category is Info.CATEGORY_CBRNE:
            return u'Chemical, Biological, Radiological, Nuclear or High-Yield Explosive threat or attack.'
        elif category is Info.CATEGORY_ENV:
            return u'Pollution and other environmental.'
        elif category is Info.CATEGORY_FIRE:
            return u'Fire suppression and rescue.'
        elif category is Info.CATEGORY_GEO:
            return u'Geophysical (inc. landslide).'
        elif category is Info.CATEGORY_HEALTH:
            return u'Medical and public health.'
        elif category is Info.CATEGORY_INFRA:
            return u'Utility, telecommunication, other non-transport infrastructure.'
        elif category is Info.CATEGORY_MET:
            return u'Meteorological (inc. flood).'
        elif category is Info.CATEGORY_OTHER:
            return u'Other events.'
        elif category is Info.CATEGORY_RESCUE:
            return u'Rescue and recovery.'
        elif category is Info.CATEGORY_SAFETY:
            return u'General emergency and public safety.'
        elif category is Info.CATEGORY_SECURITY:
            return u'Law enforcement, military, homeland and local/private security.'
        elif category is Info.CATEGORY_TRANSPORT:
            return u'Public and private transportation.'
        else:
            return u'Invalid category \"%s\"'% category

    def setEvent(self, event):
        self.event = event
        
    @staticmethod
    def aboutEvent():
        return u'The text denoting the type of the subject event of the alert message.'


    def addResponseType(self, responseType):
        if responseType == u'Shelter':
            self.responseTypes.add(Info.RESPONSE_SHELTER)
        elif responseType == u'Evacuate':
            self.responseTypes.add(Info.RESPONSE_EVACUATE)
        elif responseType == u'Prepare':
            self.responseTypes.add(Info.RESPONSE_PREPARE)
        elif responseType == u'Execute':
            self.responseTypes.add(Info.RESPONSE_EXECUTE)
        elif responseType == u'Monitor':
            self.responseTypes.add(Info.RESPONSE_MONITOR)
        elif responseType == u'Assess':
            self.responseTypes.add(Info.RESPONSE_ASSESS)
        elif responseType == u'None':
            self.responseTypes.add(Info.RESPONSE_NONE)
        elif responseType == u'AlLClear':
            self.responseTypes.add(Info.RESPONSE_ALLCLEAR)
        else:
            Log.error("Invalid reponseType \"%s\"" % responseType)
    
    @staticmethod
    def aboutResponseType(responseType=None):
        if responseType is None:
            return u'The code denoting the type of action recommended for the target audience.'
        elif responseType is Info.RESPONSE_SHELTER:
            return u'Take shelter in place or per <instruction>.'
        elif responseType is Info.RESPONSE_EVACUATE:
            return u'Relocate as instructed in the <instruction>.'
        elif responseType is Info.RESPONSE_PREPARE:
            return u'Make preparations per the <instruction>.'
        elif responseType is Info.RESPONSE_EXECUTE:
            return u'Execute a pre-planned activity identified in <instruction>.'
        elif responseType is Info.RESPONSE_MONITOR:
            return u'Attend to information sources as described in <instruction>.'
        elif responseType is Info.RESPONSE_ASSESS:
            return u'Evaluate the information in this message.'
        elif responseType is Info.RESPONSE_NONE:
            return u'No action recommended.'
        elif responseType is Info.RESPONSE_ALLCLEAR:
            return u'The subject event no longer poses a threat or concern and any follow on action is described in <instruction>'
        else:
            return u"Invalid responseType %s" % responseType
        
    def setUrgency(self, urgency):
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
        self.audience = audience
        
    @staticmethod
    def aboutAudience():
        return u'The text describing the intended audience of the alert message.'

    def addEventCode(self, key, value):
        self.eventCodes[key] = value

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
        
    @staticmethod
    def aboutExpires():
        return u'The expiry time of the information of the alert message.'

    def setDefaultExpires(self):
        self.expires = self.effective + DEFAULT_EXPIRES

    def setSenderName(self, senderName):
        self.senderName = senderName
        
    @staticmethod
    def aboutSenderName():
        return u'The human-readable name of the agency or authority issuing this alert.'

    def setHeadline(self, headline):
        self.headline = headline
        
    @staticmethod
    def aboutHeadline():
        return u'A brief human-readable headline.'

    def setDescription(self, description):
        self.description = description
#        for x in desciption.splitlines():
#            self.description = self.description + x

    @staticmethod
    def aboutDescription():
        return u'An extended human readable description of the hazard or event that occasioned this message.'
    
    def setInstruction(self, instruction):
        self.instruction = instruction
        
    @staticmethod
    def aboutInstruction():
        return u'An extended human readable instruction to targeted recipients.'
    
    def setWeb(self, web):
        self.web = web
        
    @staticmethod
    def aboutWeb():
        return u'A full, absolute URI for an HTML page or other text resource with additional or reference information regarding this alert.'
    
    def setContact(self, contact):
        self.contact = contact
    
    @staticmethod
    def aboutContact():
        return u'The text describing the contact for follow-up and confirmation of the alert message'
    
    def addParameter(self, key, value):
        self.parameters[key] = value

    @staticmethod
    def aboutParameter():
        return u'A system specific additional parameter associated with the alert message'

    def addResource(self, resource):
        self.resources.append(resource)
        
    def addArea(self, area):
        self.areas.append(area)
        
class Resource:
    def setResourceDesc(self, resourceDesc):
        self.resourceDesc = resourceDesc
        
    @staticmethod
    def aboutResourceDesc():
        return u'The human-readable text describing the type and content, such as “map” or “photo”, of the resource file.'
    
    def setMimeType(self, mimeType):
        self.mimeType = mimeType
        
    @staticmethod
    def aboutMimeType():
        return u'The identifier of the MIME content type and sub-type describing the resource file'
    
    def setSize(self, size):
        self.size = long(size)
    
    @staticmethod
    def aboutSize():
        return u'Approximate size of the resource file in bytes.'
    
    def setUri(self, uri):
        self.uri = uri
        
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
        
    def setAreaDesc(self, areaDesc):
        self.areaDesc = areaDesc
        
    @staticmethod
    def aboutAreaDesc():
        return u'A text description of the affected area.'
    
    def addPolygon(self, polygon):
        if polygon is not None:
            p = list()
            for x in polygon.split(' '):
                (lat,long) = x.split(',')
                p.append((float(lat),float(long)))
            self.polygons.append(p)
             
    @staticmethod
    def aboutPolygon():
        return u'The geographic polygon is represented by a whitespace-delimited list of [WGS 84] coordinate pairs.'    
    
    def addCircle(self, circle):
        if circle is not None:
            (coords,radius) = circle.split(' ')
            (lat,long) = coords.split(',')
            self.circles.append((float(lat),float(long), float(radius)))

    @staticmethod
    def aboutCircle():
        return u'The circular area is represented by a central point given as a [WGS 84] coordinate pair followed by a space character and a radius value in kilometers.'
        
    def addGeoCode(self, key, value):
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
    
    
    
    
    