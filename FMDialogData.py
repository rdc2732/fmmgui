#!/usr/bin/env python
import string, os.path, subprocess, sys
import pygtk
pygtk.require('2.0')
import gtk

from FMConfig import fm_config

# Class FMDialog
#
# Setup Instructions (depending on the installation - the root directories might be different)
# Make sure the following is in your path:
#   C:\Program Files\IBM\Rational\DOORS\9.6\bin
# Copy the Server.dxl file to the following:
#   C:\Program Files\IBM\Rational\DOORS\9.6\lib\dxl\startupfiles
# Open DOORS, no module has to be open
class FMDialogData:
    def get_filedata(self):
        # check to see if data file is present
        update_file = gtk.RESPONSE_YES
        if os.path.exists(fm_config.file):
            try:
                # if present check to see if read only
                os.rename(fm_config.file,fm_config.file+".old")
                os.rename(fm_config.file+".old",fm_config.file)
                # data file can be written, ask if they want to update it
                txt = "Update DOORS data?"
                dialog = gtk.MessageDialog(None,0,gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,txt)
                update_file = dialog.run()
                dialog.destroy()
            except:
                update_file = gtk.RESPONSE_NO

        # update the data file from DOORS 
        if update_file == gtk.RESPONSE_YES:

            fmmtmp = os.path.join(fm_config.temp_dir,"fmmtmp.dxl")
            doorsfile = string.replace(fm_config.file,"\\","/")
            fp = open(fmmtmp,"w")
            fp.write("Export(\"%s\", \"%s\", \"%s\", \"%s\")" % (fm_config.module,fm_config.baseline,fm_config.view,doorsfile))
            fp.close()

            output = subprocess.Popen("dxlipf  \"" + fmmtmp + "\"", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            doors_text1 = output.stdout.read().rstrip('\n')
            doors_text2 = output.stderr.read().rstrip('\n')
            if doors_text2[:9] == "API error":
                sys.exit("DOORS extraction error:\n" + doors_text2)

        # if date file was not created, then display error and exit
        if not os.path.exists(fm_config.file):
            txt = "DOORS Data File Error\n%s\n\nExited with the following:\n%s"%(doors_text1, doors_text2)
            dialog = gtk.MessageDialog(None,0,gtk.MESSAGE_ERROR,gtk.BUTTONS_OK,txt)
            response = dialog.run()
            dialog.destroy()
            return False

        # read in the data
        self.data = []
        fp = open(fm_config.file,"r")
        lines = fp.read().splitlines()
        fp.close()

        for line in lines:
            try:
                page, function, option, fms, dependency, type, min, max = string.split(line,",")
                self.data.append([page, function, option, fms, dependency, type, eval(min), eval(max)])
            except:
                print sys.exc_info()
                err_msg = "Unable to parse diaglog data file: " + fm_config.file
                sys.exit(err_msg)
        return True

    def get(self, x, y):
        return self.data[x][y]

    def pop(self, x):
        return self.data.pop(x)
    
    def len(self):
        return len(self.data)

# instance for global use
fm_dialogdata = FMDialogData()