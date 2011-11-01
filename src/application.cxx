#include <functional>
#include <algorithm>
#include <gtkmm/filechooserdialog.h>
#include <gtkmm/imagemenuitem.h>
#include <gtkmm/main.h>
#include <gtkmm/stock.h>
#include "application.hxx"
#include "capreader.hxx"
#include "notify.hxx"
#include "util.hxx"

CAPViewer::Application::Application(int argc, char *argv[]) : 
  m_kit(argc, argv), 
  xmpp_client_ptr(new CAPViewer::XmppClient()),
  xmppConnection(xmpp_client_ptr->signal_cap.connect(sigc::mem_fun(*this, &CAPViewer::Application::produce_cap_from_xmpp)))
{
  auto refBuilder = CAPViewer::Util::getGtkBuilder();
  refBuilder->get_widget_derived("mainWindow", m_window);

  // Connect consumption signal 
  signal_cap_in_queue.connect(sigc::mem_fun(*this, &CAPViewer::Application::consume_cap));

  // Connect file production signal
  Gtk::ImageMenuItem* openFileItem = 0;
  refBuilder->get_widget("openFileMenuItem", openFileItem);
  if (openFileItem) {
    openFileItem->signal_activate().connect( sigc::mem_fun(this, &CAPViewer::Application::signal_open_from_file ));
  } else {
    // TODO: Error condition
  }

  dbus_init();
}

void CAPViewer::Application::dbus_init() {
  try {
    dbus_proxy = Gio::DBus::Proxy::create_for_bus_sync(Gio::DBus::BusType::BUS_TYPE_SESSION,
				     "org.freedesktop.Notifications", // name
				     "/org/freedesktop/Notifications", // object path
				     "org.freedesktop.Notifications", // interface name
				     Glib::RefPtr<Gio::DBus::InterfaceInfo>(),
				     Gio::DBus::ProxyFlags::PROXY_FLAGS_DO_NOT_LOAD_PROPERTIES); // ProxyFlags
  } catch (Glib::Error e) {
    g_error("Got Glib:Error in dbus_init()");
  }

  if (!dbus_proxy) {
    g_error("Couldn't get the DBus Notification proxy");
  }
}

void CAPViewer::Application::run() {
  xmpp_thread_ptr = Glib::Thread::create(sigc::mem_fun(*xmpp_client_ptr, &CAPViewer::XmppClient::run), true);
  m_kit.run(*m_window);

}

CAPViewer::Application::~Application() {
  // TODO: We are assuming that die() is thread safe. >_>
  xmpp_client_ptr->die();
  xmpp_thread_ptr->join();
  xmppConnection.disconnect();
  xmpp_client_ptr.reset();
}

// Called on the main loop
void CAPViewer::Application::consume_cap() {
  Glib::Mutex::Lock lock(mutex);
  
  while ( !queue_cap.empty() ) {
    CAPViewer::CAP cap = queue_cap.front(); queue_cap.pop();
    if ( seen_caps.count(cap) < 1 ) {
      seen_caps.insert(cap);
      CAPViewer::Notification::Notify(cap, dbus_proxy);

      m_window->display_cap(cap);
    }
  }
}

// Called from the XMPP thread
void CAPViewer::Application::produce_cap_from_xmpp(const std::vector<std::shared_ptr<CAPViewer::CAP>> &caps) {
  for (auto capptr : caps) {
    Glib::Mutex::Lock lock(mutex);
    queue_cap.push(*capptr);
  }

  signal_cap_in_queue();
}

// Called from the file reading thread
void CAPViewer::Application::produce_cap_from_file(Glib::RefPtr<Gio::File> fptr) {
  CAPViewer::CAPReaderFile reader(fptr);
  reader.do_parse();
  
  {
    for ( auto capptr : reader.getCAPs() ) {
      Glib::Mutex::Lock lock(mutex);
      queue_cap.push(*capptr);
    }
  }
  
  signal_cap_in_queue();
}



// Called on main loop thread
void CAPViewer::Application::signal_open_from_file() {
  Gtk::FileChooserDialog fcd("Please choose a CAP file", Gtk::FILE_CHOOSER_ACTION_OPEN);
  
  fcd.set_transient_for(*m_window);
  fcd.add_button(Gtk::Stock::CANCEL, Gtk::RESPONSE_CANCEL);
  fcd.add_button(Gtk::Stock::OPEN, Gtk::RESPONSE_OK);
  fcd.set_select_multiple(true);
  int result = fcd.run();

  if (result == Gtk::RESPONSE_OK) {
    auto files = fcd.get_files();
    std::for_each(files.begin(), files.end(), [this](const Glib::RefPtr<Gio::File>& fptr) {
	Glib::Thread::create(sigc::bind(sigc::mem_fun(*this, &CAPViewer::Application::produce_cap_from_file),fptr), false);
      });
  } 
  
  return;
}
