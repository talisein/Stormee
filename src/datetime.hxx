#ifndef DATETIME_HXX
#define DATETIME_HXX
#include <glibmm/ustring.h>
#include <time.h>

namespace CAPViewer {
  class DateTime {
  public:
    DateTime(const Glib::ustring& in) : tmp(in) {};
    DateTime();
    virtual ~DateTime();
    DateTime& convertFromString(const Glib::ustring&);
    Glib::ustring toString() const;
    DateTime& operator()(const Glib::ustring& in) { return this->convertFromString(in); };
  private:
    time_t     now;
    struct tm  *ts;
    Glib::ustring tmp;

  }; 
  
}
#endif
