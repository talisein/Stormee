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

Glib::ustring CAPViewer::Util::getCenterCoords() {
  return "38.56513, -121.75156"; // TODO
}

Glib::ustring CAPViewer::Util::getMapHeaderText() {
  Glib::ustring out("<!DOCTYPE html>\n"					\
		    "<html>\n"						\
		    "<head>\n"						\
		    "<meta name=\"viewport\" content=\"initial-scale=1.0, user-scalable=yes\" />\n" \
		    "<style type=\"text/css\">\n"			\
		    "html { height: 100% }\n"				\
		    "body { height: 100%; margin: 0; padding: 0 }\n"	\
		    "#map_canvas { height: 100% }\n"			\
		    "</style>\n"					\
		    "<script type=\"text/javascript\" src=\"http://maps.google.com/maps/api/js?sensor=false\"></script>\n" \
		    "<script type=\"text/javascript\">\n"		\
		    "\n"						\
		    "  function initialize() {\n"			\
		    "\n"						\
		    "    var myLatLng = new google.maps.LatLng(");
  out += CAPViewer::Util::getCenterCoords();
  out += ");\n"								\
    "    var myOptions = {\n"						\
    "      zoom: 6,\n"							\
    "      center: myLatLng,\n"						\
    "      mapTypeId: google.maps.MapTypeId.ROADMAP\n"			\
    "    };\n"								\
    "\n"								\
    "var map = new google.maps.Map(document.getElementById(\"map_canvas\"),\n" \
    "          myOptions);\n"						\
    "\n";
  return out;
}

Glib::ustring CAPViewer::Util::getMapPolygon(const CAPViewer::Polygon& polygon, int idx) {
  std::stringstream out;
  out << "var poly" << idx << "Coords = [" << std::endl;
  for (auto coord : polygon.getPoints() ) {
    out << "new google.maps.LatLng(" << coord.getLatitude() << "," 
	<< coord.getLongitude() << ")," << std::endl;
  }
  out << "]; " << std::endl << "var poly" << idx 
      << " = new google.maps.Polygon({" << std::endl
      << " paths: poly" << idx << "Coords,\n" << std::endl
      << " strokeColor: \"#FF0000\",\n" << std::endl
      << " strokeOpacity: 0.8,\n" << std::endl
      << " strokeWeight: 2,\n" << std::endl
      << " fillColor: \"#FF0000\",\n" << std::endl
      << " fillOpacity: 0.35\n" << std::endl
      << " }); \n" << std::endl
      << " poly" << idx << ".setMap(map);\n" << std::endl;
  return out.str();
}

Glib::ustring CAPViewer::Util::getMapCircle(const CAPViewer::Circle& circle, int idx) {
  std::stringstream out;
  out << "var circle" << idx << "Center = new google.maps.LatLng(" 
      << circle.getCoords().getLatitude() << "," 
      << circle.getCoords().getLongitude() << ");" << std::endl
      << "var circle" << idx << " = new google.maps.Circle({" << std::endl
      << "strokeColor: \"#FF0000\"," << std::endl
      << "strokeOpacity: 0.8," << std::endl
      << "strokeWeight: 2," << std::endl
      << "fillColor: \"#FF0000\"," << std::endl
      << "fillOpacity: 0.35," << std::endl
      << "map: map," << std::endl
      << "center: circle" << idx << "Center," << std::endl
      << "radius: " << circle.getRadius()*1000 /* Meters */ << std::endl
      << "});" << std::endl
      << "circle" << idx << ".setMap(map)" << std::endl;
  return out.str();
}

Glib::ustring CAPViewer::Util::getMapFooterText() {
  return "}\n"								\
    "</script>\n"							\
    "</head>\n"								\
    "<body onload=\"initialize()\">\n"					\
    "<div id=\"map_canvas\" style=\"width:100%; height:100%\"></div>\n"	\
    "</body>\n"								\
    "</html>\n";
}
