#include <gtkmm/main.h>
#include <gtkmm/window.h>
#include <glibmm/dispatcher.h>
#include "config.h"
#include "util.hxx"
#include "main_window.hxx"
#include "log.hxx"
#include <iostream>
#include <libintl.h>
#include "cap.hxx"
#include "capreader.hxx"
#include <libxml++/libxml++.h>
#include <gtkmm/imagemenuitem.h>
using CAPViewer::Log;

int main (int argc, char *argv[])
{
  Gtk::Main kit(argc, argv);
  if(!Glib::thread_supported()) Glib::thread_init();

  auto refBuilder = CAPViewer::Util::getGtkBuilder();
  CAPViewer::Window *window;
  refBuilder->get_widget_derived("mainWindow", window);

  Glib::Dispatcher gui_dispatcher();

  kit.run(*window);
  delete window;


  std::cout << "EXIS_SUCCESS :)" << std::endl;
  return EXIT_SUCCESS;
}

