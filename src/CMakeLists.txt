# configure a header file to pass some of the CMake settings
# to the source code
configure_file (
  "config.h.in"
  "config.h"
  )

# add the binary tree to the search path for include files
# so that we will find TutorialConfig.h

# add the executable
link_directories(
    ${GTKMM3_LIBRARY_DIRS} ${XML++_LIBRARY_DIRS} ${GTHREAD_LIBRARY_DIRS} ${STROPHE_LIBRARY_DIRS} ${CHAMPLAINGTK_LIBRARY_DIRS})

include_directories(
    ${GTKMM3_INCLUDE_DIRS}  ${XML++_INCLUDE_DIRS} ${GTHREAD_LIBRARY_DIRS} ${STROPHE_INCLUDE_DIRS} ${CHAMPLAINGTK_INCLUDE_DIRS})

add_executable(stormee main.cxx util.cxx main_window.cxx log.cxx cap.cxx datetime.cxx capreader.cxx xmpp.cxx notify.cxx application.cxx)

target_link_libraries(stormee 
    ${GTKMM3_LIBRARIES} ${XML++_LIBRARIES} ${STROPHE_LIBRARIES} ${CHAMPLAINGTK_LIBRARIES})
