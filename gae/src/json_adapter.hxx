#ifndef JSON_ADAPTER_CXX
#define JSON_ADAPTER_CXX

#include <curl/curl.h>
#include <gnome-keyring-1/gnome-keyring.h>
#include <string>
#include <map>
#include "secure_string.hxx"

#include <iostream>

namespace Stormee {
	
	class JsonAdapter {
	public:
		JsonAdapter(CURL *curl);
		std::string postSigned(const std::string &url, 
		                       const std::map<std::string, std::string> &params);


	private:
		void getRequestToken(const std::string&);
		void getVerifier();
		void getAccessToken(const std::string&);

		void getTokenFromKeyring();
		void storeClientIdInteractive();
		void storeAccessTokenInteractive();

		std::string postSignedAbstract(const std::string &url, 
		                               const std::map<std::string, std::string> &params,
		                               const secure_string &token,
		                               const secure_string &token_secret);

		CURL *curl;
		const long VERBOSE_CURL = 0;
		const std::string base_url = "https://stormee-gae.appspot.com/";
		const std::string request_token_url = base_url + "_ah/OAuthGetRequestToken";
		const std::string verifier_url = base_url + "_ah/OAuthAuthorizeToken";
		const std::string access_token_url = base_url + "_ah/OAuthGetAccessToken";

		secure_string client_key, client_secret;
		secure_string access_token, access_token_secret;
		secure_string request_token, request_token_secret;
		std::string verifier;

		const GnomeKeyringPasswordSchema oauth_client_schema = {
			GNOME_KEYRING_ITEM_GENERIC_SECRET,
			{
				{ "gae_appname", GNOME_KEYRING_ATTRIBUTE_TYPE_STRING },
				{ "client_key", GNOME_KEYRING_ATTRIBUTE_TYPE_STRING },
				{ NULL, GNOME_KEYRING_ATTRIBUTE_TYPE_STRING }
			}
		};

		const GnomeKeyringPasswordSchema oauth_token_schema = {
			GNOME_KEYRING_ITEM_GENERIC_SECRET,
			{
				{ "stormee_server", GNOME_KEYRING_ATTRIBUTE_TYPE_STRING },
				{ "access_token", GNOME_KEYRING_ATTRIBUTE_TYPE_STRING },
				{ NULL, GNOME_KEYRING_ATTRIBUTE_TYPE_STRING }
			}
		};

	};

}

#endif
