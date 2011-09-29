#include "cap.hxx"
#include "datetime.hxx"
#include "log.hpp"
#include "util.h"
#include <libintl.h>
#define _(String) gettext (String)

using CAPViewer::Log;

CAPViewer::CAP& CAPViewer::CAP::addCode(const Glib::ustring& in) {
  codes.push_back(in);
  return *this;
}

std::vector<Glib::ustring> CAPViewer::CAP::getCodes() const {
  return codes;
}

CAPViewer::CAP& CAPViewer::CAP::addReference(const Glib::ustring& in) {
  /* TODO: Parse reference string:
   *  The extended message identifier(s) (in the form sender,identifier,sent) 
   *  of an earlier CAP message or messages referenced by this one.
   *  If multiple messages are referenced, they SHALL be separated by whitespace.
   *
   *  In pre-IPAWS reality, this is often just identifier.
   */

  references.push_back(in);
  return *this;
}

std::vector<Glib::ustring> CAPViewer::CAP::getReferences() const {
  return references;
}

CAPViewer::CAP& CAPViewer::CAP::addInfo(const CAPViewer::Info& in) {
  infos.push_back(in);
  return *this;
}

std::vector<CAPViewer::Info> CAPViewer::CAP::getInfos() const {
  return infos;
}

Glib::ustring CAPViewer::CAP::getTitle() const {
  for (auto info : infos) {
    /*            if info.vtec is not None and info.vtec.hasPVTEC:
                return str.format("{0} {1}", info.vtec.phenomena, info.vtec.significance)
    */
     
    if ( info.getEvent().length() > 0 ) {
      return info.getEvent();
    } 

    if (info.getEventCodes().count("SAME") > 0) {
      auto iter = info.getEventCodes().find("SAME");
      if (iter->second.length() > 0)
	return iter->second; // TODO: expand out acronym
    }
  }

  if ( note.length() > 0 ) {
    return note;
  }
   
  return getId();

  /*
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
  */
		  
}

CAPViewer::CAP& CAPViewer::CAP::setId(const Glib::ustring& in) {
  id = in;
  return *this;
}

Glib::ustring CAPViewer::CAP::getId() const {
  return id;
}

CAPViewer::CAP& CAPViewer::CAP::setVersion(const Glib::ustring& in) {
  version = in;
  return *this;
}

Glib::ustring CAPViewer::CAP::getVersion() const {
  return version;
}

CAPViewer::CAP& CAPViewer::CAP::setSender(const Glib::ustring& in) {
  sender = in;
  return *this;
}

Glib::ustring CAPViewer::CAP::getSender() const {
  return sender;
}

CAPViewer::CAP& CAPViewer::CAP::setSent(const CAPViewer::DateTime& in) {
  sent = in;
  return *this;
}

CAPViewer::DateTime CAPViewer::CAP::getSent() const {
  return sent;
}

CAPViewer::CAP& CAPViewer::CAP::setStatus(const CAPViewer::eStatus& in) {
  status = in;
  return *this;
}

CAPViewer::CAP& CAPViewer::CAP::setStatus(const Glib::ustring& in) {
  auto iter = CAPViewer::stringStatusMap.find(CAPViewer::Util::squish(in));
  if ( iter != CAPViewer::stringStatusMap.end() ) {
    status = iter->second;
    return *this;
  } else {
    throw CAPViewer::EnumParseError("Invalid status: " + in);
  }
}

CAPViewer::eStatus CAPViewer::CAP::getStatus() const {
  return status;
}


CAPViewer::CAP& CAPViewer::CAP::setMsgType(const CAPViewer::eMsgType& in) {
  msgType = in;
  return *this;
}

CAPViewer::CAP& CAPViewer::CAP::setMsgType(const Glib::ustring& in) {
  auto iter = CAPViewer::stringMsgTypeMap.find(CAPViewer::Util::squish(in));
  if ( iter != CAPViewer::stringMsgTypeMap.end() ) {
    msgType = iter->second;
    return *this;
  } else {
    throw CAPViewer::EnumParseError("Invalid msgType: " + in);
  }
}

CAPViewer::eMsgType CAPViewer::CAP::getMsgType() const {
  return msgType;
}

