#!/usr/bin/env python
import os, string
import pygtk
pygtk.require('2.0')
import gtk

from FMDialogData import fm_dialogdata
from FMData import fm_data    
from FMConfig import fm_config

# Class FMOption
# Creates a yes/no option control box where
# True = Yes button active
# False = No button active
# None = Hidden button active
# "Disabled" = Hidden button active; Frame containing Yes, No, Hidden buttons is disabled
class FMOption:
    def __init__(self, box, text, fms, dependency):
        # use box around Yes/No/Label to manage enable/disable
        enable = gtk.HBox(homogeneous=False, spacing=0)

        # hidden button (used to clear both the yes/no buttons)
        hidden = gtk.RadioButton(None, "")
        hidden.connect('toggled', fm_data.callback, "Option-Hidden", fms)
        enable.pack_start(hidden, expand=False, fill=False, padding=0)
        # do not show hidden

        # Yes/No buttons
        yes_no_box = gtk.HBox(homogeneous=False, spacing=0)
        yes = gtk.RadioButton(hidden, "Yes")
        yes.connect('toggled', fm_data.callback, "Option-Yes", fms)
        yes_no_box.pack_start(yes, expand=False, fill=False, padding=0)
        yes.show()
        no = gtk.RadioButton(yes, "No  :")
        no.connect('toggled', fm_data.callback, "Option-No", fms)
        yes_no_box.pack_start(no, expand=False, fill=False, padding=0)
        no.show()
        enable.pack_start(yes_no_box, expand=False, fill=False, padding=0)
        yes_no_box.show()

        # label
        label = gtk.Label(text)
        enable.pack_start(label, expand=False, fill=False, padding=3)
        label.show()

        # add enable_box to main box
        box.pack_start(enable, expand=False, fill=False, padding=0)
        enable.show()

        # if debug enabled, add debug data to dialog
        debug = None
        if fm_config.debug & 2:
            debug = gtk.Label()
            box.pack_start(debug, expand=False, fill=False, padding=0)
            debug.show()

        fm_data.add("option", fms, dependency, yes, no, hidden, enable, debug)
        self.yes = yes

    # not used in FMOption; used by FMSelect to check for single enabled button
    def get_sensitive(self):
        return False

    # returns if the selection is true, used to check selection count between min/max
    def get_active(self):
        return self.yes.get_active()

    def hide_test(self,text):
        return False
    
    def fms_test(self,fms):
        return False

# Class FMSelect
# Creates a radio button control where
# True = Object button active
# False = Object and Hidden not active
# None = Hidden button active
# "Disabled" = Frame containing Object button is disabled; Object is not active
class FMSelect:
    def __init__(self, box, hidden, text, fms, dependency):

        # Selection button
        enable = gtk.VBox(homogeneous=False, spacing=0)
        object = gtk.RadioButton(hidden, text)
        object.connect('toggled', fm_data.callback, "Select-Enable", fms)
        enable.pack_start(object, expand=False, fill=False, padding=0)
        object.show()
        
        # add enable_box to main box
        box.pack_start(enable, expand=False, fill=False, padding=0)
        enable.show()
        enable.set_sensitive(False)

        debug = None
        if fm_config.debug & 2:
            debug = gtk.Label()
            box.pack_start(debug, expand=False, fill=False, padding=0)
            debug.show()
        
        fm_data.add("select", fms, dependency, object, None, hidden, enable, debug)
        self.object = object
        self.enable = enable
        self.text = text
        self.fms = fms

    # used to count number of enabled selection buttons
    def get_sensitive(self):
        return self.enable.get_sensitive()

    # used to set single enabled button active
    def set_active(self):
        self.object.set_active(1)

    # not used in FMSelect; used by FMOption to check selection count between min/max
    def get_active(self):
        return 0

    def hide_test(self,text):
        if text == None or text == self.text:
            return self.text
        return False

    def fms_test(self,fms):
        if fms == None or fms == self.fms:
            return self.fms
        return False
    
