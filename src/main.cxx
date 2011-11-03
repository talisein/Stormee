#include <libintl.h>
#include <clutter-gtk/clutter-gtk.h>
#include <gtkmm/main.h>
#include <glibmm/thread.h>
#include "application.hxx"

int main (int argc, char *argv[])
{
  if(!Glib::thread_supported()) Glib::thread_init();
  gtk_clutter_init(&argc, &argv);

  CAPViewer::Application app(argc, argv);
  app.run();

  return EXIT_SUCCESS;
}

