#include "json_adapter.hxx"
#include <oauth.h>
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <cstdio>

namespace Stormee {

	JsonAdapter::JsonAdapter(CURL *in)  
		: curl(in) 
	{
		if (!gnome_keyring_is_available()) {
			std::cerr << "No GNOME Keyring available! Aborting." << std::endl;
			exit(EXIT_FAILURE);
		}
		
		getTokenFromKeyring();
	}

	void JsonAdapter::getRequestToken(const std::string& in) 
	{
		char** vp = NULL;
		int cp = 0;

		cp = oauth_split_url_parameters(in.c_str(), &vp);
		std::qsort(vp, cp, sizeof(char *), oauth_cmpstringp);
			
		if( cp==2 
		    && !std::strncmp(vp[0],"oauth_token=",11)
		    && !std::strncmp(vp[1],"oauth_token_secret=",18) ) {
			
			request_token = oauth_url_unescape(&(vp[0][12]), NULL);
			request_token_secret = oauth_url_unescape(&(vp[1][19]), NULL);
		} else {
			std::cerr <<  "getRequestToken failed parsing the response: "
			          << in << std::endl;
				exit(EXIT_FAILURE);
		}

		oauth_free_array(&cp, &vp); cp = 0; vp = NULL;
	}
	
	void JsonAdapter::getVerifier() {
		std::cout << "Please navigate to " << verifier_url << "?oauth_token="
		          << request_token << std::endl << "Input the verification code: ";
		std::cin >> verifier;
	}

	void JsonAdapter::getAccessToken(const std::string& in) {
		char** vp = NULL;
		int cp = 0;
		cp = oauth_split_url_parameters(in.c_str(), &vp);
		std::qsort(vp, cp, sizeof(char *), oauth_cmpstringp);
		
		if( cp==2 
		    && !std::strncmp(vp[0],"oauth_token=",11)
		    && !std::strncmp(vp[1],"oauth_token_secret=",18) ) {
			access_token = oauth_url_unescape(&(vp[0][12]), NULL);
			access_token_secret = oauth_url_unescape(&(vp[1][19]), NULL);
		} else {
			std::cerr << "getAccessToken failed parsing the response: "
			          << in << std::endl;
		}

		oauth_free_array(&cp, &vp); cp = 0; vp = NULL;
	}

	std::string JsonAdapter::postSigned(const std::string &url,
	                                    const std::map<std::string, std::string> &params) {
		return postSignedAbstract(url, params, access_token, access_token_secret);
	}


	std::string JsonAdapter::postSignedAbstract(const std::string &url,
	                                     const std::map<std::string, std::string> &params,
	                                     const secure_string &token,
	                                     const secure_string &token_secret) {
		CURLcode res;
		char** vp = NULL;
		int cp = 0;
		size_t stream_size = 0;
		char* cbuf = NULL;
		FILE* stream = NULL;
		char* postarg;
		std::string out;

		stream = open_memstream(&cbuf, &stream_size);
		if (!stream) perror("postSigned error opening memstream");

		oauth_add_param_to_array(&cp, &vp, url.c_str());
		for(auto iter = params.begin(); iter != params.end(); iter++) {
			std::string urlenc = iter->first + "=" + iter->second;
			oauth_add_param_to_array(&cp, &vp, urlenc.c_str());
		}

		oauth_sign_array2(&cp, &vp, &postarg, OA_HMAC, NULL, 
		                  client_key.c_str(), client_secret.c_str(),
		                  token.c_str(), token_secret.c_str());

		curl_easy_reset(curl);
		
		curl_easy_setopt(curl, CURLOPT_VERBOSE, VERBOSE_CURL);
		curl_easy_setopt(curl, CURLOPT_POST, 1);
		curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
		curl_easy_setopt(curl, CURLOPT_POSTFIELDS, postarg);
		curl_easy_setopt(curl, CURLOPT_WRITEDATA, stream);
		res = curl_easy_perform(curl);
		oauth_free_array(&cp, &vp); cp = 0; vp = NULL;

		if (res != CURLE_OK) {
			std::cerr << "curl_easy_perform() failed in getAccessToken: "
			          << curl_easy_strerror(res);
		} else {
			if (std::fclose(stream) == EOF) perror("fclose stream");
		}

		out = cbuf;
		if (cbuf) free(cbuf);
		return out;
	}

	
	void JsonAdapter::storeClientIdInteractive() {
		GnomeKeyringResult res;
	
		std::cout << "Enter client id: ";
		std::cin >> client_key;
		std::cout << "Enter client secret: ";
		std::cin >> client_secret;
		std::cout << "Got key " << client_key << " and secret " << client_secret << std::endl;

	
		res = gnome_keyring_store_password_sync(&oauth_client_schema, 
		                                        GNOME_KEYRING_DEFAULT, 
		                                        "Stormee GAE Injector Client Id",
		                                        client_secret.c_str(),
		                                        "gae_appname", "Stormee Injector",
		                                        "client_key", client_key.c_str(),
		                                        NULL);

		if (res != GNOME_KEYRING_RESULT_OK) {
			std::cerr << "Error: Could not store OAuth client id to the keyring. "
			          << gnome_keyring_result_to_message(res) << std::endl;
			exit(EXIT_FAILURE);
		} else {
			std::cout << "Stored client key to the keyring." << std::endl;
			exit(EXIT_SUCCESS);
		}
	}

