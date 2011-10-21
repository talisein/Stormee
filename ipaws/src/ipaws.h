#include "soapH.h"

void addSecurity(struct soap*);
struct ns3__responseParameterList* getRequest(struct soap* soap, struct ns2__requestParameterList* reqList);
struct _ns1__messageResponseTypeDef* getMessage(struct soap* soap, struct ns2__requestParameterList* reqList);

struct ns3__responseParameterList* doPing(struct soap* soap);
struct ns3__responseParameterList* getServerInfo(struct soap* soap);
struct ns3__responseParameterList* getCOGList(struct soap* soap);
struct ns3__responseParameterList* getValueListURN(struct soap* soap, char* urn);
struct ns3__responseParameterList* getMessageList(struct soap* soap, char* date);
char* getMessages(struct soap* soap, char* date);

void printRespList(struct ns3__responseParameterList* respList);
