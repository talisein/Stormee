#ifndef LOG_HPP
#define LOG_HPP
#include <iostream>
#include <string>
#include <glibmm/thread.h>


namespace CAPViewer {
  class Log {
  public:
    virtual ~Log();

    static void debug(const Glib::ustring&);
    static void info(const Glib::ustring&);
    static void warn(const Glib::ustring&);
    //    static void error(const char*);
    static void error(const Glib::ustring&);
    static Log& getLog();

  
    static Glib::Mutex* mutex;

  private:
    static void init();
    Log();
    Log(const Log&); // Prevent copy-construction
    Log& operator=(const Log&); // Prevent assignment

  };
}
#endif
