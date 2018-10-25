#!/usr/bin/env python
import os

import pygtk
pygtk.require('2.0')
import gtk

from FMDialogData import fm_dialogdata
from FMData import fm_data
from FMFunction import FMFunction
from FMConfig import fm_config

# Class FeatureModel
# Main feature model selection dialog window
# Consists of a table of functions on multiple notebook pages
class FMDialog:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_border_width(5)
        self.window.set_title("PCC Feature Model Selection")        
        self.window.connect("destroy", self.destroy)
        self.window.set_size_request(800, 600)
        self.flist = []

        # define the notebook and max size
        # setup to show as full the first time
        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        table_list = []
        table_name = None

        while fm_dialogdata.len() > 0:
            # create/save the function frame
            func_frame = FMFunction()
            self.flist.append(func_frame)
            func_frame.Frame.show()

            # check to see if table is full or page change            
            if not table_name == func_frame.get_label():
                if len(table_list) > 0:
                    table_window = self.create_table(table_list)
                    page_name = gtk.Label()
                    page_name.set_label(table_name)
                    notebook.append_page(table_window, page_name)
                    table_list = []

            # if not hidden, add the function to the list
            if func_frame.is_hidden():
                func_frame.Frame.hide()
            else:
                table_list.append(func_frame)
            table_name = func_frame.get_label()

        if len(table_list) > 0:
            table_window = self.create_table(table_list)
            page_name = gtk.Label()
            page_name.set_label(table_name)
            notebook.append_page(table_window, page_name)

        # add the notebook and control buttons to the dialog window
        vbox = gtk.VBox(homogeneous=False, spacing=2)
        vbox.pack_start(notebook, expand=True, fill=True, padding=0)
        notebook.show()

        separator = gtk.HSeparator()
        vbox.pack_start(separator, False, True, 0)
        separator.show() 

        hbox = gtk.HBox(homogeneous=False, spacing=2)
        vbox.pack_start(hbox, expand=False, fill=False, padding=3)
        hbox.show()

        button = gtk.Button("   Load   ")
        hbox.pack_start(button, expand=True, fill=False, padding=10)
        button.show()
        button.connect('clicked', self.load)

        button = gtk.Button("   Save   ")
        hbox.pack_start(button, expand=True, fill=False, padding=10)
        button.show()
        button.connect('clicked', self.save)

        button = gtk.Button("   Exit   ")
        hbox.pack_start(button, expand=True, fill=False, padding=10)
        button.show()
        button.connect('clicked', self.exit)

        self.window.add(vbox)
        vbox.show()
        self.window.show()
        self.run_enable = True

    # creates the table object for display within the notebook page.
    def create_table(self, t_list):
        fm_table = gtk.Table()
        fm_table.set_row_spacings(5)
        fm_table.set_col_spacings(5)
        fm_table.show()

        # determine the maximum columns based on the number of objects
        if len(t_list) < 4:
            max_col = 1
        elif len(t_list) < 9:
            max_col = 2
        elif len(t_list) < 19:
            max_col = 3
        else:
            max_col = 4

        col = 0
        row = 0
        max_list = [0 for x in range(max_col)]
        min_row = [0 for x in range(max_col)]
        index = 0
        while index < len(t_list):
            if max_list[col] == min(max_list) and min_row[col] == 0:
                r_size = t_list[index].count() + 1
                fm_table.attach(t_list[index].Frame, col, col+1, row, row+r_size)
                max_list[col] = max_list[col] + r_size
                min_row[col] = min_row[col] + r_size - 1
                index += 1
            elif min_row[col] > 0:
                min_row[col] = min_row[col] - 1

            col += 1
            if col >= max_col:
                col = 0
                row += 1

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(2)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.show()
        xbox = gtk.VBox(homogeneous=False, spacing=2)
        xbox.pack_start(fm_table, expand=False, fill=False, padding=0)
        xbox.show()                
        scrolled_window.add_with_viewport(xbox)
        return scrolled_window

    def destroy(self, widget, data=None):
        self.run_enable = False
        
    def main(self):
        while self.run_enable:
            gtk.main_iteration()
            fm_data.update()
            for f in self.flist:
                f.update()

    def exit(self, widget, data=None):
        self.destroy(widget)

    def load(self, widget, data=None):
        file_select = gtk.FileSelection()
        path, file = os.path.split(fm_config.file)
        file_select.set_filename(path+"\\")
        response = file_select.run()
        filename = file_select.get_filename()
        file_select.destroy()
        
        if response == gtk.RESPONSE_OK:
            # need error checking for unknown file
            fp = open(filename,"r")
            lines = fp.read().splitlines()
            fp.close()
            value = None
            for line in lines:
                if line == "FM SELECTION (SET)":
                    value = True
                elif line == "FM SELECTION (NOT SET)":
                    value = False
                elif line == "FM SELECTION (INCOMPLETE)":
                    value = None
                elif line == "" or line[0] == "#":
                    continue
                else:
                    fm_data.set(line, value)

    def save(self, widget, data=None):
        # check for complete data
        incomplete = fm_data.display([None])
        invalid = ""
        for f in self.flist:
            invalid = invalid + f.display(False)

        # check to see if all selections have been made
        response = gtk.RESPONSE_YES
        if not incomplete == "" or not invalid == "":
            txt = "The following feature selections have not been made:\n" + incomplete + invalid +  "\n\nDo you still want to save the incomplete data?"
            dialog = gtk.MessageDialog(self.window,0,gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,txt)
            response = dialog.run()
            dialog.destroy()

        # if everything is filled in or they want to save incomplete data
        if response == gtk.RESPONSE_YES:
            file_select = gtk.FileSelection()
            path, file = os.path.split(fm_config.file)
            file_select.set_filename(path+"\\")
            response = file_select.run()
            filename = file_select.get_filename()
            file_select.destroy()
            if response == gtk.RESPONSE_OK and not filename == None:
                fp = open(filename,"w")
                fp.write("FM SELECTION (SET)\n")
                fp.write(fm_data.display([True]))
                fp.write("\nFM SELECTION (NOT SET)\n")
                fp.write(fm_data.display([False,"Disabled"]))
                incomplete = fm_data.display([None])
                if not incomplete == "":
                    fp.write("\nFM SELECTION (INCOMPLETE)\n")
                    fp.write(incomplete)
                fp.write("\n")
                fp.close()
        
