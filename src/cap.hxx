#ifndef CAP_HXX
#define CAP_HXX
#include <vector>
#include <unordered_map>
#include <map>
#include <string>
#include <glibmm/ustring.h>
#include <libintl.h>
#include "datetime.hxx"
#include "vtec.hxx"

#define _(String) gettext (String)

namespace CAPViewer {

  enum eStatus { Actual, Exercise, System, Test, Draft};
  enum eMsgType { Alert, Update, Cancel, Ack, Error};
  enum eScope { Public, Restricted, Private };
  enum eCategory { Geo, Met, Safety, Security, Rescue, Fire, Health, Env, Transport, Infra, Cbrne, Other };
  enum eResponse { Shelter, Evacuate, Prepare, Execute, Avoid, Monitor, Assess, AllClear, None };
  enum eUrgency { uImmediate, uExpected, uFuture, uPast, uUnknown };
  enum eSeverity { sExtreme, sSevere, sModerate, sMinor, sUnknown };
  enum eCertainty { cObserved, cLikely, cPossible, cUnlikely, cUnknown };

  const Glib::ustring aboutStatus(const eStatus&);
  const Glib::ustring aboutStatus();
  const Glib::ustring aboutMsgType(const eMsgType&);
  const Glib::ustring aboutMsgType();
  const Glib::ustring aboutScope(const eScope&);
  const Glib::ustring aboutScope();
  const Glib::ustring aboutCategory(const eCategory&);
  const Glib::ustring aboutCategory();
  const Glib::ustring aboutResponse(const eResponse&);
  const Glib::ustring aboutResponse();
  const Glib::ustring aboutUrgency(const eUrgency&);
  const Glib::ustring aboutUrgency();
  const Glib::ustring aboutSeverity(const eSeverity&);
  const Glib::ustring aboutSeverity();
  const Glib::ustring aboutCertainty(const eCertainty&);
  const Glib::ustring aboutCertainty();

  class Coords {
  public:
    Coords();

    Coords(const Glib::ustring& in) { setLatLong(in); };
    explicit Coords(std::stringstream& in) { setLatLong(in); };
    Coords& setLatitude(const Glib::ustring&);
    Coords& setLongitude(const Glib::ustring&);
    Coords& setLatLong(const Glib::ustring&);
    Coords& setLatLong(std::stringstream&);
    gdouble getLatitude() const { return latitude; };
    gdouble getLongitude() const { return longitude; };

  private:
    gdouble latitude;
    gdouble longitude;
  };

  class Polygon {
  public:
    Polygon();
    Polygon(const Glib::ustring&);
    std::vector<Coords> getPoints() const { return points; };
    Polygon& addPoints(const Glib::ustring&);

    const Glib::ustring getPrintString() const;

  private:
    std::vector<Coords> points;
  };

  class Circle {
  public:
    Circle();
    explicit Circle(std::stringstream&);
    Circle(const Glib::ustring&);

    Circle& setCircle(const Glib::ustring&);
    Coords getCoords() const { return coords; };
    gdouble getRadius() const { return radius; };

    const Glib::ustring getPrintString() const;

  private:
    Circle& setCircle(std::stringstream&);
    Coords coords;
    gdouble radius;
  };
  
  class Area {
  public:
    Area();

    Area& addPolygon(const Polygon& in) { polygons.push_back(in); return *this; };
    std::vector<Polygon> getPolygons() const {return polygons;};
    static const Glib::ustring aboutPolygons();

    Area& addCircle(const Circle& in) { circles.push_back(in); return *this;};
    std::vector<Circle> getCircles() const {return circles;};
    static const Glib::ustring aboutCircles();

    Area& addGeoCode(const Glib::ustring&, const Glib::ustring&);
    std::multimap<Glib::ustring, Glib::ustring> getGeoCodes() const { return geoCodes;};
    static const Glib::ustring aboutGeoCodes();

    Area& setAreaDesc(const Glib::ustring& in) { areaDesc = in; return *this; };
    Glib::ustring getAreaDesc() const { return areaDesc; };
    static const Glib::ustring aboutAreaDesc();

    Area& setAltitude(const gint64& in) { altitude = in; return *this; };
    Area& setAltitude(const Glib::ustring&);
    gint64 getAltitude() const {return altitude;};
    static const Glib::ustring aboutAltitude();

    Area& setCeiling(const gint64& in) { ceiling = in; return *this; };
    Area& setCeiling(const Glib::ustring&);
    gint64 getCeiling() const {return ceiling;};
    static const Glib::ustring aboutCeiling();

    const Glib::ustring getPrintString() const;

