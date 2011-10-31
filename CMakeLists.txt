cmake_minimum_required (VERSION 2.6)
project (CAPViewer CXX C)

# The version number
set (CAPViewer_VERSION_MAJOR 0)
set (CAPViewer_VERSION_MINOR 1)

# check libs and packages (headers + lib)
set(CAPViewer_glade_location "\"${CMAKE_INSTALL_PREFIX}/share/CAPViewer/CAPViewer.glade\"")

# std C libraries
#find_package(stdlibs REQUIRED)

# libpthread with pthread.h
#find_package(pthread REQUIRED)

find_package(Git)
if(Git_FOUND)

endif(Git_FOUND)

find_package( Gettext REQUIRED )
find_package( Boost REQUIRED COMPONENTS date_time )

find_package(PkgConfig)
#find_package( WebkitGTK REQUIRED )

pkg_check_modules(WEBKITGTK webkitgtk-3.0 REQUIRED)
pkg_check_modules(GTKMM3 gtkmm-3.0 REQUIRED)
pkg_check_modules(XML++ libxml++-2.6 REQUIRED)
pkg_check_modules(GTHREAD gthread-2.0 REQUIRED)
pkg_check_modules(STROPHE libstrophe REQUIRED)
pkg_check_modules(LIBNOTIFY libnotifymm-1.0 REQUIRED)

set(CMAKE_BUILD_TYPE debug)
set(CMAKE_CXX_FLAGS_DEBUG "-ggdb3 -O2" )

add_definitions(-Wall -Wextra -pedantic -std=c++0x -D_GNU_SOURCE)

add_subdirectory (glade)
add_subdirectory (src)
