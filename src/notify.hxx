#include <glibmm/thread.h>
#include <glibmm/refptr.h>
#include <giomm/dbusproxy.h>
#include <glibmm/variant.h>

#include "cap.hxx"
namespace CAPViewer {
  class Notification {
  public:
    Notification(const Glib::ustring& summary, const Glib::ustring& body, const Glib::RefPtr<Gio::DBus::Proxy>& proxy );
    static void Notify(const CAPViewer::CAP& cap, const Glib::RefPtr<Gio::DBus::Proxy>& proxy);
    void show();
    void show_finish(const Glib::RefPtr< Gio::AsyncResult >& res, const Glib::RefPtr<Gio::DBus::Proxy>& proxy);

  private:
    Glib::Variant<Glib::ustring> app_name;
    Glib::Variant<guint32> replaces_id;
    Glib::Variant<Glib::ustring> icon;
    Glib::Variant<Glib::ustring> m_summary;
    Glib::Variant<Glib::ustring> m_body;
    Glib::Variant<std::vector<Glib::ustring>> actions;
    Glib::Variant<std::map<Glib::ustring, Glib::ustring>> hints;
    Glib::Variant<gint32> expire_timeout;
    Glib::RefPtr<Gio::DBus::Proxy> m_proxy;
  };
}
