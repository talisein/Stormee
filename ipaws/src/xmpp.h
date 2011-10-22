#include <strophe.h>

void conn_handler(xmpp_conn_t * const conn, const xmpp_conn_event_t status, 
		  const int error, xmpp_stream_error_t * const stream_error,
		  void * const);

void getUsers(xmpp_conn_t * const conn, xmpp_ctx_t *ctx);

void sendAlert(xmpp_conn_t * const conn, xmpp_ctx_t *ctx, char* alert, char* id);
