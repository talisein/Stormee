#ifndef STORMEE_SECRETS_HXX
#define STORMEE_SECRETS_HXX

#include <libsecret/secret.h>

namspace Stormee {

	class SecretAdapter {
	public:

	private:

		const SecretSchema client_secret_schema = {
			"org.stormee.injection.client", SECRET_SCHEMA_NONE,
			{
				{ "gae_appname", SECRET_SCHEMA_ATTRIBUTE_STRING },
				{ "client_key",  SECRET_SCHEMA_ATTRIBUTE_STRING },
				{ NULL, 0 },
			}
		};
	};

}

#endif