  private:
    std::vector<Polygon> polygons;
    std::vector<Circle> circles;
    std::multimap<Glib::ustring, Glib::ustring> geoCodes;
    Glib::ustring areaDesc;
    gint64 altitude;
    gint64 ceiling;
  };

  class Resource {
  public:
    Resource();

    Resource& setResourceDesc(const Glib::ustring& in) {resourceDesc = in; return *this;};
    Glib::ustring getResourceDesc() const { return resourceDesc; };
    static const Glib::ustring aboutResourceDesc();

    Resource& setMimeType(const Glib::ustring& in) { mimeType = in; return *this;};
    Glib::ustring getMimeType() const { return mimeType; };
    static const Glib::ustring aboutMimeType();
    
    Resource& setSize(const guint64& in) { size = in; return *this; };
    Resource& setSize(const Glib::ustring&);
    guint64 getSize() const { return size; };
    static const Glib::ustring aboutSize();

    Resource& setUri(const Glib::ustring& in) { uri = in; return *this; };
    Glib::ustring getUri() const { return uri; };
    static const Glib::ustring aboutUri();

    Resource& setDerefUri(const Glib::ustring& in) {deref_uri = in; return *this;};
    Glib::ustring getDerefUri() const { return deref_uri; };
    static const Glib::ustring aboutDerefUri();

    Resource& setDigest(const Glib::ustring& in) { digest = in; return *this; };
    Glib::ustring getDigest() const { return digest; };
    static const Glib::ustring aboutDigest();
    
    const Glib::ustring getPrintString() const;

  private:
    Glib::ustring resourceDesc;
    Glib::ustring mimeType;
    guint64 size;
    Glib::ustring uri;
    Glib::ustring deref_uri;
    Glib::ustring digest;

  };

  class Info {
  public:
    Info& setLanguage(const Glib::ustring& in) { language = in; return *this; };
    Glib::ustring getLanguage() const { return language; };
    static const Glib::ustring aboutLanguage();

    Info& addCategory(const eCategory& in) { categories.push_back(in); return *this; };
    Info& addCategory(const Glib::ustring& in);
    std::vector<eCategory> getCategories() const { return categories; };

    Info& addResponse(const eResponse& in) { responses.push_back(in); return *this; };
    Info& addResponse(const Glib::ustring& in);
    std::vector<eResponse> getResponses() { return responses; };

    Info& addEventCode(const Glib::ustring&, const Glib::ustring&);
    std::multimap<Glib::ustring, Glib::ustring> getEventCodes() const { return eventCodes; };
    static const Glib::ustring aboutEventCodes();

    Info& addParameter(const Glib::ustring&, const Glib::ustring&);
    std::multimap<Glib::ustring, Glib::ustring> getParameters() const { return parameters; };
    static const Glib::ustring aboutParameters();

    Info& addResource(const Resource& in) { resources.push_back(in); return *this; };
    std::vector<Resource> getResources() const { return resources; };

    Info& addArea(const Area& in) { areas.push_back(in); return *this; };
    std::vector<Area> getAreas() const { return areas; };
    
    Info& setEvent(const Glib::ustring& in) { event = in; return *this; };
    Glib::ustring getEvent() const { return event; };
    static const Glib::ustring aboutEvent();

    Info& setUrgency(const eUrgency& in) { urgency = in; return *this; };
    Info& setUrgency(const Glib::ustring&);
    eUrgency getUrgency() const { return urgency; };
    
    Info& setSeverity(const eSeverity& in) { severity = in; return *this; };
    Info& setSeverity(const Glib::ustring&);
    eSeverity getSeverity() const { return severity; };

    Info& setCertainty(const eCertainty& in) { certainty = in; return *this; };
    Info& setCertainty(const Glib::ustring&);
    eCertainty getCertainty() const { return certainty; };

    Info& setAudience(const Glib::ustring& in) { audience = in; return *this; };
    Glib::ustring getAudience() const { return audience; };
    static const Glib::ustring aboutAudience();

    Info& setEffective(const DateTime& in) { effective = in; return *this; };
    DateTime getEffective() const { return effective; };
    static const Glib::ustring aboutEffective();
        
    Info& setOnset(const DateTime& in) { onset = in; return *this; };
    DateTime getOnset() const { return onset; };
    static const Glib::ustring aboutOnset();
    
    Info& setExpires(const DateTime& in) { expires = in; return *this;};
    DateTime getExpires() const { return expires; };
    static const Glib::ustring aboutExpires();
    
    Info& setSenderName(const Glib::ustring& in) { senderName = in; return *this;};
    Glib::ustring getSenderName() const { return senderName; };
    static const Glib::ustring aboutSenderName();