CAPViewer::eUrgency CAPViewer::CAP::getUrgency() const {
  return infos.front().getUrgency();
}

CAPViewer::eSeverity CAPViewer::CAP::getSeverity() const {
  return infos.front().getSeverity();
}

CAPViewer::CAP& CAPViewer::CAP::setScope(const CAPViewer::eScope& in) {
  scope = in;
  return *this;
}

CAPViewer::CAP& CAPViewer::CAP::setScope(const Glib::ustring& in) {
  auto iter = CAPViewer::stringScopeMap.find(CAPViewer::Util::squish(in));
  if ( iter != CAPViewer::stringScopeMap.end() ) {
    scope = iter->second;
    return *this;
  } else {
    throw CAPViewer::EnumParseError("Invalid scope: " + in);
  }
}

CAPViewer::eScope CAPViewer::CAP::getScope() const {
  return scope;
}


CAPViewer::CAP& CAPViewer::CAP::setSource(const Glib::ustring& in) {
  source = in;
  return *this;
}

Glib::ustring CAPViewer::CAP::getSource() const {
  return source;
}

CAPViewer::CAP& CAPViewer::CAP::setRestriction(const Glib::ustring& in) {
  restriction = in;
  return *this;
}

Glib::ustring CAPViewer::CAP::getRestriction() const {
  return restriction;
}

CAPViewer::CAP& CAPViewer::CAP::setAddresses(const Glib::ustring& in) {
  addresses = in;
  return *this;
}

Glib::ustring CAPViewer::CAP::getAddresses() const {
  return addresses;
}

CAPViewer::CAP& CAPViewer::CAP::setNote(const Glib::ustring& in) {
  note = in;
  return *this;
}

Glib::ustring CAPViewer::CAP::getNote() const {
  return note;
}

CAPViewer::CAP& CAPViewer::CAP::setIncidents(const Glib::ustring& in) {
  incidents = in;
  return *this;
}

Glib::ustring CAPViewer::CAP::getIncidents() const {
  return incidents;
}

/* Info methods */

CAPViewer::Info& CAPViewer::Info::addCategory(const Glib::ustring& in) {
  auto iter = CAPViewer::stringCategoryMap.find(CAPViewer::Util::squish(in));
  if ( iter != CAPViewer::stringCategoryMap.end() ) {
    categories.push_back(iter->second);
    return *this;
  } else {
    throw CAPViewer::EnumParseError("Invalid category: " + in);
  }
}

CAPViewer::Info& CAPViewer::Info::addResponse(const Glib::ustring& in) {
  auto iter = CAPViewer::stringResponseMap.find(CAPViewer::Util::squish(in));
  if ( iter != CAPViewer::stringResponseMap.end() ) {
    responses.push_back(iter->second);
    return *this;
  } else {
    throw CAPViewer::EnumParseError("Invalid response: " + in);
  }
}

CAPViewer::Info& CAPViewer::Info::addEventCode(const Glib::ustring& key, const Glib::ustring& value) {
  const std::pair<Glib::ustring, Glib::ustring> kv = {key, value};
  eventCodes.insert(kv);
  return *this;
}

CAPViewer::Info& CAPViewer::Info::addParameter(const Glib::ustring& key, const Glib::ustring& value) {
  const std::pair<Glib::ustring, Glib::ustring> kv = {key, value};
  parameters.insert(kv);
  return *this;
}

CAPViewer::Info& CAPViewer::Info::setUrgency(const Glib::ustring& in) {
  auto iter = CAPViewer::stringUrgencyMap.find(CAPViewer::Util::squish(in));
  if ( iter != CAPViewer::stringUrgencyMap.end() ) {
    urgency = iter->second;
    return *this;
  } else {
    throw CAPViewer::EnumParseError("Invalid urgency: " + in);
  }
}

CAPViewer::Info& CAPViewer::Info::setSeverity(const Glib::ustring& in) {
  auto iter = CAPViewer::stringSeverityMap.find(CAPViewer::Util::squish(in));
  if ( iter != CAPViewer::stringSeverityMap.end() ) {
    severity = iter->second;
    return *this;
  } else {
    throw CAPViewer::EnumParseError("Invalid severity: " + in);
  }
}

