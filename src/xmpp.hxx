#ifndef XMPP_H
#define XMPP_H
#include <memory>
#include <glibmm.h>
#include <strophe.h>
#include "cap.hxx"

namespace CAPViewer {

  class MessageHandlerFunctor {
    xmpp_ctx_t* m_ctx;
    sigc::signal<void, std::vector<std::shared_ptr<CAPViewer::CAP>>>* m_signal_ptr;

  public:
    explicit MessageHandlerFunctor(xmpp_ctx_t* ctx, sigc::signal<void, std::vector<std::shared_ptr<CAPViewer::CAP>>>* signal_ptr) : m_ctx(ctx), m_signal_ptr(signal_ptr) {};
    int operator() (xmpp_conn_t * const conn,
		    xmpp_stanza_t * const stanza);
  };

  class ConnectionHandlerFunctor {
    xmpp_ctx_t* m_ctx;
    MessageHandlerFunctor* m_MsgHandler;
  public:
    explicit ConnectionHandlerFunctor(xmpp_ctx_t* ctx, MessageHandlerFunctor* msgHandler) : m_ctx(ctx), m_MsgHandler(msgHandler) {};
    void operator() (xmpp_conn_t * const conn,
		     const xmpp_conn_event_t status,
		     const int error,
		     xmpp_stream_error_t * const stream_error);
  };

  class XmppClient { 
  public:
    explicit XmppClient();
    ~XmppClient();
    void run();
    void die();

    sigc::signal<void, std::vector<std::shared_ptr<CAPViewer::CAP>>> signal_cap;
  private:
    void init();

    xmpp_log_t* log;
    xmpp_ctx_t* ctx;
    xmpp_conn_t* conn;
    MessageHandlerFunctor m_MsgHandler;
    ConnectionHandlerFunctor m_ConnHandler;
  };

}


#endif
