#include <memory>
#include "notify.hxx"
#include "util.hxx"

CAPViewer::Notification::Notification(const Glib::ustring& summary, const Glib::ustring& body) : notification(summary, body) {
  // TODO: Figure out if this isn't thread safe
  if ( !Notify::is_initted() )
    Notify::init(CAPViewer::Util::getAppName());
}

void CAPViewer::Notification::Notify(const CAPViewer::CAP& cap) {
  std::shared_ptr<CAPViewer::Notification> notice;
  if (cap.getInfos().size() > 0)
    notice = std::shared_ptr<CAPViewer::Notification>(new CAPViewer::Notification(cap.getTitle(), cap.getInfos().begin()->getHeadline()));
  else
    notice = std::shared_ptr<CAPViewer::Notification>(new CAPViewer::Notification(cap.getTitle(), ""));

  notice->notification.show();
}