    Info& setHeadline(const Glib::ustring& in) { headline = in; return *this;};
    Glib::ustring getHeadline() const { return headline; };
    static const Glib::ustring aboutHeadline();

    Info& setDescription(const Glib::ustring& in) { description = in; return *this; };
    Glib::ustring getDescription() const { return description; };
    static const Glib::ustring aboutDescription();

    Info& setInstruction(const Glib::ustring& in) { instruction = in; return *this;};
    Glib::ustring getInstruction() const { return instruction; };
    static const Glib::ustring aboutInstruction();

    Info& setWeb(const Glib::ustring& in) { web = in; return *this; };
    Glib::ustring getWeb() const { return web; };
    static const Glib::ustring aboutWeb();

    Info& setContact(const Glib::ustring& in) { contact = in; return *this; };
    Glib::ustring getContact() const { return contact; };
    static const Glib::ustring aboutContact();

    VTEC setVTEC(const VTEC& in) { return vtec=in; };
    VTEC getVTEC() const { return vtec; };

    const Glib::ustring getPrintString() const;

  private:
    Glib::ustring language; //
    std::vector<eCategory> categories; //
    std::vector<eResponse> responses; //
    std::multimap<Glib::ustring, Glib::ustring> eventCodes;
    std::multimap<Glib::ustring, Glib::ustring> parameters;
    std::vector<Resource> resources;
    std::vector<Area> areas;

    Glib::ustring event; 
    eUrgency urgency;
    eSeverity severity;
    eCertainty certainty;
    Glib::ustring audience;
    DateTime effective;
    DateTime onset;
    DateTime expires;
    Glib::ustring senderName;
    Glib::ustring headline;
    Glib::ustring description;
    Glib::ustring instruction;
    Glib::ustring web;
    Glib::ustring contact;
    VTEC vtec;

  };
  
  class CAP {
  public:
    bool operator<(const CAP& rhs) const { return id < rhs.id; }

    Glib::ustring getTitle() const;
    bool checkArea() const;
    bool checkUGC() const;
    bool checkCoords() const;
    bool isExpired() const;

    CAP& addCode(const Glib::ustring&);
    static const Glib::ustring aboutCodes();
    std::vector<Glib::ustring> getCodes() const;

    CAP& addReference(const Glib::ustring&);
    static const Glib::ustring aboutReferences();
    std::vector<Glib::ustring> getReferences() const;

    CAP& addInfo(const Info&);
    std::vector<Info> getInfos() const;

    CAP& setId(const Glib::ustring&);
    static const Glib::ustring aboutId();
    Glib::ustring getId() const;

    CAP& setVersion(const Glib::ustring&);
    static const Glib::ustring aboutVersion();
    Glib::ustring getVersion() const;

    CAP& setSender(const Glib::ustring&);
    static const Glib::ustring aboutSender();
    Glib::ustring getSender() const;

    CAP& setSent(const DateTime&);
    static const Glib::ustring aboutSent();
    DateTime getSent() const;
    
    CAP& setStatus(const eStatus&);
    CAP& setStatus(const Glib::ustring&);
    eStatus getStatus() const;

    CAP& setMsgType(const eMsgType&);
    CAP& setMsgType(const Glib::ustring&);
    eMsgType getMsgType() const;

    CAP& setScope(const eScope&);
    CAP& setScope(const Glib::ustring&);
    eScope getScope() const;

    CAP& setSource(const Glib::ustring&);
    Glib::ustring getSource() const;
    static const Glib::ustring aboutSource();

    CAP& setRestriction(const Glib::ustring&);
    Glib::ustring getRestriction() const;
    static const Glib::ustring aboutRestriction();

    CAP& setAddresses(const Glib::ustring&);
    Glib::ustring getAddresses() const;
    static const Glib::ustring aboutAddresses();

    CAP& setNote(const Glib::ustring&);
    Glib::ustring getNote() const;
    static const Glib::ustring aboutNote();

    CAP& setIncidents(const Glib::ustring&);
    Glib::ustring getIncidents() const;
    static const Glib::ustring aboutIncidents();

    const Glib::ustring getPrintString() const;

  private:
    std::vector<Glib::ustring> codes;
    std::vector<Glib::ustring> references;
    std::vector<Info> infos;
    Glib::ustring id;
    Glib::ustring version;
    Glib::ustring sender;
    DateTime sent;
    eStatus status;
    eMsgType msgType;
    eScope scope;
    Glib::ustring source;
    Glib::ustring restriction;
    Glib::ustring addresses;
    Glib::ustring note;
    Glib::ustring incidents;


  };

