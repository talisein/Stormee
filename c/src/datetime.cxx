#include "datetime.hxx"

CAPViewer::DateTime::DateTime() {}
CAPViewer::DateTime::~DateTime() {}
CAPViewer::DateTime& CAPViewer::DateTime::convertFromString(const Glib::ustring& in) {
  tmp = in;
  // TODO: this function :(
  // 2002-05-24T16:49:00-07:00
  return *this;
}

Glib::ustring CAPViewer::DateTime::toString() const {
  return tmp;
}
