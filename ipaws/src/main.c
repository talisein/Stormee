#include <stdlib.h>
#include <strophe.h>
#include <openssl/engine.h>
#include <openssl/pem.h>
#include <openssl/conf.h>
#include "ipaws.h"
#include "CAPSoapHttp.nsmap"
#include "plugin.h"
#include "wsseapi.h"

EVP_PKEY *rsa_private_key = NULL;
X509 *cert = NULL;

struct soap* init(void);
void cleanup(struct soap*);

struct soap* init(void) {
  FILE *fd = NULL;
  struct soap* soap = NULL;
  char passwd[10] = {'\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0'};

  soap = soap_new1(SOAP_XML_CANONICAL | SOAP_XML_INDENT);
  soap_ssl_init();
  soap_register_plugin(soap, plugin); // register plugin
  soap_register_plugin(soap, soap_wsse);

  fd = fopen("secrets", "r");
  if (fd) {
    fgets(passwd, 10, fd);
    fclose(fd);
    if (passwd == NULL) {
      perror("Unable to read password for X509 certificate.");
      return NULL;
    }
  } else {
    perror("Unable to open secrets file");
    return NULL;
  }

  fd = fopen("DMOPEN_100014_PRIVATE.pem", "r");
  if (fd) {
    rsa_private_key = PEM_read_PrivateKey(fd, NULL, NULL, passwd);
    fclose(fd);
    if (rsa_private_key == NULL) {
      perror("Error reading private key");
      return NULL;
    }
  } else {
    perror("Unable to open Private X509 .pem file");
    return NULL;
  }

  fd = fopen("DMOPEN_100014.pem", "r");
  if (fd) {
    cert = PEM_read_X509(fd, NULL, NULL, NULL);
    fclose(fd);
    if (cert == NULL) {
      perror("Error reading certificate file");
      return NULL;
    }
  } else {
    perror("Unable to open publix X509 .pem file");
    return NULL;
  }

  return soap;
}

void cleanup(struct soap* soap) {

  if (rsa_private_key) {
    EVP_PKEY_free(rsa_private_key);
  }

  if (cert) {
    X509_free(cert);
  }

  if (soap) {
    soap_end(soap);
    soap_done(soap);
    soap_free(soap);
  }
  
  ERR_remove_state(0);
  ENGINE_cleanup();
  CONF_modules_unload(1);

  ERR_free_strings();
  EVP_cleanup();
  CRYPTO_cleanup_all_ex_data();
}

int main(void) {
  struct soap* soap = init();
  
  if (soap) {
    doPing(soap);
    //    printRespList(getServerInfo(soap));
    //printRespList(getCOGList(soap));
    //printRespList(getValueListURN(soap, "https://www.dmopen.fema.gov/RequestOperationList"));
    //printRespList(getMessageList(soap, "2011-10-18T15:21:00-00:00"));
    //getMessages(soap, "2011-10-18T15:21:00-00:00");
  } else {
    perror("Error in initialization");
    cleanup(soap);
    return EXIT_FAILURE;
  }

  cleanup(soap);
  return EXIT_SUCCESS;
}
