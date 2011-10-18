#include <iostream>
#include <glibmm/convert.h>
#include <glib.h>
#include "capreader.hxx"
#include "util.h"

CAPViewer::CAPReader::CAPReader() : inEventCode(false), inParameter(false), inGeocode(false) {
}

CAPViewer::CAPReader::~CAPReader() {
  cap.reset();
}

CAPViewer::CAPReaderFile::~CAPReaderFile() {
}

CAPViewer::CAPReaderFile::CAPReaderFile(const Glib::RefPtr<const Gio::File>& f) : CAPViewer::CAPReader(), file(f) {

}

void CAPViewer::CAPReaderFile::do_parse() {
  parse_file(file->get_uri());
}

void CAPViewer::CAPReader::on_start_document() {
}

void CAPViewer::CAPReader::on_end_document() {
}


void CAPViewer::CAPReader::on_start_element(const Glib::ustring& name, 
					    const AttributeList& attributes) {
  str_buf.clear();

  if (name.find("alert") != Glib::ustring::npos) {
    cap = std::shared_ptr<CAPViewer::CAP>(new CAPViewer::CAP());
    node = nAlert;
    g_message("Starting a new alert!");
    for (auto attr : attributes) {
      if (attr.name.find("xmlns") != Glib::ustring::npos)
	cap->setVersion(attr.value);
    }
  } else if (name.find("identifier") != Glib::ustring::npos) {
    node = nIdentifier;
  } else if (name.find("senderName") != Glib::ustring::npos) {
    node = nSenderName;
  } else if (name.find("sender") != Glib::ustring::npos) {
    node = nSender;
  } else if (name.find("sent") != Glib::ustring::npos) {
    node = nSent;
  } else if (name.find("status") != Glib::ustring::npos) {
    node = nStatus;
  } else if (name.find("msgType") != Glib::ustring::npos) {
    node = nMsgType;
  } else if (name.find("scope") != Glib::ustring::npos) {
    node = nScope;
  } else if (name.find("restriction") != Glib::ustring::npos) {
    node = nRestriction;
  } else if (name.find("addresses") != Glib::ustring::npos) {
    node = nAddresses;
  } else if (name.find("note") != Glib::ustring::npos) {
    node = nNote;
  } else if (name.find("references") != Glib::ustring::npos) {
    node = nReferences;
  } else if (name.find("incidents") != Glib::ustring::npos) {
    node = nIncidents;
  } else if (name.find("info") != Glib::ustring::npos) {
    node = nInfo;
    info = std::shared_ptr<CAPViewer::Info>(new CAPViewer::Info());
  } else if (name.find("language") != Glib::ustring::npos) {
    node = nLanguage;
  } else if (name.find("category") != Glib::ustring::npos) {
    node = nCategory;
  } else if (name.find("responseType") != Glib::ustring::npos) {
    node = nResponse;
  } else if (name.find("urgency") != Glib::ustring::npos) {
    node = nUrgency;
  } else if (name.find("severity") != Glib::ustring::npos) {
    node = nSeverity;
  } else if (name.find("certainty") != Glib::ustring::npos) {
    node = nCertainty;
  } else if (name.find("audience") != Glib::ustring::npos) {
    node = nAudience;
  } else if (name.find("eventCode") != Glib::ustring::npos) {
    node = nEventCode;
    inEventCode = true;
  } else if (name.find("code") != Glib::ustring::npos) {
    node = nCode;
  } else if (name.find("event") != Glib::ustring::npos) {
    node = nEvent;
  } else if (name.find("valueName") != Glib::ustring::npos) {
    node = nValueName;
  }  else if (name.find("value") != Glib::ustring::npos) {
    node = nValue;
  }  else if (name.find("effective") != Glib::ustring::npos) {
    node = nEffective;
  }  else if (name.find("onset") != Glib::ustring::npos) {
    node = nOnset;
  }  else if (name.find("expires") != Glib::ustring::npos) {
    node = nExpires;
  }  else if (name.find("headline") != Glib::ustring::npos) {
    node = nHeadline;
  }  else if (name.find("description") != Glib::ustring::npos) {
    node = nDescription;
  }  else if (name.find("instruction") != Glib::ustring::npos) {
    node = nInstruction;
  }  else if (name.find("web") != Glib::ustring::npos) {
    node = nWeb;
  }  else if (name.find("contact") != Glib::ustring::npos) {
    node = nContact;
  }  else if (name.find("parameter") != Glib::ustring::npos) {
    node = nParameter;
    inParameter = true;
  }  else if (name.find("area") != Glib::ustring::npos) {
    node = nArea;
    area = std::shared_ptr<CAPViewer::Area>(new CAPViewer::Area());
  }  else if (name.find("areaDesc") != Glib::ustring::npos) {
    node = nAreaDesc;
  }  else if (name.find("altitude") != Glib::ustring::npos) {
    node = nAltitude;
  }  else if (name.find("ceiling") != Glib::ustring::npos) {
    node = nCeiling;
  }  else if (name.find("polygon") != Glib::ustring::npos) {
    node = nPolygon;
  }  else if (name.find("geocode") != Glib::ustring::npos) {
    node = nGeocode;
    inGeocode = true;
  }  else if (name.find("circle") != Glib::ustring::npos) {
    node = nCircle;
  } else if (name.find("resourceDesc") != Glib::ustring::npos) {
    node = nResourceDesc;
  } else if (name.find("mimeType") != Glib::ustring::npos) {
    node = nMimeType;
  } else if (name.find("size") != Glib::ustring::npos) {
    node = nSize;
  } else if (name.find("derefUri") != Glib::ustring::npos) {
    node = nDerefUri;
  } else if (name.find("uri") != Glib::ustring::npos) {
    node = nUri;
  } else if (name.find("digest") != Glib::ustring::npos) {
    node = nDigest;
  } else if (name.find("resource") != Glib::ustring::npos) {
      node = nResource;
      resource = std::shared_ptr<CAPViewer::Resource>(new CAPViewer::Resource());
  } else if (name.find("source") != Glib::ustring::npos) {
    node = nSource;
  } else {
    g_message("Unknown CAP field '%s'", name.c_str());
  }
}

