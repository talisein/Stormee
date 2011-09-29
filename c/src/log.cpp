#include "log.hpp"
#include <glibmm/thread.h>
#include <iostream>


Glib::Mutex* CAPViewer::Log::mutex = 0;

CAPViewer::Log::Log() {
  if(!Glib::thread_supported()) 
    Glib::thread_init();
  mutex = new Glib::Mutex();
}

void CAPViewer::Log::init() {
  if (mutex == 0)
    getLog();
}

void CAPViewer::Log::debug(const Glib::ustring& msg) {
  init();
  Glib::Mutex::Lock lock (*mutex);
  
  std::cerr << "Debug: " << msg << std::endl;
}

void CAPViewer::Log::info(const Glib::ustring& msg) {
  init();
  Glib::Mutex::Lock lock (*mutex);
  
  std::cerr << "Info: " << msg << std::endl;
}

void CAPViewer::Log::warn(const Glib::ustring& msg) {
  init();
  Glib::Mutex::Lock lock (*mutex);
  
  std::cerr << "Warning: " << msg << std::endl;
}

void CAPViewer::Log::error(const Glib::ustring& msg) {
  init();
  Glib::Mutex::Lock lock (*mutex);
  
  std::cerr << "Error: " << msg << std::endl;
}

/*
void CAPViewer::Log::error(const Glib::ustring& msg) {
  init();
  Glib::Mutex::Lock lock (*mutex);
  
  std::cerr << "Error: " << msg << std::endl;
}
*/

CAPViewer::Log& CAPViewer::Log::getLog()
 {
  static Log log;
  return log;
}

CAPViewer::Log::~Log() {
  delete mutex;
}

