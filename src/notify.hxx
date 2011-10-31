#include <glibmm/thread.h>
#include <libnotifymm.h>
#include "cap.hxx"
namespace CAPViewer {
  class Notification {
  public:
    Notification(const Glib::ustring& summary, const Glib::ustring& body);
    static void Notify(const CAPViewer::CAP& cap);

  private:
    Notify::Notification notification;
  };

}
