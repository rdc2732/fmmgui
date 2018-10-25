#!/usr/bin/env python
import string
import sys
import pygtk
pygtk.require('2.0')
import gtk
       
# Class FMData
# Holds data associated with all of the selections
class FMData:
    def __init__(self):
        self.list = []
        self.data = {}
        
    # adds the given data
    def add(self, type, fms, dependency, true_widget, false_widget, hidden_widget, enable_widget, debug_label=None):
        # save ordered list of feature model selections
        if not self.data.has_key(fms):
            self.list.append(fms)

        # convert the dependancy so it can be evaluated
        eval_dependency = "[[True"
        if not dependency == "n/a":
            for d in string.split(dependency,";"):
                if eval_dependency == "[True":
                    eval_dependency = "[fm_data.get(\"%s\")"%(d)
                else:
                    eval_dependency = eval_dependency + ",fm_data.get(\"%s\")"%(d)
        eval_dependency = eval_dependency + "]]"

        # save data
        if self.data.has_key(fms):
            enable_widget.hide()
            prev_eval_dependency, true_widget, false_widget, hidden_widget, enable_widget, debug_label = self.data[fms]
            eval_dependency = prev_eval_dependency[:-1] + "," + eval_dependency[1:]
        self.data[fms] = [eval_dependency, true_widget, false_widget, hidden_widget, enable_widget, debug_label]

    # uses the internal stored widgets to set the current value
    def set(self, fms, value):
        if self.data.has_key(fms):
            dependency, true_widget, false_widget, hidden_widget, enable_widget, debug_label = self.data[fms]
            if value == True:
                true_widget.set_active(1)
            elif value == False and not false_widget == None:
                false_widget.set_active(1)
            elif value == None:
                hidden_widget.set_active(1)
        else:
            message = "WARNING:\nSelection 'SET' variable '%s' not found!!\n"%fms
            dialog = gtk.MessageDialog(None,0,gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,message)
            response = dialog.run()
            dialog.destroy()

    # uses the internal stored widgets to determine the current value
    def get(self, fms):
        if self.data.has_key(fms):
            dependency, true_widget, false_widget, hidden_widget, enable_widget, debug_label = self.data[fms]
            if not enable_widget.get_sensitive():
                return "Disabled"
            if true_widget.get_active():
                return True
            if hidden_widget.get_active():
                return None
        else:
            message = "WARNING:\nSelection 'GET' variable '%s' not found!!\n"%fms
            dialog = gtk.MessageDialog(None,0,gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,message)
            response = dialog.run()
            dialog.destroy()
        return False
            
    # returns text string which include selections that match the give type (True, False, None, "Disabled")
    # type is an arrary in which the output will include either of the items in the array
    def display(self, type):
        text = ""
        for fms in self.list:
            dependency, true_widget, false_widget, hidden_widget, enable_widget, debug_label = self.data[fms]
            for t in type:
                if self.get(fms) == t:
                    text = text + fms + "\n"
                    break
        return text

    # updates the enabling/disabling of a sections
    # when disabled, forces the object to be not selected (e.g. None)
    def update(self):
        for fms in self.list:
            dependency, true_widget, false_widget, hidden_widget, enable_widget, debug_label = self.data[fms]

            # sensitivity is used to conrol enable/disable
            # determine value of dependency by going over the AND and OR conditions
            test_dep = eval(dependency)
            enable_status = False
            for tor in test_dep:
                val = True
                for tand in tor:
                    val = val and tand==True
                enable_status = enable_status or val==True
            enable_widget.set_sensitive(enable_status)

            # if disabled - clear the selection
            status = self.get(fms)
            if status == "Disabled":
                if true_widget.get_active():
                    hidden_widget.set_active(1)
                if (not false_widget == None) and false_widget.get_active():
                    hidden_widget.set_active(1)

            # add the current status to dialog if debug is enabled
            if not debug_label == None:
                debug_label.set_text(str([fms,status,dependency]))

    # called when any of the buttons are changed
    def callback(self, widget, type, fms):
        #print "%s-%s was changed: %i" % (type, fms, widget.get_active())
        self.last_change = fms

    # called to remove the last change by setting the selection to none
    def undo_last(self):
        self.set(self.last_change,None)

fm_data = FMData()
#instance for global use