CAPViewer::Info& CAPViewer::Info::setCertainty(const Glib::ustring& in) {
  auto iter = CAPViewer::stringCertaintyMap.find(CAPViewer::Util::squish(in));
  if ( iter != CAPViewer::stringCertaintyMap.end() ) {
    certainty = iter->second;
    return *this;
  } else {
    throw CAPViewer::EnumParseError("Invalid certainty: " + in);
  }
}

/* Resource methods */
CAPViewer::Resource::Resource() : size(0) {
}

CAPViewer::Resource& CAPViewer::Resource::setSize(const Glib::ustring& in) {
  std::stringstream s;
  s << in.raw();
  s >> std::ws;
  
  if (s.eof())
    throw SizeParseError("No size found in given string; all whitespace");

  s >> size >> std::ws;
  if (s.bad())
    throw std::ios_base::failure("'Bad' failure on stream parsing resource size");
  if (s.fail())
    throw SizeParseError("Error parsing resource size");

  if (!s.eof())
    Log::warn("Parsed resource size from string, but text remains in string. Original string: " + in);

  return *this;
}


/* Polygon Methods */
CAPViewer::Polygon::Polygon() {
  points.clear();
}

CAPViewer::Polygon::Polygon(const Glib::ustring& in) {
  points.clear();
  addPoints(in);
}

CAPViewer::Polygon& CAPViewer::Polygon::addPoints(const Glib::ustring& in) {
  std::stringstream s;
  s << in.raw();  
  
  while(!s.eof()) {
    CAPViewer::Coords c(s);
    points.push_back(c);
  }
  return *this;
}

/* Circle methods */
CAPViewer::Circle::Circle() : radius(0.0) {
}

CAPViewer::Circle::Circle(const Glib::ustring& in) : radius(0.0) {
  setCircle(in);
}

CAPViewer::Circle::Circle(std::stringstream& in) : radius(0.0) {
  setCircle(in);
}

CAPViewer::Circle& CAPViewer::Circle::setCircle(const Glib::ustring& in) {
  std::stringstream s;
  s << in.raw();

  return setCircle(s);
}

CAPViewer::Circle& CAPViewer::Circle::setCircle(std::stringstream& in) {
  coords.setLatLong(in);

  if (in.eof())
    throw CoordinateParseError("Got circle center coordinate, but no radius");

  in >> radius >> std::ws;
  if (in.bad())
    throw std::ios_base::failure("'Bad' failure on stream parsing circle radius");
  if (in.fail())
    throw CoordinateParseError("Failure parsing circle radius");

  if (!in.eof()) {
    Log::warn("Parsed a circle, but there is unexpected data left in the string");
  }
  return *this;
}

/* Coords methods */
CAPViewer::Coords::Coords() {
  latitude = 0.0;
  longitude = 0.0;
}

CAPViewer::Coords& CAPViewer::Coords::setLatLong(const Glib::ustring& in) {
  std::stringstream s;
  s << in.raw();

  return setLatLong(s);
}

CAPViewer::Coords& CAPViewer::Coords::setLatLong(std::stringstream& s) {
  std::ios::fmtflags flags = s.flags();
  s >> std::noskipws;

  s >> std::ws;
  if (s.eof())
    throw CoordinateParseError("No latitude or longitude in stream");
  
  s >> latitude;
  if (s.eof())
    throw CoordinateParseError("Got latitude but no longitude in stream");
  if (s.bad())
    throw std::ios_base::failure("'Bad' failure on stream parsing latitude");
  if (s.fail())
    throw CoordinateParseError("Failure on stream paring latitude. Probably no number at the beginning of the stream.");

  if ( s.get() != ',' ) {
    s.unget();
    throw CoordinateParseError("Invalid formatting, didn't find expected comma");
  }

  if (s.eof()) 
    throw CoordinateParseError("Got latitude but no longitude in stream");
  if (s.bad())
    throw std::ios_base::failure("'Bad' failure on stream parsing comma");
  if (s.fail())
    throw CoordinateParseError("Failure on stream parsing comma");

  s >> longitude >> std::ws;
  if (s.bad())
    throw std::ios_base::failure("'Bad' failure on stream parsing longitude");
  if (s.fail())
    throw CoordinateParseError("Failure on stream parsing longitude. Probably no number after the comma.");
  
  s.flags(flags); // reset stream to default
  return *this;
}

