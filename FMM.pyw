#!/usr/bin/env python
import sys, traceback, os.path
import pygtk
pygtk.require('2.0')
import gtk

from FMDialogData import fm_dialogdata
from FMDialog import FMDialog
from FMConfig import fm_config

# checks to see if this script if main
if __name__ == "__main__":
    try:
        if fm_config.get_configdata():
            if fm_dialogdata.get_filedata():
                FMD = FMDialog()
                FMD.main()

    except:
        # if any error occurs during the execution, capture and print out in dialog window
        # this will not display syntax errors whiich will only be seen from the command line
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        trace_text = traceback.extract_tb(exc_traceback)
        message = "FMM Script Error:\n\nTraceback:\n"
        for tt in trace_text:
            message = message + "%s (%s:%d)\n"%(os.path.split(tt[0])[1],tt[2],tt[1])
        message = message + "\nMessage:\n" + str(exc_value)
        dialog = gtk.MessageDialog(None,0,gtk.MESSAGE_ERROR,gtk.BUTTONS_OK,message)
        response = dialog.run()
        dialog.destroy()
        
