#include "ipaws.h"
#include "wsseapi.h"

extern EVP_PKEY *rsa_private_key;
extern X509 *cert;

void addSecurity(struct soap* soap) {
  struct _ns1__CAPHeaderTypeDef* CAPheader;
  int* CogId;

  soap_wsse_add_Security(soap);
  if (soap_wsse_sign_body(soap, SOAP_SMD_SIGN_RSA_SHA256, rsa_private_key, 0)) {
    printf("Error signing body\n");
    exit(EXIT_FAILURE);
  }

  if (soap_wsse_add_BinarySecurityTokenX509(soap, "X509Token", cert)) {
    printf("Error adding security token\n");
    exit(EXIT_FAILURE);
  }
  if (soap_wsse_add_KeyInfo_SecurityTokenReferenceX509(soap, "X509TokenReference")) {
    printf("Error adding security token reference\n");
    exit(EXIT_FAILURE);
  }

  CAPheader = (struct _ns1__CAPHeaderTypeDef*) soap_malloc(soap, sizeof(struct _ns1__CAPHeaderTypeDef));
  CogId = (int*) soap_malloc(soap, sizeof(int));
  *CogId = 100014;

  soap_default__ns1__CAPHeaderTypeDef(soap, CAPheader);
  CAPheader->logonUser = soap_strdup(soap, "dmopentester");
  CAPheader->logonCogId = CogId;

  soap->header->ns1__CAPHeaderTypeDef = CAPheader;
}

static struct ns2__requestParameterList* new_reqList(struct soap* soap, char* reqOp, char* paramName, char* comparOp, char* paramValue) {
  struct ns2__requestParameterList* reqList = (struct ns2__requestParameterList*) soap_malloc(soap, sizeof(struct ns2__requestParameterList));
  struct ns2__parameterListItem* listItem = (struct ns2__parameterListItem*) soap_malloc(soap, sizeof(struct ns2__parameterListItem));

  soap_default_ns2__requestParameterList(soap, reqList);
  soap_default_ns2__parameterListItem(soap, listItem);

  reqList->requestAPI = "REQUEST1";
  reqList->requestOperation = reqOp;
  reqList->parameters = listItem;
  reqList->__sizeparameters = 1;
  listItem->comparisonOp = comparOp;
  listItem->parameterValue = soap_malloc(soap, sizeof(char*));
  listItem->parameterValue[0] = paramValue;
  listItem->__sizeparameterValue = 1;
  listItem->parameterName = paramName;

  return reqList;
}

struct ns3__responseParameterList* getRequest(struct soap* soap, struct ns2__requestParameterList* reqList) {
  struct ns3__responseParameterList* respList = NULL;

  addSecurity(soap);
  respList = (struct ns3__responseParameterList*) soap_malloc(soap, sizeof(struct ns3__responseParameterList));

  if (soap_call___ns1__getRequest(soap, "https://tdl.integration.fema.gov/IPAWS_CAPService/IPAWS", NULL, reqList, respList)) {
    soap_print_fault(soap, stderr);
    return NULL;
  }

  return respList;
}

struct _ns1__messageResponseTypeDef* getMessage(struct soap* soap, struct ns2__requestParameterList* reqList) {
  struct _ns1__messageResponseTypeDef* respList = NULL;

  addSecurity(soap);
  respList = (struct _ns1__messageResponseTypeDef*) soap_malloc(soap, sizeof(struct _ns1__messageResponseTypeDef));

  if (soap_call___ns1__getMessage(soap, "https://tdl.integration.fema.gov/IPAWS_CAPService/IPAWS", NULL, reqList, respList)) {
    soap_print_fault(soap, stderr);
    return NULL;
  }

  return respList;
}

void printRespList(struct ns3__responseParameterList* respList) {
  if (respList != NULL) {
    printf("ResponseOperation: %s\n", respList->ResponseOperation);
    printf("ResponseType: %s\n", respList->ResponseType);
    
    for (int i = 0; i < respList->__sizeparameterListItem; i++) {
      printf("parameterName: %s\n", respList->parameterListItem[i].parameterName);
      printf("parameterValue: %s\n", respList->parameterListItem[i].parameterValue);
      for (int j = 0; j < respList->parameterListItem[i].__sizesubParaListItem; j++) {
	printf("%s:\t%s\n", respList->parameterListItem[i].subParaListItem[j].subParameterName, respList->parameterListItem[i].subParaListItem[j].subParameterValue);
      }
    }
  }
}

struct ns3__responseParameterList* doPing(struct soap* soap) {
  return getRequest(soap, new_reqList(soap, "getACK", NULL, NULL, NULL));
}

struct ns3__responseParameterList* getServerInfo(struct soap* soap) {
  return getRequest(soap, new_reqList(soap, "getServerInfo", NULL, NULL, NULL));
}

struct ns3__responseParameterList* getCOGList(struct soap* soap) {
  return getRequest(soap, new_reqList(soap, "getCOG", NULL, NULL, "ALL"));
}

struct ns3__responseParameterList* getValueListURN(struct soap* soap, char* urn) {
  return getRequest(soap, new_reqList(soap, "getValueListUrn", NULL, NULL, urn));
}

struct ns3__responseParameterList* getMessageList(struct soap* soap, char* date) {
  return getRequest(soap, new_reqList(soap, "getMessageListAll", "sent", "greaterthan", date));
}

struct _ns1__messageResponseTypeDef* getMessages(struct soap* soap, char* date) {
  return getMessage(soap, new_reqList(soap, "getMessageAll", "sent", "greaterthan", date));
}
