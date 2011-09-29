#include <gtkmm/builder.h>

namespace CAPViewer {
  namespace Util {
    Glib::RefPtr<Gtk::Builder> getGtkBuilder();
    Glib::ustring squish(Glib::ustring);
  }
}
