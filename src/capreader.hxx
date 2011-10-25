#include <glibmm.h>
#include <giomm.h>
#include <libxml++/parsers/saxparser.h>
#include <vector>
#include "cap.hxx"

namespace CAPViewer {
  class CAPReader : public xmlpp::SaxParser {
  
  public:
    CAPReader();
    virtual ~CAPReader();
    const std::vector<std::shared_ptr<CAPViewer::CAP>> getCAPs() const { return caps; };
    virtual void do_parse() = 0;

  protected:
    void on_start_document();
    void on_end_document();
    void on_start_element(const Glib::ustring& name,
				  const AttributeList& attributes);
    void on_end_element(const Glib::ustring& name);
    void on_characters(const Glib::ustring& text);
    void on_comment(const Glib::ustring& text);
    void on_warning(const Glib::ustring& text);
    void on_error(const Glib::ustring& text);
    void on_fatal_error(const Glib::ustring& text);


  private:
    std::vector<std::shared_ptr<CAPViewer::CAP>> caps;
    std::shared_ptr<CAPViewer::CAP> cap;
    std::shared_ptr<CAPViewer::Info> info;
    std::shared_ptr<CAPViewer::Area> area;
    std::shared_ptr<CAPViewer::Resource> resource;
    std::shared_ptr<CAPViewer::Circle> circle;
    std::shared_ptr<CAPViewer::Polygon> polygon;

    enum eNode {nAlert, nIdentifier, nSender, nSent, nStatus, nMsgType, nSource, nScope, nRestriction, nAddresses, nCode, nNote, nReferences, nIncidents, nInfo, nLanguage, nCategory, nResponse, nEventCode, nParameter, nValueName, nValue, nEvent, nUrgency, nSeverity, nCertainty, nAudience, nEffective, nOnset, nExpires, nSenderName, nHeadline, nDescription, nInstruction, nWeb, nContact, nArea, nPolygon, nCircle, nGeocode, nAreaDesc, nAltitude, nCeiling, nResource, nResourceDesc, nMimeType, nSize, nUri, nDerefUri, nDigest, nNone} node;
    bool inEventCode;
    bool inParameter;
    bool inGeocode;
    Glib::ustring valueName;
    Glib::ustring str_buf;
  };

  class CAPReaderFile : public CAPReader {
  public:
    explicit CAPReaderFile(const Glib::RefPtr<const Gio::File>&);
    ~CAPReaderFile();
    void do_parse();

  private:
    Glib::RefPtr<const Gio::File> file;
  };

  class CAPReaderBuffer : public CAPReader {
  public:
    explicit CAPReaderBuffer(char* buf, size_t buflen);
    ~CAPReaderBuffer();
    void do_parse();

  private:
    std::string m_string;
  };
}