  const std::map<const CAPViewer::eStatus,const Glib::ustring> statusStringMap{
    {Actual, "Actual" },
    {Exercise, "Exercise" },
    {System, "System"},
    {Test, "Test"},
    {Draft, "Draft"},
  };

  const std::map<Glib::ustring, const CAPViewer::eStatus> stringStatusMap = {
    {"Actual", Actual },
    {"Exercise", Exercise },
    {"System", System},
    {"Test", Test},
    {"Draft", Draft},
  };

  const std::map<const CAPViewer::eMsgType, Glib::ustring> msgTypeStringMap = {
    {Alert, "Alert"},
    {Update, "Update"},
    {Cancel, "Cancel"},
    {Ack, "Ack"},
    {Error, "Error"},
  };
  
  const std::map<Glib::ustring, const CAPViewer::eMsgType> stringMsgTypeMap = {
    {"Alert", Alert},
    {"Update", Update},
    {"Cancel", Cancel},
    {"Ack", Ack},
    {"Error", Error},
  };
  
  const std::map<const CAPViewer::eScope, Glib::ustring> scopeStringMap = {
    {Public, "Public" },
    {Restricted, "Restricted" },
    {Private, "Private" },
  };

  const std::map<Glib::ustring, const CAPViewer::eScope> stringScopeMap = {
    {"Public", Public },
    {"Restricted", Restricted },
    {"Private", Private },
  };

  const std::unordered_map<Glib::ustring, const CAPViewer::eCategory, std::hash<std::string>> stringCategoryMap = {
    {"Geo", Geo},
    {"Met", Met},
    {"Safety", Safety},
    {"Security", Security},
    {"Rescue", Rescue},
    {"Fire", Fire},
    {"Health", Health},
    {"Env", Env},
    {"Transport", Transport},
    {"Infra", Infra},
    {"Cbrne", Cbrne},
    {"CBRNE", Cbrne},
    {"Other", Other},
  };

  const std::map<CAPViewer::eCategory, const Glib::ustring> categoryStringMap = {
    {Geo, "Geo"},
    {Met, "Met"},
    {Safety, "Safety"},
    {Security, "Security"},
    {Rescue, "Rescue"},
    {Fire, "Fire"},
    {Health, "Health"},
    {Env, "Env"},
    {Transport, "Transport"},
    {Infra, "Infra"},
    {Cbrne, "Cbrne"},
    {Other, "Other"},
  };
  
  const std::unordered_map<Glib::ustring, const CAPViewer::eResponse, std::hash<std::string>> stringResponseMap = {
    {"Shelter", Shelter},
    {"Evacuate", Evacuate},
    {"Prepare", Prepare},
    {"Execute", Execute},
    {"Avoid", Avoid},
    {"Monitor", Monitor},
    {"Assess", Assess},
    {"All Clear", AllClear},
    {"AllClear", AllClear},
    {"None", None},
  };

  const std::map<CAPViewer::eResponse, const Glib::ustring> responseStringMap = {
    {Shelter, "Shelter"},
    {Evacuate, "Evacuate"},
    {Prepare, "Prepare"},
    {Execute, "Execute"},
    {Avoid, "Avoid"},
    {Monitor, "Monitor"},
    {Assess, "Assess"},
    {AllClear, "All Clear"},
    {None, "None"},
  };
  
  const std::map<Glib::ustring, const CAPViewer::eUrgency> stringUrgencyMap = {
    {"Immediate", uImmediate},
    {"Expected", uExpected},
    {"Future", uFuture},
    {"Past", uPast},
    {"Unknown", uUnknown},
  };

  const std::map<CAPViewer::eUrgency, const Glib::ustring> urgencyStringMap = {
    {uImmediate, "Immediate"},
    {uExpected, "Expected"},
    {uFuture, "Future"},
    {uPast, "Past"},
    {uUnknown, "Unknown"},
  };

  const std::map<Glib::ustring, const CAPViewer::eSeverity> stringSeverityMap = {
    {"Extreme", sExtreme},
    {"Severe", sSevere},
    {"Moderate", sModerate},
    {"Minor", sMinor},
    {"Unknown", sUnknown},
  };

  const std::map<CAPViewer::eSeverity, Glib::ustring> severityStringMap = {
    {sExtreme, "Extreme"},
    {sSevere, "Severe"},
    {sModerate, "Moderate"},
    {sMinor, "Minor"},
    {sUnknown, "Unknown"},
  };
    
  const std::map<Glib::ustring, const CAPViewer::eCertainty> stringCertaintyMap = {
    {"Observed", cObserved},
    {"Likely", cLikely},
    {"Possible", cPossible},
    {"Unlikely", cUnlikely},
    {"Unknown", cUnknown},
  };

