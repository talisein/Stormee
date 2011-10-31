#include <libintl.h>
#include <gtkmm/main.h>
#include <glibmm/thread.h>
#include "application.hxx"

int main (int argc, char *argv[])
{
  if(!Glib::thread_supported()) Glib::thread_init();

  CAPViewer::Application app(argc, argv);
  app.run();

  return EXIT_SUCCESS;
}

