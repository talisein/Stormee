#include <string.h>
#include "xmpp.h"

int handle_reply(xmpp_conn_t * const conn,
		 xmpp_stanza_t * const stanza,
		 void * const userdata  __attribute__((unused)))
{
    xmpp_stanza_t *query, *item;
    char *type;

    type = xmpp_stanza_get_type(stanza);
    if (strcmp(type, "error") == 0)
	fprintf(stderr, "ERROR: query failed\n");
    else {
	query = xmpp_stanza_get_child_by_name(stanza, "query");
	printf("Active Sessions:\n");
	for (item = xmpp_stanza_get_children(query); item; 
	     item = xmpp_stanza_get_next(item))
	    printf("\t %s\n", xmpp_stanza_get_attribute(item, "jid"));
	printf("END OF LIST\n");
    }

    /* disconnect */
    xmpp_disconnect(conn);

    return 0;
}

int handle_createNode(xmpp_conn_t * const conn,
		 xmpp_stanza_t * const stanza,
		 void * const userdata  __attribute__((unused)))
{
    xmpp_stanza_t *query, *item;
    char *type;

    type = xmpp_stanza_get_type(stanza);
    if (strcmp(type, "error") == 0)
	fprintf(stderr, "ERROR: createNode failed\n");
    else {
      query = xmpp_stanza_get_child_by_name(stanza, "pubsub");
      printf("Created pubsub node:\n");
      for (item = xmpp_stanza_get_children(query); item; 
	   item = xmpp_stanza_get_next(item))
	printf("\tNode: %s\n", xmpp_stanza_get_attribute(item, "node"));
      printf("END OF LIST\n");      
    }

    xmpp_disconnect(conn);
    return 0;
}


int handle_sendAlert(xmpp_conn_t * const conn,
		 xmpp_stanza_t * const stanza,
		 void * const userdata  __attribute__((unused)))
{
  xmpp_stanza_t *query, *publish, *item;
  char *type;
  
  type = xmpp_stanza_get_type(stanza);
  if (strcmp(type, "error") == 0)
    fprintf(stderr, "ERROR: createNode failed\n");
  else {
    query = xmpp_stanza_get_child_by_name(stanza, "pubsub");
    printf("Published alert:\n");
    for (publish = xmpp_stanza_get_children(query); publish; 
	 publish = xmpp_stanza_get_next(publish)) {
      printf("\tNode: %s\n", xmpp_stanza_get_attribute(publish, "node"));
      for ( item = xmpp_stanza_get_children(publish); item; item = xmpp_stanza_get_next(item)) {
	printf("\t\tItem: %s\n", xmpp_stanza_get_id(item));
      }
    }
    printf("END OF LIST\n");      
  }
  
  return 1;
}

void sendAlert(xmpp_conn_t * const conn, xmpp_ctx_t *ctx, char *alert, char *id) {
  xmpp_stanza_t *iq, *pubsub, *publish, *item, *text;
  
  iq = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(iq, "iq");
  xmpp_stanza_set_type(iq, "set");
  xmpp_stanza_set_attribute(iq, "to", "pubsub.xmpp.stormee.org");
  xmpp_stanza_set_attribute(iq, "from", xmpp_conn_get_bound_jid(conn));
  xmpp_stanza_set_id(iq, "publish1");
 
  pubsub = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(pubsub, "pubsub");
  xmpp_stanza_set_ns(pubsub, "http://jabber.org/protocol/pubsub");
  
  publish = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(publish, "publish");
  xmpp_stanza_set_attribute(publish, "node", "Test1");

  item = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(item, "item");
  xmpp_stanza_set_attribute(item, "id", id);

  text = xmpp_stanza_new(ctx);
  xmpp_stanza_set_text(text, alert);

  xmpp_stanza_add_child(item, text);
  xmpp_stanza_release(text);
  xmpp_stanza_add_child(publish, item);
  xmpp_stanza_release(item);
  xmpp_stanza_add_child(pubsub, publish);
  xmpp_stanza_release(publish);
  xmpp_stanza_add_child(iq, pubsub);
  xmpp_stanza_release(pubsub);

  xmpp_send(conn, iq);
  xmpp_stanza_release(iq);
}