CAPViewer::Coords& CAPViewer::Coords::setLatitude(const Glib::ustring& in) {
  std::stringstream s;
  s << in.raw();

  s >> std::ws;
  if (s.eof())
    throw CoordinateParseError("No latitude in given string");

  s >> latitude >> std::ws;
  if (s.bad()) {
    throw std::ios_base::failure("'Bad' failure on stream parsing latitude");
  }
  if (s.fail()) {
    throw CoordinateParseError("Failure on stream parsing latitude. Input was " + in);
  }

  if (!s.eof()) {
    Log::warn("Parsed a latitude but there is still unparsed text. Input was " + in);
  }

  return *this;
}

CAPViewer::Coords& CAPViewer::Coords::setLongitude(const Glib::ustring& in) {
  std::stringstream s;
  s << in.raw();

  s >> std::ws;
  if (s.eof())
    throw CoordinateParseError("No longitude in given string");

  s >> latitude >> std::ws;
  if (s.bad()) {
    throw std::ios_base::failure("'Bad' failure on stream parsing longitude");
  }
  if (s.fail()) {
    throw CoordinateParseError("Failure on stream parsing longitude. Input was " + in);
  }

  if (!s.eof()) {
    Log::warn("Parsed a longitude but there is still unparsed text. Input was " + in);
  }

  return *this;
}

/* Area methods */
CAPViewer::Area::Area() : altitude(0), ceiling(0) {
}


CAPViewer::Area& CAPViewer::Area::addGeoCode(const Glib::ustring& key, const Glib::ustring& value) {
  const std::pair<Glib::ustring, Glib::ustring> kv = {key, value};
  geoCodes.insert(kv);
  return *this;
}

CAPViewer::Area& CAPViewer::Area::setAltitude(const Glib::ustring& in) {
  std::stringstream s;
  s << in.raw();
  
  s >> std::ws;
  if (s.eof())
    throw AltitudeParseError("No altitude in given string; all whitespace");

  s >> altitude >> std::ws;
  if (s.bad())
    throw std::ios_base::failure("'Bad' failure on stream parsing altitude");
  if (s.fail())
    throw AltitudeParseError("Error parsing altitude from given string");
  if (!s.eof())
    Log::warn("Parsed altitude from string, but text remains in string. Original string: " + in);

  return *this;
}

CAPViewer::Area& CAPViewer::Area::setCeiling(const Glib::ustring& in) {
  std::stringstream s;
  s << in.raw();
  
  s >> std::ws;
  if (s.eof())
    throw AltitudeParseError("No ceiling in given string; all whitespace");

  s >> ceiling >> std::ws;
  if (s.bad())
    throw std::ios_base::failure("'Bad' failure on stream parsing ceiling");
  if (s.fail())
    throw AltitudeParseError("Error parsing ceiling from given string");
  if (!s.eof())
    Log::warn("Parsed ceiling from string, but text remains in string. Original string: " + in);

  return *this;
}

/* Begin 'about' Strings */

const Glib::ustring CAPViewer::aboutScope(const CAPViewer::eScope& in) {
  auto it =  CAPViewer::aboutScopeMap.find(in);
  if (it == CAPViewer::aboutScopeMap.end()) {
    Log::error("Invalid scope passed to CAPViewer::aboutScope(eScope)");
    return CAPViewer::aboutErrorText;
  }
  else
    return it->second;
}

const Glib::ustring CAPViewer::aboutMsgType(const CAPViewer::eMsgType& in) {
  auto it =  CAPViewer::aboutMsgTypeMap.find(in);
  if (it == CAPViewer::aboutMsgTypeMap.end()) {
    Log::error("Invalid msgType passed to CAPViewer::aboutMsgType(eMsgType)");
    return CAPViewer::aboutErrorText;
  }
  else
    return it->second;
}

const Glib::ustring CAPViewer::aboutStatus(const CAPViewer::eStatus& in) {
  auto it =  CAPViewer::aboutStatusMap.find(in);
  if (it == CAPViewer::aboutStatusMap.end()) {
    Log::error("Invalid status passed to CAPViewer::aboutStatus(eStatus)");
    return CAPViewer::aboutErrorText;
  }
  else
    return it->second;
}

