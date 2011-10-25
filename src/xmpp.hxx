#ifndef XMPP_H
#define XMPP_H
#include <memory>
#include <glibmm.h>
#include <strophe.h>
#include "cap.hxx"

namespace CAPViewer {
  class XmppClient { 
  public:
    explicit XmppClient();
    ~XmppClient();

    void run();
    void die();

    static sigc::signal<void, std::vector<std::shared_ptr<CAPViewer::CAP>>> signal_cap;
  private:
    void init();
    static void conn_handler(xmpp_conn_t * const conn __attribute__((unused)), 
		  const xmpp_conn_event_t status, 
		  const int error __attribute__((unused)), 
		  xmpp_stream_error_t * const stream_error __attribute__((unused)),
		      void * const userdata );
    static int message_handler(xmpp_conn_t * const conn __attribute__((unused)), xmpp_stanza_t * const stanza, void * const userdata);

    xmpp_log_t* log;
    xmpp_ctx_t* ctx;
    xmpp_conn_t* conn;
  
  };

}


#endif
