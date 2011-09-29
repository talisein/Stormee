#include "util.h"
#include "config.h"
#include <cstdlib>
#include <iostream>

Glib::ustring CAPViewer::Util::squish(Glib::ustring in) {
  Glib::ustring::size_type start, end;
  const char* wspc = " \n\t\r";
  start = in.find_first_not_of(wspc);
  end = in.find_last_not_of(wspc);
  if (start != Glib::ustring::npos && end != Glib::ustring::npos) {
    return in.substr(start, end-start+1);
  } else {
    in.clear();
    return in;
  }
}

Glib::RefPtr<Gtk::Builder> CAPViewer::Util::getGtkBuilder() {
  try {
    // TODO: Make sure glade file found from correct spot
    auto ptr = Gtk::Builder::create_from_file(CAPVIEWER_GLADE_LOCATION); 

    if (ptr) {
      return ptr;
    } else {
      std::cerr << "UnknownError: Unable to load Glade file." << std::endl;
    }

  } catch (const Glib::FileError& ex) {
    std::cerr << "FileError: " << ex.what() << std::endl;
    
  } catch (const Gtk::BuilderError& ex) {
    std::cerr << "BuilderError: " << ex.what() << std::endl;
    
  } catch (const Glib::MarkupError& ex) {
    std::cerr << "MarkupError: " << ex.what() << std::endl;
  }

  exit(EXIT_FAILURE);
}