const Glib::ustring CAPViewer::aboutCategory(const CAPViewer::eCategory& in) {
  auto it =  CAPViewer::aboutCategoryMap.find(in);
  if (it == CAPViewer::aboutCategoryMap.end()) {
    Log::error("Invalid eCategory passed to aboutCategory.");
    return CAPViewer::aboutErrorText;
  }
  else
    return it->second;
}

const Glib::ustring CAPViewer::aboutResponse(const CAPViewer::eResponse& in) {
  auto it =  CAPViewer::aboutResponseMap.find(in);
  if (it == CAPViewer::aboutResponseMap.end()) {
    Log::error("Invalid eResponse passed to aboutReponse.");
    return CAPViewer::aboutErrorText;
  }
  else
    return it->second;
}

const Glib::ustring CAPViewer::aboutUrgency(const CAPViewer::eUrgency& in) {
  auto it =  CAPViewer::aboutUrgencyMap.find(in);
  if (it == CAPViewer::aboutUrgencyMap.end()) {
    Log::error("Invalid eUrgency passed to aboutUrgency.");
    return CAPViewer::aboutErrorText;
  }
  else
    return it->second;
}

const Glib::ustring CAPViewer::aboutSeverity(const CAPViewer::eSeverity& in) {
  auto it =  CAPViewer::aboutSeverityMap.find(in);
  if (it == CAPViewer::aboutSeverityMap.end()) {
    Log::error("Invalid eSeverity passed to aboutSeverity.");
    return CAPViewer::aboutErrorText;
  }
  else
    return it->second;
}

const Glib::ustring CAPViewer::aboutCertainty(const CAPViewer::eCertainty& in) {
  auto it =  CAPViewer::aboutCertaintyMap.find(in);
  if (it == CAPViewer::aboutCertaintyMap.end()) {
    Log::error("Invalid eCertainty passed to aboutCertainty.");
    return CAPViewer::aboutErrorText;
  }
  else
    return it->second;
}

const Glib::ustring CAPViewer::Info::aboutAudience() {
  return _("The text describing the intended audience of the alert message");
}

const Glib::ustring CAPViewer::Info::aboutEffective() {
  return _("The effective time of the information of the alert message");
}

const Glib::ustring CAPViewer::Info::aboutOnset() {
  return _("The expected time of the beginning of the subject event of the alert message");
}

const Glib::ustring CAPViewer::Info::aboutExpires() {
  return _("The expiry time of the information of the alert message");
}

const Glib::ustring CAPViewer::Info::aboutSenderName() {
  return _("The human-readable name of the agency or authority issuing this alert");
}

const Glib::ustring CAPViewer::Info::aboutHeadline() {
  return _("A brief human-readable headline");
}

const Glib::ustring CAPViewer::Info::aboutDescription() {
  return _("An extended human readable description of the hazard or event that occasioned this message");
}

const Glib::ustring CAPViewer::Info::aboutInstruction() {
  return _("An extended human readable instruction to targeted recipients");
}

const Glib::ustring CAPViewer::Info::aboutWeb() {
  return _("A full, absolute URI for an HTML page or other text resource with additional or reference information regarding this alert");
}

const Glib::ustring CAPViewer::Info::aboutContact() {
  return _("The text describing the contact for follow-up and confirmation of the alert message");
}

const Glib::ustring CAPViewer::CAP::aboutCodes() {
  return _("The code denoting the special handling of the alert message.");
}

const Glib::ustring CAPViewer::CAP::aboutReferences() {
  return _("The group listing identifying earlier message(s) referenced by the alert message.");
}

const Glib::ustring CAPViewer::CAP::aboutId() {
  return _("A number or string uniquely identifying this message, assigned by the sender.");
}

const Glib::ustring CAPViewer::CAP::aboutVersion() {
  return _("The version of the CAP standard this message was sent in"); /* FIXME */
}

const Glib::ustring CAPViewer::CAP::aboutSender() {
  return _("Identifies the originator of this alert. Guaranteed by assigner to be unique globally; e.g., may be based on an Internet domain name.");
}

const Glib::ustring aboutSent() {
  return _("The time and date of the origination of the alert message");
}

const Glib::ustring CAPViewer::aboutStatus() {
  return _("The code denoting the appropriate handling of the alert message");
}

