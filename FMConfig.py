#!/usr/bin/env python
import os.path

import pygtk
pygtk.require('2.0')
import gtk

# Class FMConfig
# Manages the configuration and options of the selection
class FMConfig:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_border_width(5)
        self.window.set_title("PCC Feature Model Selection")        
        self.window.connect("destroy", self.exit)

        vbox = gtk.VBox(homogeneous=False, spacing=2)

        #Feature Model Data file
        hbox = gtk.HBox(homogeneous=False, spacing=2)
        vbox.pack_start(hbox, expand=False, fill=False, padding=3)
        hbox.show()

        label = gtk.Label("Feature Model Data:")
        hbox.pack_start(label, expand=False, fill=False, padding=3)
        label.show()

        self.file = gtk.Entry(max=0)
        hbox.pack_start(self.file, expand=True, fill=True, padding=10)
        self.file.show()

        button = gtk.Button("Browse")
        hbox.pack_start(button, expand=False, fill=False, padding=10)
        button.show()
        button.connect('clicked', self.browse)

        #DOORS Data - Row 1
        hbox = gtk.HBox(homogeneous=False, spacing=2)
        vbox.pack_start(hbox, expand=False, fill=False, padding=3)
        hbox.show()

        label = gtk.Label("DOORS Module:")
        hbox.pack_start(label, expand=False, fill=False, padding=3)
        label.show()

        self.module = gtk.Entry(max=0)
        hbox.pack_start(self.module, expand=True, fill=True, padding=10)
        self.module.show()

        #empty label here to fill in space
        label = gtk.Label()
        hbox.pack_start(label, expand=False, fill=False, padding=50)
        label.show()

        # DOORS Data- Row 2
        hbox = gtk.HBox(homogeneous=False, spacing=2)
        vbox.pack_start(hbox, expand=False, fill=False, padding=3)
        hbox.show()

        label = gtk.Label("DOORS Baseline:")
        hbox.pack_start(label, expand=False, fill=False, padding=3)
        label.show()

        self.baseline = gtk.Entry(max=0)
        hbox.pack_start(self.baseline, expand=True, fill=True, padding=10)
        self.baseline.show()

        #empty label here to fill in space
        label = gtk.Label()
        hbox.pack_start(label, expand=False, fill=False, padding=80)
        label.show()

        # BIT #1 of self.debug
        #debug = gtk.CheckButton("Display Single Menu Items")
        #vbox.pack_start(debug, expand=False, fill=False, padding=10)
        #debug.show()

        # BIT #2 of self.debug
        #debug = gtk.CheckButton("Display Debug Dialog Data")
        #vbox.pack_start(debug, expand=False, fill=False, padding=10)
        #debug.show()

        separator = gtk.HSeparator()
        vbox.pack_start(separator, False, True, 0)
        # adjust width of entire dialog
        separator.set_size_request(500, 5)
        separator.show() 

        hbox = gtk.HBox(homogeneous=False, spacing=2)
        vbox.pack_start(hbox, expand=False, fill=False, padding=3)
        hbox.show()

        button = gtk.Button(" Continue ")
        hbox.pack_start(button, expand=True, fill=False, padding=10)
        button.show()
        button.connect('clicked', self.cont)

        button = gtk.Button("   Exit   ")
        hbox.pack_start(button, expand=True, fill=False, padding=10)
        button.show()
        button.connect('clicked', self.exit)

        self.window.add(vbox)
        vbox.show()
        self.window.show()

        self.temp_dir = os.getenv("TMP")
        if self.temp_dir == None:
            self.temp_dir = os.getenv("TEMP")
        if self.temp_dir == None:
            sys.exit("Environment variable TMP or TEMP not defined")

        try:
            self.config = os.path.join(self.temp_dir,"fmm_config.ini")
            fp = open(self.config,"r")
            data = fp.read().splitlines()
            fp.close()
        except:
            data = []

        if len(data) >= 4:
            self.file.set_text(data[0])
            self.module.set_text(data[1])
            self.baseline.set_text(data[2])
            self.view = data[3]
            try:
                self.debug = eval(data[4])
            except:
                self.debug = 1
        else:
            self.file.set_text("C:\\")
            self.module.set_text("/PCC Library/Feature Model Master")
            self.baseline.set_text("*")
            self.view = "Export_View"
            self.debug = 1
        self.run_enable = True

    def exit(self, widget, data=None):
        self.run_enable = False

    def get_configdata(self):
        while self.run_enable == True:
            gtk.main_iteration()

        if self.run_enable == "continue":
            self.file = self.file.get_text()
            self.module = self.module.get_text()
            self.baseline = self.baseline.get_text()
            #self.view = Not in the config GUI yet, but in the config file
            #self.debug = Not in the config GUI yet, but in the config file
            self.window.destroy()
        
            fp = open(self.config,"w")
            fp.write(self.file+"\n")
            fp.write(self.module+"\n")
            fp.write(self.baseline+"\n")
            fp.write(self.view+"\n")
            fp.write(str(self.debug)+"\n")
            fp.close()

            return True
        return False

    def cont(self, widget, data=None):
        self.run_enable = "continue"

    def browse(self, widget, data=None):
        file_select = gtk.FileSelection()
        file_select.set_filename(self.file.get_text())
        response = file_select.run()
        filename = file_select.get_filename()
        file_select.destroy()
        if response == gtk.RESPONSE_OK:
            self.file.set_text(filename)

fm_config = FMConfig()
