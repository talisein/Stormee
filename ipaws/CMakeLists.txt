cmake_minimum_required (VERSION 2.6)
project (StormeeBridge C)

# The version number
set (StormeeBridge_VERSION_MAJOR 0)
set (StormeeBridge_VERSION_MINOR 1)

# std C libraries
#find_package(stdlibs REQUIRED)

# libpthread with pthread.h
#find_package(pthread REQUIRED)

find_package(Git)
if(Git_FOUND)

endif(Git_FOUND)

#find_package( Gettext REQUIRED )
#find_package( Boost REQUIRED COMPONENTS date_time )

find_package(PkgConfig)
#find_package( WebkitGTK REQUIRED )

#pkg_check_modules(WEBKITGTK webkitgtk-3.0 REQUIRED)
#pkg_check_modules(GTKMM3 gtkmm-3.0 REQUIRED)
#pkg_check_modules(XML++ libxml++-2.6 REQUIRED)
#pkg_check_modules(GTHREAD gthread-2.0 REQUIRED)
pkg_check_modules(GSOAP gsoapssl REQUIRED)
pkg_check_modules(STROPHE libstrophe REQUIRED)
pkg_check_modules(GLIB glib-2.0 REQUIRED)

set(CMAKE_BUILD_TYPE debug)
set(CMAKE_C_FLAGS_DEBUG "-ggdb -Os")

add_definitions(-D_POSIX_C_SOURCE=200809L -DWITH_OPENSSL -DWITH_DOM -Wall -Wextra -pedantic -std=c99)

add_subdirectory (src)
