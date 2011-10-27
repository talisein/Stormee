#include "xmpp.hxx"
#include "capreader.hxx"

CAPViewer::XmppClient::XmppClient() : log(xmpp_get_default_logger(XMPP_LEVEL_DEBUG)), ctx(xmpp_ctx_new(NULL, NULL)), conn(xmpp_conn_new(ctx)), m_MsgHandler(ctx, &signal_cap), m_ConnHandler(ctx, &m_MsgHandler) {
  init();
}

void CAPViewer::XmppClient::init() {
  
  xmpp_initialize();
  
  /* setup authentication information */
  xmpp_conn_set_jid(conn, "xmpp.stormee.org");

}

CAPViewer::XmppClient::~XmppClient() {
  xmpp_conn_release(conn);
  xmpp_ctx_free(ctx);
  
  /* final shutdown of the library */
  xmpp_shutdown();
  g_message("xmpp_shutdown()");
}

static void doSubscribe(xmpp_conn_t * conn, xmpp_ctx_t * ctx) {
  xmpp_stanza_t *iq, *pubsub, *subscribe;
  
  iq = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(iq, "iq");
  xmpp_stanza_set_type(iq, "set");
  xmpp_stanza_set_attribute(iq, "to", "pubsub.xmpp.stormee.org");
  xmpp_stanza_set_attribute(iq, "from", xmpp_conn_get_bound_jid(conn));
  xmpp_stanza_set_id(iq, "sub1");
 
  pubsub = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(pubsub, "pubsub");
  xmpp_stanza_set_ns(pubsub, "http://jabber.org/protocol/pubsub");
  
  subscribe = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(subscribe, "subscribe");
  xmpp_stanza_set_attribute(subscribe, "node", "Test1");
  xmpp_stanza_set_attribute(subscribe, "jid", xmpp_conn_get_bound_jid(conn));

  xmpp_stanza_add_child(pubsub, subscribe);
  xmpp_stanza_release(subscribe);
  xmpp_stanza_add_child(iq, pubsub);
  xmpp_stanza_release(pubsub);

  xmpp_send(conn, iq);
  xmpp_stanza_release(iq);
}

extern "C" int MessageHandlerFunctorInC(xmpp_conn_t * const conn __attribute__((unused)), xmpp_stanza_t * const stanza, void * const userdata) {
  CAPViewer::MessageHandlerFunctor* my_functor = (CAPViewer::MessageHandlerFunctor*) userdata;
  return my_functor->operator()(conn, stanza);
}

int CAPViewer::MessageHandlerFunctor::operator()(xmpp_conn_t * const conn __attribute__((unused)), xmpp_stanza_t * const stanza)
{
  xmpp_stanza_t *event, *items, *item, *alert;

  char* buf;
  size_t buflen;

  if(!(event = xmpp_stanza_get_child_by_name(stanza, "event"))) {
    return 1;
  }
  if(!(items = xmpp_stanza_get_child_by_name(event, "items"))) {
    return 1;
  }
  if(!(item = xmpp_stanza_get_child_by_name(items, "item"))) {
    return 1;
  }
  if(!(alert = xmpp_stanza_get_child_by_name(item, "ns4:alert"))) {
    return 1;
  }
  
  if (xmpp_stanza_to_text(alert, &buf, &buflen) < 0) {
    g_warning("Error converting incoming alert to text");
  }

  std::shared_ptr<CAPViewer::CAPReaderBuffer> reader = std::shared_ptr<CAPViewer::CAPReaderBuffer>(new CAPViewer::CAPReaderBuffer(buf, buflen));
  reader->do_parse();
  
  m_signal_ptr->operator()(reader->getCAPs());
  xmpp_free(m_ctx, buf);

  return 1;
}

extern "C" void ConnectionHandlerFunctorInC(
	    xmpp_conn_t * const conn,
	    const xmpp_conn_event_t status, 
	    const int error,
	    xmpp_stream_error_t * const stream_error,
	    void* userdata) {
  CAPViewer::ConnectionHandlerFunctor* my_functor = (CAPViewer::ConnectionHandlerFunctor*) userdata;
  my_functor->operator()(conn, status, error, stream_error);
}

void CAPViewer::ConnectionHandlerFunctor::operator()(
       xmpp_conn_t * const conn __attribute__((unused)), 
       const xmpp_conn_event_t status, 
       const int error __attribute__((unused)), 
       xmpp_stream_error_t * const stream_error __attribute__((unused))) {
  
  if (status == XMPP_CONN_CONNECT) {
    g_debug("xmpp connected"); 
    xmpp_handler_add(conn, &MessageHandlerFunctorInC, NULL, "message", NULL, m_MsgHandler );
    doSubscribe(conn, m_ctx);

  } else if (status == XMPP_CONN_DISCONNECT) {
    g_debug("xmpp disconnected");
    xmpp_stop(m_ctx);
  } else {
    g_debug("Failure in connection handler");
    xmpp_stop(m_ctx);
  }
  
}

void CAPViewer::XmppClient::run() {
  
  xmpp_connect_client(conn, NULL, 0, &ConnectionHandlerFunctorInC, &m_ConnHandler);
  xmpp_run(ctx);
}


void CAPViewer::XmppClient::die() {
  if (conn) {
    xmpp_disconnect(conn);
  }
}
