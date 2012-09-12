# this is example-file: configure.ac
AC_PREREQ([2.68])
AC_INIT([stormee-inject], [0.1], [agpotter@gmail.com])
AC_CONFIG_SRCDIR([src/])
AC_CONFIG_MACRO_DIR([m4/])

AM_INIT_AUTOMAKE
#AC_CONFIG_HEADERS([config.h])


# Checks for programs.
AC_PROG_CXX
AC_LANG([C++])

AX_CXX_COMPILE_STDCXX_11([noext])

# Checks for libraries.
PKG_CHECK_MODULES([GLIB], [glib-2.0 >= 2.32.0])
PKG_CHECK_MODULES([KEYRING], [gnome-keyring-1 >= 3.0])
PKG_CHECK_MODULES([CURL], [libcurl >= 7.24.0])
PKG_CHECK_MODULES([OAUTH], [oauth >= 0.9.6])
PKG_CHECK_MODULES([GCR], [gcr-3 >= 3.4.0])


AC_SUBST([GLIB_LIBS])
AC_SUBST([GLIB_CFLAGS])
AC_SUBST([KEYRING_LIBS])
AC_SUBST([KEYRING_CFLAGS])
AC_SUBST([CURL_LIBS])
AC_SUBST([CURL_CFLAGS])
AC_SUBST([OAUTH_LIBS])
AC_SUBST([OAUTH_CFLAGS])
AC_SUBST([GCR_LIBS])
AC_SUBST([GCR_CFLAGS])

# Checks for header files.
AC_CHECK_HEADERS([stdlib.h string.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_TYPE_SIZE_T

# Checks for library functions.
AC_FUNC_MALLOC

AC_CONFIG_FILES([Makefile
                 src/Makefile])
AC_OUTPUT


