# Install glade file into FOO/lib/ADM_glade/
set(CAPViewer_glade CAPViewer.glade)
set(CAPViewer_glade_location "${CMAKE_INSTALL_PREFIX}/share/CAPViewer/")

INSTALL(FILES ${CAPViewer_glade} DESTINATION ${CAPViewer_glade_location})