void CAPViewer::CAPReader::on_end_element(const Glib::ustring& name) {
  str_buf = CAPViewer::Util::squish(str_buf);
  switch (node) {
  case nIdentifier: cap->setId(str_buf);
    break;
  case nSender: cap->setSender(str_buf);
    break;
  case nSent: cap->setSent(str_buf);
    break;
  case nStatus: cap->setStatus(str_buf);
    break;
  case nMsgType: cap->setMsgType(str_buf);
    break;
  case nSource: cap->setSource(str_buf);
    break;
  case nScope: cap->setScope(str_buf);
    break;
  case nRestriction: cap->setRestriction(str_buf);
    break;
  case nAddresses: cap->setAddresses(str_buf);
    break;
  case nCode: cap->addCode(str_buf);
    break;
  case nNote: cap->setNote(str_buf);
    break;
  case nReferences: cap->addReference(str_buf);
    break;
  case nIncidents: cap->setIncidents(str_buf);
    break;
  case nInfo: 
    break;
  case nLanguage: info->setLanguage(str_buf);
    break;
  case nCategory: info->addCategory(str_buf);
    break;
  case nResponse: info->addResponse(str_buf);
    break;
  case nEvent: info->setEvent(str_buf);
    break;
  case nUrgency: info->setUrgency(str_buf);
    break;
  case nSeverity: info->setSeverity(str_buf);
    break;
  case nCertainty: info->setCertainty(str_buf);
    break;
  case nAudience: info->setAudience(str_buf);
    break;
  case nEventCode:
    break;
  case nValueName: 
    valueName = str_buf;
    break;
  case nValue: 
    if (inEventCode) {
      info->addEventCode(valueName, str_buf);
    } else if (inParameter)
      info->addParameter(valueName, str_buf);
    else if (inGeocode)
      area->addGeoCode(valueName, str_buf);
    break;
  case nEffective: info->setEffective(str_buf);
    break;
  case nOnset: info->setOnset(str_buf);
    break;
  case nExpires: info->setExpires(str_buf);
    break;
  case nSenderName: info->setSenderName(str_buf);
    break;
  case nHeadline: info->setHeadline(str_buf);
    break;
  case nDescription: info->setDescription(str_buf);
    break;
  case nInstruction: info->setInstruction(str_buf);
    break;
  case nWeb: info->setWeb(str_buf);
    break;
  case nContact: info->setContact(str_buf);
    break;
  case nParameter: 
    break;
  case nArea: 
    break;
  case nAreaDesc: area->setAreaDesc(str_buf);
    break;
  case nAltitude: area->setAltitude(str_buf);
    break;
  case nCeiling: area->setCeiling(str_buf);
    break;
  case nPolygon:
    if (!str_buf.empty()) {
      try {
	polygon = std::shared_ptr<CAPViewer::Polygon>(new CAPViewer::Polygon(str_buf));
	area->addPolygon(*polygon);
      } catch (CAPViewer::CoordinateParseError e) {
	g_warning("While parsing a polygon parameter, encountered error '%s'", e.what());
      }
    }
    break;
  case nCircle: 
    try {
    circle = std::shared_ptr<CAPViewer::Circle>(new CAPViewer::Circle(str_buf));
    area->addCircle(*circle);
    } catch (CAPViewer::CoordinateParseError e) {
      g_warning("While parsing a circle parameter, encountered error '%s'", e.what());
    }
    break;
  case nGeocode: 
    break;
  case nResourceDesc: 
      resource->setResourceDesc(str_buf);
    break;
  case nMimeType: 
      resource->setMimeType(str_buf);
    break;
  case nSize: 
    try {
	resource->setSize(str_buf);
    } catch (CAPViewer::SizeParseError e) {
      g_warning("Failed to convert resource's size parameter to internal type (%s)", e.what());
      // TODO: Size is probably sent to max guint64. 
    }
    break;
  case nUri: 
      resource->setUri(str_buf);
    break;
  case nDerefUri: 
      resource->setDerefUri(str_buf);
    break;
  case nDigest: 
      resource->setDigest(str_buf);
    break;
  default:
    if (!str_buf.empty() && str_buf.find_first_not_of("\n\t\r ") != Glib::ustring::npos)
      g_warning("Characters found in unknown node %s: '%s'", name.c_str(), str_buf.c_str());
  }

  str_buf.clear();

  if (name.find("alert") != Glib::ustring::npos) {
    caps.push_back(cap);
    g_message("Pushed a full <alert>!");
  } else if (name.find("info") != Glib::ustring::npos) {
    cap->addInfo(*info);
  } else if (name.find("area") != Glib::ustring::npos) {
    if ( name.find("areaDesc") == Glib::ustring::npos) {
      info->addArea(*area);
    }
  } else if ( name.find("resource") != Glib::ustring::npos) {
    if ( name.find("resourceDesc") == Glib::ustring::npos ) {
	info->addResource(*resource);
    }
  } else if (name.find("eventCode") != Glib::ustring::npos) {
    inEventCode = false;
    valueName.clear();
  } else if (name.find("parameter") != Glib::ustring::npos) {
    inParameter = false;
    valueName.clear();
  } else if (name.find("geocode") != Glib::ustring::npos) {
    inGeocode = false;
    valueName.clear();
  }

  node = nNone;
}

void CAPViewer::CAPReader::on_characters(const Glib::ustring& text) {
  str_buf += text;
}

void CAPViewer::CAPReader::on_comment(const Glib::ustring& text) {
  g_debug("Encountered comment in XML: %s", text.c_str());
}

void CAPViewer::CAPReader::on_warning(const Glib::ustring& text) {
  g_warning("While parsing CAP XML: %s", text.c_str());
}

void CAPViewer::CAPReader::on_error(const Glib::ustring& text) {
  g_critical("While parsing CAP XML: %s", text.c_str());
}

void CAPViewer::CAPReader::on_fatal_error(const Glib::ustring& text) {
  g_critical("While parsing CAP XML: %s", text.c_str());
}



