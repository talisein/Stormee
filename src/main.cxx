#include <libintl.h>
#include <gtkmm/main.h>
#include "config.h"
#include "util.hxx"
#include "main_window.hxx"


int main (int argc, char *argv[])
{
  Gtk::Main kit(argc, argv);
  if(!Glib::thread_supported()) Glib::thread_init();

  auto refBuilder = CAPViewer::Util::getGtkBuilder();
  CAPViewer::Window *window;
  refBuilder->get_widget_derived("mainWindow", window);

  kit.run(*window);
  delete window;
  return EXIT_SUCCESS;
}