const Glib::ustring CAPViewer::aboutMsgType() {
  return _("The code denoting the nature of the alert message");
}

const Glib::ustring CAPViewer::aboutScope() {
  return _("The code denoting the intended distribution of the alert message");
}

const Glib::ustring CAPViewer::CAP::aboutSource() {
  return _("The particular source of this alert; e.g., an operator or a specific device");
}

const Glib::ustring CAPViewer::CAP::aboutRestriction() {
  return _("The text describing the rule for limiting distribution of the restricted alert message");
}

const Glib::ustring CAPViewer::CAP::aboutAddresses() {
  return _("The group listing of intended recipients of the private alert message");
}

const Glib::ustring CAPViewer::CAP::aboutNote() {
  return _("The text describing the purpose or significance of the alert message");
}

const Glib::ustring CAPViewer::CAP::aboutIncidents() {
  return _("The group listing identifying earlier message(s) referenced by the alert message");
}

const Glib::ustring CAPViewer::Info::aboutLanguage() {
  return _("The code denoting the language of the info subelement of the alert message");
}

const Glib::ustring CAPViewer::Info::aboutEvent() {
  return _("The text denoting the type of the subject event of the alert message.");
}

const Glib::ustring CAPViewer::aboutCategory() {
  return _("The code denoting the category of the subject event of the alert message");
}

const Glib::ustring CAPViewer::aboutSeverity() {
  return _("The code denoting the severity of the subject event of the alert message");
}

const Glib::ustring CAPViewer::aboutResponse() {
  return _("The code denoting the type of action recommended for the target audience");
}

const Glib::ustring CAPViewer::aboutUrgency() {
  return _("The code denoting the urgency of the subject event of the alert message");
}

const Glib::ustring CAPViewer::aboutCertainty() {
  return _("The code denoting the certainty of the subject event of the alert message");
}

const Glib::ustring CAPViewer::Info::aboutEventCodes() {
  return _("A system specific code identifying the event type of the alert message");
}

const Glib::ustring CAPViewer::Info::aboutParameters() {
  return _("A system specific additional parameter associated with the alert message");
}

const Glib::ustring CAPViewer::Resource::aboutResourceDesc() {
  return _("The human-readable text describing the type and content, such as “map” or “photo”, of the resource file");
}

const Glib::ustring CAPViewer::Resource::aboutMimeType() {
  return _("The identifier of the MIME content type and sub-type describing the resource file");
}

const Glib::ustring CAPViewer::Resource::aboutSize() {
  return _("Approximate size of the resource file in bytes");
}

const Glib::ustring CAPViewer::Resource::aboutUri() {
  return _("A full absolute URI, typically a Uniform Resource Locator that can be used to retrieve the resource over the Internet OR a relative URI to name the content of a <derefUri> element if one is present in this resource block");
}

const Glib::ustring CAPViewer::Resource::aboutDerefUri() {
  return _("The data content of the resource file");
}

const Glib::ustring CAPViewer::Resource::aboutDigest() {
  return _("The code representing the digital digest (“hash”) computed from the resource file. Computed using SHA-1");
}

const Glib::ustring CAPViewer::Area::aboutPolygons() {
  return _("The geographic polygon is represented by a whitespace-delimited list of [WGS 84] coordinate pairs");
}

const Glib::ustring CAPViewer::Area::aboutCircles() {
  return _("The circular area is represented by a central point given as a [WGS 84] coordinate pair followed by a space character and a radius value in kilometers");
}

const Glib::ustring CAPViewer::Area::aboutGeoCodes() {
  return _("Any geographically-based code to describe a message target area");
}

const Glib::ustring CAPViewer::Area::aboutAreaDesc() {
  return _("A text description of the affected area");
}

const Glib::ustring CAPViewer::Area::aboutAltitude() {
  return _("If used with the <ceiling> element this value is the lower limit of a range. Otherwise, this value specifies a specific altitude. The altitude measure is in feet above mean sea level per the [WGS 84] datum");
}

const Glib::ustring CAPViewer::Area::aboutCeiling() {
  return _("The maximum altitude of the affected area of the alert message");
}