void createNode(xmpp_conn_t * const conn, xmpp_ctx_t *ctx, char * const nodeName) {
  xmpp_stanza_t *iq, *pubsub, *create, *configure;

  iq = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(iq, "iq");
  xmpp_stanza_set_type(iq, "set");
  xmpp_stanza_set_attribute(iq, "to", "pubsub.xmpp.stormee.org");
  xmpp_stanza_set_attribute(iq, "from", xmpp_conn_get_bound_jid(conn));
  xmpp_stanza_set_id(iq, "create1");
	
  pubsub = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(pubsub, "pubsub");
  xmpp_stanza_set_ns(pubsub, "http://jabber.org/protocol/pubsub");

  create = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(create, "create");
  xmpp_stanza_set_attribute(create, "node", nodeName);

  configure = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(configure, "configure");

  xmpp_stanza_add_child(pubsub, create);
  xmpp_stanza_release(create);
  xmpp_stanza_add_child(pubsub, configure);
  xmpp_stanza_release(configure);
  xmpp_stanza_add_child(iq, pubsub);
  xmpp_stanza_release(pubsub);
  
  xmpp_id_handler_add(conn, handle_createNode, "create1", ctx);
 
  xmpp_send(conn, iq);

  xmpp_stanza_release(iq);
}

int handle_getNodeConfig(xmpp_conn_t * const conn,
		 xmpp_stanza_t * const stanza,
		 void * const userdata  __attribute__((unused)))
{
  //  xmpp_stanza_t *query, *item, *subitem, *field, *value;
  char *type;
  
  type = xmpp_stanza_get_type(stanza);
  if (strcmp(type, "error") == 0)
    fprintf(stderr, "ERROR: getConfig failed\n");
  else {
    /*    query = xmpp_stanza_get_child_by_name(stanza, "pubsub");
    printf("Node configuration:\n");
    for (item = xmpp_stanza_get_children(query); item; 
	 item = xmpp_stanza_get_next(item)) {
      printf("\tNode: %s\n", xmpp_stanza_get_attribute(item, "node"));
  
      for (subitem = xmpp_stanza_get_children(item); subitem; subitem=xmpp_stanza_get_next(item)) {
	for (field = xmpp_stanza_get_children(subitem); field; field=xmpp_stanza_get_next(subitem)) {
	  printf("\t\tField: %s [%s]\n", xmpp_stanza_get_attribute(field,"var"), xmpp_stanza_get_attribute(field,"label"));
	  value = xmpp_stanza_get_child_by_name(field, "value");
	  printf("\t\t\tValue: %s\n", xmpp_stanza_get_text(value));
	}
      }
    }
    printf("END OF LIST\n");      */
  }
  
  xmpp_disconnect(conn);
  return 0;
}

void getNodeConfig(xmpp_conn_t * const conn, xmpp_ctx_t *ctx, char * const nodeName) {
  xmpp_stanza_t *iq, *pubsub, *configure;

  iq = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(iq, "iq");
  xmpp_stanza_set_attribute(iq, "to", "pubsub.xmpp.stormee.org");
  xmpp_stanza_set_attribute(iq, "from", xmpp_conn_get_bound_jid(conn));
  xmpp_stanza_set_type(iq, "get");
  xmpp_stanza_set_id(iq, "config1");
  
  pubsub = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(pubsub, "pubsub");
  xmpp_stanza_set_ns(pubsub, "http://jabber.org/protocol/pubsub#owner");

  configure = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(configure, "configure");
  xmpp_stanza_set_attribute(configure, "node", nodeName);

  xmpp_stanza_add_child(pubsub, configure);
  xmpp_stanza_release(configure);
  xmpp_stanza_add_child(iq, pubsub);
  xmpp_stanza_release(pubsub);
  
  xmpp_id_handler_add(conn, handle_getNodeConfig, "config1", ctx);
 
  xmpp_send(conn, iq);

  xmpp_stanza_release(iq);
}