  const std::map<CAPViewer::eCertainty, const Glib::ustring> certaintyStringMap = {
    {cObserved, "Observed"},
    {cLikely, "Likely"},
    {cPossible, "Possible"},
    {cUnlikely, "Unlikely"},
    {cUnknown, "Unknown"},
  };

  const Glib::ustring aboutErrorText = _("(Internal error generating explaination text)");

  const std::map<const CAPViewer::eStatus, const Glib::ustring> aboutStatusMap = {
    {Actual, _("Actionable by all targeted recipients")},
    {Exercise, _("Actionable only by designated exercise participants; exercise identifier should appear in <note>")},
    {System, _("For messages that support alert network internal functions")},
    {Test, _("Technical testing only, all recipients disregard")},
    {Draft, _("A preliminary template or draft, not actionable in its current form")},
  };

  const std::map<const CAPViewer::eMsgType, const Glib::ustring> aboutMsgTypeMap = {
    {Alert, _("Initial information requiring attention by targeted recipients")},
    {Update, _("Updates and supercedes the earlier message(s) identified in <references>")},
    {Cancel, _("Cancels the earlier message(s) identified in <references>")},
    {Ack, _("Acknowledges receipt and acceptance of the message(s)) identified in <references>")},
    {Error, _("Indicates rejection of the message(s) identified in <references>; explanation should appear in <note>")},
  };

  const std::map<const CAPViewer::eScope, const Glib::ustring> aboutScopeMap = {
    {Public, _("For general dissemination to unrestricted audience")},
    {Restricted, _("For dissemination only to users with a known operational requirement (see <restriction>)")},
    {Private, _("For dissemination only to specified addresses (see <address>)")},
  };

  const std::map<const CAPViewer::eCategory, const Glib::ustring> aboutCategoryMap = {
    {Geo, _("Geophysical (inc. landslide")}, 
    {Met, _("Meteorological (inc. flood)")},
    {Safety, _("General emergency and public safety")},
    {Security, _("Law enforcement, military, homeland and local/private security")},
    {Rescue, _("Rescue and recovery")},
    {Fire, _("Fire suppression and rescue")},
    {Health, _("Medical and public health")},
    {Env, _("Pollution and other environmental")},
    {Transport, _("Public and private transportation")},
    {Infra, _("Utility, telecommunication, other non-transport infrastructure")},
    {Cbrne, _("Chemical, Biological, Radiological, Nuclear or High-Yield Explosive threat or attack")},
    {Other, _("Other events")},
  };

  const std::map<const CAPViewer::eResponse, const Glib::ustring> aboutResponseMap = {
    {Shelter, _("Take shelter in place or per <instruction>")},
    {Evacuate, _("Relocate as instructed in the <instruction>")},
    {Prepare, _("Make preparations per the <instruction>")},
    {Execute, _("Execute a pre-planned activity identified in <instruction>")},
    {Avoid, _("Avoid the subject event as per the <instruction>")},
    {Monitor, _("Attend to information sources as described in <instruction>")},
    {Assess, _("Evaluate the information in this message")},
    {AllClear, _("The subject event no longer poses a threat or concern and any follow on action is described in <instruction>")},
    {None, _("No action recommended")},
  };

  const std::map<const CAPViewer::eUrgency, const Glib::ustring> aboutUrgencyMap = {
    {uImmediate, _("Responsive action should be taken immediately")},
    {uExpected, _("Responsive action should be taken soon (within next hour)")},
    {uFuture, _("Responsive action should be taken in the near future")},
    {uPast, _("Responsive action is no longer required")},
    {uUnknown, _("Urgency not known")},
  };

  const std::map<const CAPViewer::eSeverity, const Glib::ustring> aboutSeverityMap = {
    {sExtreme, _("Extraordinary threat to life or property")},
    {sSevere, _("Significant threat to life or property")},
    {sModerate, _("Possible threat to life or property")},
    {sMinor, _("Minimal to no known threat to life or property")},
    {sUnknown, _("Severity unknown")},
  };

  const std::map<const CAPViewer::eCertainty, const Glib::ustring> aboutCertaintyMap = {
    {cObserved, _("Determined to have occurred or to be ongoing")},
    {cLikely, _("Likely (p > ~50%)")},
    {cPossible, _("Possible but not likely (p <= ~50%)")},
    {cUnlikely, _("Not expected to occur (p ~ 0)")},
    {cUnknown, _("Certainty unknown")},
  };


} // namespace CAPViewer



#endif
