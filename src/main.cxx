#include <libintl.h>
#include <glibmm/thread.h>
#include "application.hxx"
#include <clutter-gtk/clutter-gtk.h>

int main (int argc, char *argv[])
{
  if(!Glib::thread_supported()) Glib::thread_init();
  gtk_clutter_init(&argc, &argv);

  CAPViewer::Application app(argc, argv);
  app.run();

  return EXIT_SUCCESS;
}

