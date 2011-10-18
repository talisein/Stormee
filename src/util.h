#include <gtkmm/builder.h>
#include "cap.hxx"

namespace CAPViewer {
  namespace Util {
    Glib::RefPtr<Gtk::Builder> getGtkBuilder();
    Glib::ustring squish(Glib::ustring);
    Glib::ustring getCenterCoords();
    Glib::ustring getMapHeaderText();
    Glib::ustring getMapPolygon(const CAPViewer::Polygon&, int idx);
    Glib::ustring getMapCircle(const CAPViewer::Circle&, int idx);
    Glib::ustring getMapFooterText();
  }
}