const Glib::ustring CAPViewer::CAP::getPrintString() const {
  Glib::ustring out;

  out += "Id: " + id + "\n";
  out += "Version: " + version + "\n";
  out += "Sender: " + sender + "\n";
  out += "Sent: " + sent.toString() + "\n";
  out += "Status: " + statusStringMap.find(status)->second + "\n";
  out += "MsgType: " + msgTypeStringMap.find(msgType)->second + "\n";
  out += "Scope: " + scopeStringMap.find(scope)->second + "\n";
  out += "Source: " + source + "\n";
  out += "Restriction: " + restriction + "\n";
  out += "Addresses: " + addresses + "\n";
  out += "Note: " + note + "\n";
  out += "Incidents: " + incidents + "\n";
  out += "Codes:\n";
  for (const Glib::ustring& i : codes) { 
    out += "\t" + i + "\n";
  }
  out += "References:\n";
  for (const Glib::ustring& i : references) { 
    out += "\t" + i + "\n";
  }
  long i = 1;
  for (const CAPViewer::Info& info : infos) { 
    out += "Info ";
    std::stringstream st;
    st << i;
    out += st.str();
    out += ":\n";
    out += info.getPrintString();
    i++;
  }

  return out;
}

const Glib::ustring CAPViewer::Info::getPrintString() const {
  Glib::ustring out;
  
  out += "Language: " + language + "\n";
  for (eCategory category : categories) {
    out += "Category: " + categoryStringMap.find(category)->second + "\n";
  }
  for (eResponse response : responses) {
    out += "Response: " + responseStringMap.find(response)->second + "\n";
  }
  for (auto pair : eventCodes) {
    out += "EventCode: " + pair.first + "=" + pair.second + "\n";
  }
  for (auto pair : parameters) {
    out += "Parameter: " + pair.first + "=" + pair.second + "\n";
  }
  out += "Event: " + event + "\n";
  out += "Urgency: " + urgencyStringMap.find(urgency)->second + "\n";
  out += "Severity: " + severityStringMap.find(severity)->second + "\n";
  out += "Certainty: " + certaintyStringMap.find(certainty)->second + "\n";
  out += "Audience: " + audience + "\n";
  out += "Effective: " + effective.toString() + "\n";
  out += "Onset: " + onset.toString() + "\n";
  out += "Expires: " + expires.toString() + "\n";
  out += "SenderName: " + senderName + "\n";
  out += "Headline: " + headline + "\n";
  out += "Description: \n" + description + "\n";
  out += "Instruction: \n" + instruction + "\n";
  out += "Web: " + web + "\n";
  out += "Contact: " + contact + "\n";

  int i = 1;
  for (auto area : areas) {
    out += "Area ";
    std::stringstream st;
    st << i;
    out += st.str() + ":\n";
    out += area.getPrintString();
    i++;
  }

  i = 1;
  for (auto resource : resources) {
    out += "Resource ";
    std::stringstream st;
    st << i;
    out += st.str() + ":\n";
    out += resource.getPrintString();
    i++;
  }
   
  
  return out;
}

const Glib::ustring CAPViewer::Area::getPrintString() const {
  Glib::ustring out;

  for (auto pair : geoCodes) {
    out += "geoCode: " + pair.first + "=" + pair.second + "\n";
  }
  out += "areaDesc: " + areaDesc + "\n";
  std::stringstream st;
  st << altitude;
  out += "Altitude: " + st.str() + "\n";
  std::stringstream st2;
  st2 << ceiling;
  out += "Ceiling: " + st2.str() + "\n";

  // TODO: print out circles, polygons
  return out;
}

const Glib::ustring CAPViewer::Resource::getPrintString() const {
  Glib::ustring out;
  std::stringstream st;

  st << "ResourceDesc: " << resourceDesc << std::endl;
  st << "MIMEType: " << mimeType << std::endl;
  st << "Size: " << size << std::endl;
  st << "URI: " << uri << std::endl;
  st << "deref_uri: " << deref_uri << std::endl;
  st << "Digest: " << digest << std::endl;

  out += st.str();

  return out;
}

const Glib::ustring CAPViewer::Circle::getPrintString() const {
  return "Unimplemented"; // TODO
}

const Glib::ustring CAPViewer::Polygon::getPrintString() const {
  return "Unimplemented"; // TODO
}
