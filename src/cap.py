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
                if type in area.geoCodes:
                    if code in area.geoCodes[type]:
                        return True
        return False

    def checkCoords(self, coords):
        for info in self.infos:
            for area in info.areas:
                for circle in area.circles:
                    x, y, radius = circle
                    Log.debug("The distance is %s" % utils.distance((x,y), coords))
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
                    (sender,identifier,sent) = reference.split(references,',')
                    self.references.append(identifier)
                else:
                    if len(reference) > 0:
                        Log.warning("Failure to parse references. \"{0}\"".format(references))
                    
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
            self.language = language.strip()
        else:
            self.language = u'en-US'
            
    @staticmethod
    def aboutLanguage():
        return u'The code denoting the language of the info subelement of the alert message'

    def addCategory(self, category):
        if category is not None:
            category = category.strip()
            if category == u'Geo':
                self.categories.add(Info.CATEGORY_GEO)
            elif category == u'Met':
                self.categories.add(Info.CATEGORY_MET)
            elif category == u'Safety':
                self.categories.add(Info.CATEGORY_SAFETY)
            elif category == u'Security':
                self.categories.add(Info.CATEGORY_SECURITY)
            elif category == u'Rescue':
                self.categories.add(Info.CATEGORY_RESCUE)
            elif category == u'Fire':
                self.categories.add(Info.CATEGORY_FIRE)
            elif category == u'Health':
                self.categories.add(Info.CATEGORY_HEALTH)
            elif category == u'Env':
                self.categories.add(Info.CATEGORY_ENV)
            elif category == u'Transport':
                self.categories.add(Info.CATEGORY_TRANSPORT)
            elif category == u'Infra':
                self.categories.add(Info.CATEGORY_INFRA)
            elif category == u'CBRNE':
                self.categories.add(Info.CATEGORY_CBRNE)
            elif category == u'Other':
                self.categories.add(Info.CATEGORY_OTHER)
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
        if event is not None:
            self.event = event.strip()

    @staticmethod
    def aboutEvent():
        return u'The text denoting the type of the subject event of the alert message.'


    def addResponseType(self, responseType):
        if responseType is not None:
            responseType = responseType.strip()
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
    product_class = dict({'O': 'Operational Product',
                  'T': 'Test Product',
                  'E': 'Experimental Product',
                  'X': 'Experimental VTEC in an Operational Product'
        })
    significance = dict({'W': 'Warning',
                         'A': 'Watch',
                         'Y': 'Advisory',
                         'S': 'Statement',
                         'F': 'Forecast',
                         'O': 'Outlook',
                         'N': 'Synopsis',
                         })
    actions = dict({'NEW': 'New Event',
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
    phenomena = dict({
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
    
    flood_severity = dict({
                           'N': 'None',
                           '0': 'Areal Flood or Flash Flood Product',
                           '1': 'Minor',
                           '2': 'Moderate',
                           '3': 'Major',
                           'U': 'Unknown'
                           })
    
    immediate_cause = dict({
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
    
    flood_record_status = dict({
                                'NO': 'A record flood is not expected',
                                'NR': 'Near record or record flood expected',
                                'UU': 'Flood without a period of record to compare',
                                'OO': 'For areal flood warnings, areal flash flood products, and flood advisories (point and real)'
                                })
    @staticmethod
    def getProductClass(pc):
        if pc is not None:
            if pc.upper() in VTEC.product_class:
                return VTEC.product_class[pc.upper()]
            else:
                Log.warning('Unknown VTEC product class {0}'.format(pc))
        return 'Unknown Product Class'
    
    @staticmethod
    def getSignificance(sig):
        if sig is not None:
            if sig.upper() in VTEC.significance:
                return VTEC.significance[sig.upper()]
            else:
                Log.warning('Unknown VTEC significance {0}'.format(sig))
        return 'Unknown Significance'
    
    @staticmethod
    def getActions(act):
        if act is not None:
            if act.upper() in VTEC.actions:
                return VTEC.actions[act.upper()]
            else:
                Log.warning('Unknown VTEC action {0}'.format(act))
        return 'Unknown Actions'
    
    @staticmethod
    def getPhenomena(pp):
        if pp is not None:
            if pp.upper() in VTEC.phenomena:
                return VTEC.phenomena[pp.upper()]
            else:
                Log.warning('Unknown VTEC phenomena {0}'.format(pp))
        return 'Unknown Phenomena'
    
    @staticmethod
    def getFloodSeverity(sev):
        if sev is not None:
            if sev in VTEC.flood_severity:
                return VTEC.flood_severity[sev]
            else:
                Log.warning('Unknown VTEC Flood Severity {0}'.format(sev))
        return 'Unknown Severity'
    
    @staticmethod
    def getImmediateCause(ic):
        if ic is not None:
            if ic.upper() in VTEC.immediate_cause:
                return VTEC.immediate_cause[ic.upper()]
            else:
                Log.warning("Unknown VTEC Immediate Cause {0}".format(ic))
        return "Unknown Cause"
    
    @staticmethod
    def getFloodRecordStatus(frs):
        if frs is not None:
            if frs.upper() in VTEC.flood_record_status:
                return VTEC.flood_record_status[frs.upper()]
            else:
                Log.warning("Unknown Flood Record Status {0}".format(frs))
        return 'Unknown record status'
    
# TODO: UGC codes
# http://www.weather.gov/directives/sym/pd01017002curr.pdf