#include <set>
#include <queue>
#include <vector>
#include <giomm/file.h>
#include <glibmm/dispatcher.h>
#include <glibmm/thread.h>
#include <glibmm/refptr.h>
#include <sigc++/connection.h>
#include "main_window.hxx"
#include "xmpp.hxx"
#include "cap.hxx"


namespace CAPViewer {
  class Application {
  public:
    explicit Application(int argc, char *argv[]);
    ~Application();
    void run();


  private:
    void consume_cap();
    void produce_cap_from_file(Glib::RefPtr<Gio::File> fptr);
    void produce_cap_from_xmpp(const std::vector<std::shared_ptr<CAPViewer::CAP>>&);
    Glib::Dispatcher signal_cap_in_queue;

    Gtk::Main m_kit;
    CAPViewer::Window* m_window;

    Glib::Mutex mutex;

    void signal_open_from_file();

    std::shared_ptr<CAPViewer::XmppClient> xmpp_client_ptr;
    Glib::Thread* xmpp_thread_ptr;
    sigc::connection xmppConnection;

    std::set<CAPViewer::CAP> seen_caps;
    std::queue<CAPViewer::CAP> queue_cap;

  };
}