	void JsonAdapter::storeAccessTokenInteractive() {
		GnomeKeyringResult res;

		getRequestToken(postSignedAbstract(request_token_url,
		                                   {{"oauth_callback","oob"}},
		                                   "", ""));
		getVerifier();
		getAccessToken(postSignedAbstract(access_token_url, 
		                                  {{"oauth_verifier",verifier}}, 
		                                  request_token, request_token_secret ));

		res = gnome_keyring_store_password_sync(&oauth_token_schema,
		                                        GNOME_KEYRING_DEFAULT,
		                                        "Stormee GAE Injector OAuth 1.0 Access Token",
		                                        access_token_secret.c_str(),
		                                        "stormee_server", "stormee-gae.appspot.com",
		                                        "access_token", access_token.c_str(),
		                                        NULL);

		if (res != GNOME_KEYRING_RESULT_OK) {
			std::cerr << "Error: Could not store access token to the keyring. "
			          << gnome_keyring_result_to_message(res) << std::endl;
			exit(EXIT_FAILURE);
		} else {
			std::cout << "Stored access token to the keyring." << std::endl;
			exit(EXIT_SUCCESS);
		}
	}

	void JsonAdapter::getTokenFromKeyring() {
		GnomeKeyringResult res;
		GList* found_list = NULL;
		
		/* First, get the client id and client secret */
		
		res = gnome_keyring_find_itemsv_sync(GNOME_KEYRING_ITEM_GENERIC_SECRET, 
		                                     &found_list,
		                                     "gae_appname",
		                                     GNOME_KEYRING_ATTRIBUTE_TYPE_STRING,
		                                     "Stormee Injector",
		                                     NULL);
		
		if (res != GNOME_KEYRING_RESULT_OK) {
			if (res == GNOME_KEYRING_RESULT_NO_MATCH) {
				storeClientIdInteractive();
			} else {
				std::cerr << "Error: Could not fetch client id from the keyring. "
				          << gnome_keyring_result_to_message(res) << std::endl;
				exit(EXIT_FAILURE);
			}
		}


		if (g_list_length(found_list) > 1) {
			std::cerr << "Error: More than one client_id in keyring. Delete one"
			          << " from the GNOME Passwords and Keys app." << std::endl;
			exit(EXIT_FAILURE);
		}

		if (g_list_length(found_list) == 1) {
			GnomeKeyringFound* found = (GnomeKeyringFound*) g_list_first(found_list)->data;
			client_secret = found->secret;
			GnomeKeyringAttribute cid = gnome_keyring_attribute_list_index(found->attributes, 1);
			client_key = gnome_keyring_attribute_get_string(&cid);
		}

		if (found_list) gnome_keyring_found_list_free(found_list);

		/* Now get the access token and secret */
		res = gnome_keyring_find_itemsv_sync(GNOME_KEYRING_ITEM_GENERIC_SECRET, 
		                                     &found_list,
		                                     "stormee_server",
		                                     GNOME_KEYRING_ATTRIBUTE_TYPE_STRING,
		                                     "stormee-gae.appspot.com", NULL);
	
		if (res != GNOME_KEYRING_RESULT_OK) {
			if (res == GNOME_KEYRING_RESULT_NO_MATCH) {
				storeAccessTokenInteractive();
			} else {
				std::cerr << "Error: Could not fetch access token from the keyring. "
				          << gnome_keyring_result_to_message(res) << std::endl;
				exit(EXIT_FAILURE);
			}
		}

		if (g_list_length(found_list) > 1) {
			std::cerr << "Error: More than one access token in keyring. Delete "
			          << "one from the GNOME Passwords and Keys app." << std::endl;
			exit(EXIT_FAILURE);
		}


		if (g_list_length(found_list) == 1) {
			GnomeKeyringFound* found = (GnomeKeyringFound*) g_list_first(found_list)->data;
			access_token_secret = found->secret;
			GnomeKeyringAttribute cid = gnome_keyring_attribute_list_index(found->attributes, 0);
			access_token = gnome_keyring_attribute_get_string(&cid);
		}

		if (found_list) gnome_keyring_found_list_free(found_list);
	}
}
