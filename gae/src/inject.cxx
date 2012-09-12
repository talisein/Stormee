#include <iostream>
#include <curl/curl.h>
#include "json_adapter.hxx"
#include <fstream>

void mycb(const std::string &params) {

	std::cout << "Omg it works?" << std::endl;
	std::cout << params << std::endl;


}
static std::string read_file(char* filename) {
	std::string out;
	std::fstream file(filename, std::fstream::in);

	if ( file.is_open() ) {
		file.seekg(0, std::ios::end);
		std::streampos length = file.tellg();
		file.seekg(0, std::ios::beg);

		char *buf = new char[length];
		file.read(buf, length);
		out.assign(buf, length);
		file.close();
	} else {
		std::cerr << "Could not open file " << filename << std::endl;
	}

	return out;
}
int main(int argc, char *argv[])
{
	CURL *curl;
	
	/* In windows, this will init the winsock stuff */ 
	curl_global_init(CURL_GLOBAL_ALL);
 
	/* get a curl handle */ 
	curl = curl_easy_init();
	if(curl) {

		Stormee::JsonAdapter json(curl);

		for ( int i = 1; i < argc; i++ ) {
			std::string cap = read_file(argv[i]);
			
			mycb(json.postSigned("https://stormee-gae.appspot.com/inject", {{"cap", cap}, {"Test", "Value"}}));

		}
		curl_easy_cleanup(curl);
	}

	curl_global_cleanup();
	return EXIT_SUCCESS;
}
