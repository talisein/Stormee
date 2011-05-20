#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2011 Andrew G. Potter
#    This file is part of the GNOME Common Alerting Protocol Viewer.
# 
#    GNOME Common Alerting Protocol Viewer is free software: you can 
#    redistribute it and/or modify it under the terms of the GNU General 
#    Public License as published by the Free Software Foundation, either 
#    version 3 of the License, or (at your option) any later version.
# 
#    GNOME Common Alerting Protocol Viewer is distributed in the hope 
#    that it will be useful, but WITHOUT ANY WARRANTY; without even the 
#    implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
#    PURPOSE.  See the    GNU General Public License for more details.
# 
#    You should have received a copy of the GNU General Public License
#    along with GNOME Common Alerting Protocol Viewer.  
#    If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import gtk
import tray
import logging

Log = logging.getLogger()
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
Log.addHandler(ch)
Log.setLevel(logging.DEBUG)

def main():
    t = tray.CAPTray()
    gtk.main()

    
if __name__ == '__main__':
    main()
    
