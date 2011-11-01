#include <memory>
#include "notify.hxx"
#include "util.hxx"

CAPViewer::Notification::Notification(const Glib::ustring& summary, const Glib::ustring& body, const Glib::RefPtr<Gio::DBus::Proxy>& proxy) : app_name(Glib::Variant<Glib::ustring>::create("Stormee")), replaces_id(Glib::Variant<guint32>::create(0)),  icon(Glib::Variant<Glib::ustring>::create("")),  m_summary(Glib::Variant<Glib::ustring>::create(summary)),  m_body(Glib::Variant<Glib::ustring>::create(body)), expire_timeout(Glib::Variant<gint32>::create(-1)), m_proxy(proxy) {
  actions = Glib::Variant<std::vector<Glib::ustring>>::create(std::vector<Glib::ustring>());
  hints = Glib::Variant<std::map<Glib::ustring,Glib::ustring>>::create(std::map<Glib::ustring, Glib::ustring>());
}

void CAPViewer::Notification::show() {
  //  Glib::Variant<std::vector<Glib::VariantBase>> parameters{app_name, replaces_id, icon, m_summary, m_body, actions, hints, expire_timeout };

  std::vector<Glib::VariantBase> vec = { app_name, replaces_id, icon, m_summary, m_body, actions, hints, expire_timeout };

  Glib::VariantContainerBase parameters = Glib::VariantContainerBase::create_tuple(vec);
  m_proxy->call("Notify", // method name
		sigc::bind<-1>(sigc::mem_fun(*this, &CAPViewer::Notification::show_finish),m_proxy),
		     parameters, // Parameters
		     -1, // timeout
		     Gio::DBus::CallFlags::CALL_FLAGS_NONE);
  
}

// We pass the proxy in because the calling object may have been destroyed already.
void CAPViewer::Notification::show_finish(const Glib::RefPtr< Gio::AsyncResult >& res, const Glib::RefPtr<Gio::DBus::Proxy>& proxy) {
  proxy->call_finish(res);
}

void CAPViewer::Notification::Notify(const CAPViewer::CAP& cap, const Glib::RefPtr<Gio::DBus::Proxy>& proxy) {
  std::shared_ptr<CAPViewer::Notification> notice;
  if (cap.getInfos().size() > 0)
    notice = std::shared_ptr<CAPViewer::Notification>(new CAPViewer::Notification(cap.getTitle(), cap.getInfos().begin()->getHeadline(), proxy));
  else
    notice = std::shared_ptr<CAPViewer::Notification>(new CAPViewer::Notification(cap.getTitle(), "", proxy));

  notice->show();
}