# FMFunction class
# Used to manage each function group.
class FMFunction:
    def __init__(self):
        self.Frame = gtk.Frame()

        self.olist = []
        box = gtk.VBox(homogeneous=False, spacing=2)
        self.minmax = None
        hidden = None

        func = fm_dialogdata.get(0,1)
        while fm_dialogdata.len() > 0 and func == fm_dialogdata.get(0,1):
            page, function, option, fms, dependency, type, min, max = fm_dialogdata.pop(0)

            dependency_x = dependency + ";-OR-;"
            for dependency in string.split(dependency_x,";-OR-;"):
                if dependency == "":
                    break
            
                # Option are a yes/no set of radio buttons where you have to select yes/no
                if min < max: # type == "Option"
                    object = FMOption(box, option, fms, dependency)
                    if self.minmax == None:
                        self.minmax = [min,max,False]
                    if not self.minmax == [min,max,False]:
                        sys.exit("Function '%s' min/max values are different"%fms)

                # Selections are a radio button (where you can choose only one item)
                elif min == max and min == 1:
                    # create the hidden button if not present
                    if hidden == None:
                        hidden = gtk.RadioButton(None, "")
                        hidden.connect('toggled', fm_data.callback, "Select-Hidden", fms)
                        box.pack_start(hidden, expand=False, fill=False, padding=0)
                    object = FMSelect(box, hidden, option, fms, dependency)
                else:
                    message = "Warning - No Function Type Found: %s"%str([page, function, min, max])
                    dialog = gtk.MessageDialog(None,0,gtk.MESSAGE_ERROR,gtk.BUTTONS_OK,message)
                    response = dialog.run()
                    dialog.destroy()
                    object = None

                self.olist.append(object)

        self.Frame.add(box)
        box.show()
        self.Frame.set_label(function)
        self.page = page

        if fm_config.debug & 2:
            debug_label = gtk.Label()
            box.pack_start(debug_label, expand=False, fill=False, padding=0)
            debug_label.show()
            self.debug_label = debug_label

    def get_label(self):
        return self.page        

    # used to manage the checking of completed functions and selecting of single buttons
    def update(self):
        first = None
        scount = 0
        ocount = 0
        for o in self.olist:
            if o.get_sensitive():
                scount = scount + 1
                if first == None:
                    first = o
            if o.get_active() == 1:
                ocount = ocount + 1

        # force any single enabled radio button (select only) to be set
        if scount == 1:
            first.set_active()

        # check the min / max count of the options
        if fm_config.debug & 2:
            self.debug_label.set_text("")
        try:
            min, max, status = self.minmax
            if status == True and (ocount < min or ocount > max):
                message = "Warning in Function: %s \nMin/Max Limits of [%d,%d] have been exceeded.\nLast change not accepted"%(self.Frame.get_label(),min,max)
                dialog = gtk.MessageDialog(None,0,gtk.MESSAGE_ERROR,gtk.BUTTONS_OK,message)
                response = dialog.run()
                dialog.destroy()
                fm_data.undo_last()
            self.minmax = [min,max,(ocount >= min and ocount <= max)]
            if fm_config.debug & 2 and (ocount < min or ocount > max):
                self.debug_label.set_text("Min/Max Invalid")
        except:
            pass

    # determines if the function should be hidden or not (e.g. single options are hidden)
    def is_hidden(self):
        # force showing all if debug selection made
        if fm_config.debug & 1:
            return False
        name = None
        for o in self.olist:            
            name = o.hide_test(name)
            if name == False:
                return False
        return True

    # counts the number of visible objects
    def count(self):
        cnt = 0
        fms = None
        for o in self.olist:
            nfms = o.fms_test(fms)
            if not nfms == fms or nfms == False:
                cnt = cnt + 1
            fms = nfms
        return cnt
       
    # display FMS values not within defined range
    def display(self, type):
        try:
            min, max, status = self.minmax
            if status == type:
                return "\nFunction %s selection count not within range %d to %d"%(gtk.Frame.get_label(self),min, max)
        except:
            pass
        return ""