int handle_deleteNode(xmpp_conn_t * const conn,
		 xmpp_stanza_t * const stanza,
		 void * const userdata  __attribute__((unused)))
{
  char *type;
  
  type = xmpp_stanza_get_type(stanza);
  if (strcmp(type, "error") == 0)
    fprintf(stderr, "ERROR: getConfig failed\n");
  else {
    printf("Node deleted"); 
  }
  
  xmpp_disconnect(conn);
  return 0;
}

void deleteNode(xmpp_conn_t * const conn, xmpp_ctx_t *ctx, char * const nodeName) {
  xmpp_stanza_t *iq, *pubsub, *delete;

  iq = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(iq, "iq");
  xmpp_stanza_set_attribute(iq, "to", "pubsub.xmpp.stormee.org");
  xmpp_stanza_set_attribute(iq, "from", xmpp_conn_get_bound_jid(conn));
  xmpp_stanza_set_type(iq, "set");
  xmpp_stanza_set_id(iq, "delete1");
  
  pubsub = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(pubsub, "pubsub");
  xmpp_stanza_set_ns(pubsub, "http://jabber.org/protocol/pubsub#owner");

  delete = xmpp_stanza_new(ctx);
  xmpp_stanza_set_name(delete, "delete");
  xmpp_stanza_set_attribute(delete, "node", nodeName);

  xmpp_stanza_add_child(pubsub, delete);
  xmpp_stanza_release(delete);
  xmpp_stanza_add_child(iq, pubsub);
  xmpp_stanza_release(pubsub);
  
  xmpp_id_handler_add(conn, handle_deleteNode, "delete1", ctx);
 
  xmpp_send(conn, iq);

  xmpp_stanza_release(iq);
}

void getUsers(xmpp_conn_t * const conn, xmpp_ctx_t *ctx) {
    xmpp_stanza_t *iq, *query;

	/* create iq stanza for request */
	iq = xmpp_stanza_new(ctx);
	xmpp_stanza_set_name(iq, "iq");
	xmpp_stanza_set_type(iq, "get");
	xmpp_stanza_set_id(iq, "active2");
	xmpp_stanza_set_attribute(iq, "to", "xmpp.stormee.org");

	query = xmpp_stanza_new(ctx);
	xmpp_stanza_set_name(query, "query");
	xmpp_stanza_set_ns(query, XMPP_NS_DISCO_ITEMS);
	xmpp_stanza_set_attribute(query, "node", "online users");

	xmpp_stanza_add_child(iq, query);

	/* we can release the stanza since it belongs to iq now */
	xmpp_stanza_release(query);

	/* set up reply handler */
	xmpp_id_handler_add(conn, handle_reply, "active2", ctx);

	/* send out the stanza */
	xmpp_send(conn, iq);

	/* release the stanza */
	xmpp_stanza_release(iq);
}

/* define a handler for connection events */
void conn_handler(xmpp_conn_t * const conn __attribute__((unused)), 
		  const xmpp_conn_event_t status, 
		  const int error __attribute__((unused)), 
		  xmpp_stream_error_t * const stream_error __attribute__((unused)),
		  void * const userdata )
{
    xmpp_ctx_t *ctx = (xmpp_ctx_t *)userdata;

    if (status == XMPP_CONN_CONNECT) {
	fprintf(stderr, "DEBUG: connected\n");
	//       	deleteNode(conn, ctx, "Test1");
	
	xmpp_id_handler_add(conn, handle_sendAlert, "publish1", ctx);

    } else if (status == XMPP_CONN_DISCONNECT) {
	fprintf(stderr, "DEBUG: disconnected\n");
	xmpp_stop(ctx);
    } else {
      fprintf(stderr, "DEBUG: Failure in connection handler\n");
      xmpp_stop(ctx);
    }
}
 
