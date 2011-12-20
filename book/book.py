#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script for managing multiple pages in GIMP, intended for working with comic books, illustrated childrens books,
# sketchbooks or similar.
#
# Copyright 2011 - Ragnar Brynjúlfsson
# TODO! Add license info
#
# http://queertales.com
import os
# import sys
import hashlib
import json
import shutil
import gtk
import gobject
import urllib
from gimpfu import *
from gimpenums import *
from time import strftime

class Thumb():
    # Managing thumbnails, and creating new ones when needed.
    def __init__(self, imagepath):
        self.imagepath = imagepath
        if not self.find_thumb():
            self.build_thumb()
            if not self.find_thumb():
                show_error_msg('Failed to find or build thumb for %s.' % self.imagepath)

    def build_thumb(self):
        # Build or rebuild a thumb for the image.
        img = pdb.gimp_xcf_load(0, self.imagepath, self.imagepath)
        pdb.gimp_file_save_thumbnail(img, self.imagepath)
        pdb.gimp_image_delete(img)
        
    def find_thumb(self):
        # Find the pages thumbnail.
        # TODO! Fails with some obscure characters like !?* ...needs testing.
        imagepathuri = urllib.quote(self.imagepath.encode("utf-8"))
        file_hash = hashlib.md5('file://'+imagepathuri).hexdigest()
        thumb = os.path.join(os.path.expanduser('~/.thumbnails/large'), file_hash) + '.png'
        if os.path.exists(thumb):
            self.thumbpix = gtk.gdk.pixbuf_new_from_file(thumb)
            return True
        else:
            thumb = os.path.join(os.path.expanduser('~/.thumbnails/normal'), file_hash) + '.png'
            if os.path.exists(thumb):
                self.thumbpix = gtk.gdk.pixbuf_new_from_file(thumb)
                return True
            else:
                return False

class NewBookWin(gtk.Window):
    # Interface for creating new books.
    def __init__(self, main):
        self.main = main
        # Create a new book.
        win = super(NewBookWin, self).__init__()
        self.set_title("Create a New Book...")
        self.set_size_request(300, 300)
        self.set_position(gtk.WIN_POS_CENTER)

        # TODO! Fix the layout, so that everything aligns properly.
        # Box for divding the window in three parts, name, page and buttons.
        cont = gtk.VBox(False, 4)
        self.add(cont)

        # Frame for the book name and path.
        bookframe = gtk.Frame()
        bookframe.set_shadow_type(gtk.SHADOW_NONE)
        bookframelabel = gtk.Label("<b>Book</b>")
        bookframelabel.set_use_markup(True)
        bookframe.set_label_widget(bookframelabel)
        cont.add(bookframe)
        # Split the book frame in 4.
        bookbox = gtk.VBox(False, 2)
        bookframe.add(bookbox)
        # Name entry field
        namebox = gtk.HBox(False, 2)
        bookbox.pack_start(namebox)
        namelabel = gtk.Label("Name:")
        self.nameentry = gtk.Entry()
        namebox.pack_start(namelabel)
        namebox.pack_start(self.nameentry)
        # Destination dialog
        destdialog = gtk.FileChooserDialog("Create a New Book", None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        destdialog.set_default_response(gtk.RESPONSE_OK)
        # Destination
        destbox = gtk.HBox(False, 2)
        bookbox.pack_start(destbox)
        destlabel = gtk.Label("Destination:")
        self.destbutton = gtk.FileChooserButton(destdialog)
        destbox.pack_start(destlabel)
        destbox.pack_start(self.destbutton)
        
        # Frame for the page size and color space.
        pageframe = gtk.Frame()
        pageframe.set_shadow_type(gtk.SHADOW_NONE)
        pageframelabel = gtk.Label("<b>Page</b>")
        pageframelabel.set_use_markup(True)
        pageframe.set_label_widget(pageframelabel)
        cont.add(pageframe)
        # Split the frame in 6
        pagebox = gtk.VBox(False, 2)
        pageframe.add(pagebox)
        # Width and height fields.
        widthbox = gtk.HBox(False, 2)
        pagebox.pack_start(widthbox)
        widthlabel = gtk.Label("Width:")
        widthadjust = gtk.Adjustment(1024, 1, 262144, 1, 100)
        self.widthentry = gtk.SpinButton(widthadjust)
        widthpixels = gtk.Label("pixels")
        widthbox.pack_start(widthlabel)
        widthbox.pack_start(self.widthentry)
        widthbox.pack_start(widthpixels)
        heightbox = gtk.HBox(False, 2)
        pagebox.pack_start(heightbox)
        heightlabel = gtk.Label("Height:")
        heightadjust = gtk.Adjustment(1024, 1, 262144, 1, 100)
        self.heightentry = gtk.SpinButton(heightadjust)
        heightpixels = gtk.Label("pixels")
        heightbox.pack_start(heightlabel)
        heightbox.pack_start(self.heightentry)
        heightbox.pack_start(heightpixels)
        # Color space:
        colorbox = gtk.HBox(False, 2)
        pagebox.pack_start(colorbox)
        colorlabel = gtk.Label("Color Space:")
        colorlist = gtk.ListStore(gobject.TYPE_STRING)
        colors = [ "RBG color", "Grayscale" ]
        for color in colors:
            colorlist.append([color])
        self.colormenu = gtk.ComboBox(colorlist)
        colorcell = gtk.CellRendererText()
        self.colormenu.pack_start(colorcell, True)
        self.colormenu.add_attribute(colorcell, 'text', 0)
        self.colormenu.set_active(0)
        colorbox.pack_start(colorlabel)
        colorbox.pack_start(self.colormenu)
        # Background fill.
        fillbox = gtk.HBox(False, 2)
        pagebox.pack_start(fillbox)
        filllabel = gtk.Label("Fill with:")
        filllist = gtk.ListStore(gobject.TYPE_STRING)
        fills = [ "Foreground color", "Background color", "White", "Transparency" ]
        for fill in fills:
            filllist.append([fill])
        self.fillmenu = gtk.ComboBox(filllist)
        fillcell = gtk.CellRendererText()
        self.fillmenu.pack_start(fillcell, True)
        self.fillmenu.add_attribute(fillcell, 'text', 0)
        self.fillmenu.set_active(1)
        fillbox.pack_start(filllabel)
        fillbox.pack_start(self.fillmenu)
        
        # Buttons
        buttonbox = gtk.HBox(False, 2)
        cont.add(buttonbox)
        # Help
        helpbutton = gtk.Button("Help")
        helpbutton.connect("clicked", self.help) # No pun intended!
        buttonbox.pack_start(helpbutton)
        # Cancel
        cancelbutton = gtk.Button("Cancel")
        cancelbutton.connect("clicked", self.cancel)
        buttonbox.pack_start(cancelbutton)
        # OK
        okbutton = gtk.Button("Ok")
        okbutton.connect("clicked", self.ok)
        buttonbox.pack_start(okbutton)

        self.show_all()


    def help(self, widget):
        # Displays help for the new book dialog.
        helpdialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, "TODO! Help for this window")
        helpdialog.run()
        helpdialog.destroy()

    def cancel(self, widget):
        # Cancel book creation and close the window.
        self.destroy()

    def ok(self, widget):
        # Creates a new book.
        self.book = Book()
        self.book.make_book(self.destbutton.get_filename(), self.nameentry.get_text(), self.widthentry.get_value(), self.heightentry.get_value(), self.colormenu.get_active(), self.fillmenu.get_active())
        self.main.add_book(self.book)
        self.destroy()

class ExportWin(gtk.Window):
    # Windows for exporting the book in various formats.
    def __init__(self, main):
        # Build the export window.
        self.main = main
        win = super(ExportWin, self).__init__()
        self.set_title("Export Book...")
        self.set_size_request(300, 300)
        self.set_position(gtk.WIN_POS_CENTER)
        # Box for divding the window in three parts, name, page and buttons.
        cont = gtk.VBox(False, 4)
        self.add(cont)
        # Output destination and name
        outframe = gtk.Frame()
        outframe.set_shadow_type(gtk.SHADOW_NONE)
        outframelabel = gtk.Label("<b>Export Name and Destination</b>")
        outframelabel.set_use_markup(True)
        outframe.set_label_widget(outframelabel)
        cont.add(outframe)
        # Name to use
        nametable = gtk.Table(3, 2, True)
        cont.pack_start(nametable)
        entry1 = gtk.Label("ONE")
        entry2 = gtk.Label("TWO")
        nametable.attach(entry1, 0, 2, 0, 2)
        nametable.attach(entry2, 1, 3, 1, 3)
        # WORKING HERE!
        namelabel = gtk.Label("Filename:")
        namelist = gtk.ListStore(gobject.TYPE_STRING)
        nameoptions = [ "Use Book Name", "Use Page Names", "Enter Name" ]
        for nameoption in nameoptions:
            namelist.append([nameoption])
        self.namemenu = gtk.ComboBox(namelist)
        namecell = gtk.CellRendererText()
        self.namemenu.pack_start(namecell, True)
        self.namemenu.add_attribute(namecell, 'text', 0)
        self.namemenu.set_active(0)
        # Name entry field
        nameentrybox = gtk.HBox(True, 2)
        cont.pack_start(nameentrybox)
        nameentrylabel = gtk.Label("Name:")
        self.nameentry = gtk.Entry()
        nameentrybox.pack_start(nameentrylabel)
        nameentrybox.pack_start(self.nameentry)
        # Frame for the crop
        cropframe = gtk.Frame()
        cropframe.set_shadow_type(gtk.SHADOW_NONE)
        cropframelabel = gtk.Label("<b>Crop and Resize</b>")
        cropframelabel.set_use_markup(True)
        cropframe.set_label_widget(cropframelabel)
        cont.add(cropframe)
        # Split the book frame in 4.
        cropbox = gtk.VBox(True, 4)
        cropframe.add(cropbox)
        # Crop entry fields.
        # x
        xcropbox = gtk.HBox(True, 2)
        cropbox.pack_start(xcropbox)
        xcroplabel = gtk.Label("x:")
        self.xcropentry = gtk.Entry()
        xcropbox.pack_start(xcroplabel)
        xcropbox.pack_start(self.xcropentry)
        # y
        ycropbox = gtk.HBox(True, 2)
        cropbox.pack_start(ycropbox)
        ycroplabel = gtk.Label("y:")
        self.ycropentry = gtk.Entry()
        ycropbox.pack_start(ycroplabel)
        ycropbox.pack_start(self.ycropentry)
        # width
        wcropbox = gtk.HBox(True, 2)
        cropbox.pack_start(wcropbox)
        wcroplabel = gtk.Label("Width:")
        self.wcropentry = gtk.Entry()
        wcropbox.pack_start(wcroplabel)
        wcropbox.pack_start(self.wcropentry)
        # height
        hcropbox = gtk.HBox(False, 2)
        cropbox.pack_start(hcropbox)
        hcroplabel = gtk.Label("Height:")
        self.hcropentry = gtk.Entry()
        hcropbox.pack_start(hcroplabel)
        hcropbox.pack_start(self.hcropentry)

        print "Opening the export window."
        #- Export
        #-- File naming
        #;--- Enter a name.
        #--- Use page names.
        #--- Use book name.
        #-- Crop and scale.
        #--- Crop: x,y,width,height
        #--- Scale: x, y, type (percent/pixels)
        #-- Include metadata where available.
        #-- Formats
        #--- xcf
        #--- Tiff (none or lzw)
        #--- jpg (meta data, compression ratio etc.)
        #--- png (include alpha)
        self.show_all()


class Book():
    # Stores and manages the data for the book.
    def __init__(self):
        # Defines basic variables to store.
        self.pagestore = gtk.ListStore(str, gtk.gdk.Pixbuf, bool)
        self.bookfile = ""  # The *.book for this book.
        self.bookname = ""  # The name of the book.
        self.pagepath = ""  # Path to the "pages" subfolder.
        self.trashpath = "" # Path to trash folder.
        self.selected = -1  # Index of the currently selected page, -1 if none.

    def make_book(self, dest, name, w, h, color, fill):
        # Build the files and folders needed for the book.
        width = int(w)
        height = int(h)
        if os.path.isdir(dest):
            if name:
                # Make folder dest/name
                fullpath = os.path.join(dest, name)
                if not os.path.isdir(fullpath):
                    os.makedirs(fullpath)
                # Make file dest/name/name.book
                metadata = json.dumps({ 'pages':[ 'Template.xcf' ] }, indent=4)
                bookfile = open(os.path.join(fullpath,name+".book"), "w")
                bookfile.write(metadata)
                bookfile.close()
                # Make folder dest/name/Pages and Trash
                if not os.path.isdir(os.path.join(fullpath,"pages")):
                    os.makedirs(os.path.join(fullpath,"pages"))
                if not os.path.isdir(os.path.join(fullpath,"trash")):
                    os.makedirs(os.path.join(fullpath,"trash"))
                # Make file dest/name/Template.xcf
                img = pdb.gimp_image_new(width, height, color)
                if color == 0:
                    bglayer = gimp.Layer(img, "Background", width, height, RGBA_IMAGE, 100, NORMAL_MODE)
                else:
                    bglayer = gimp.Layer(img, "Background", width, height, GRAYA_IMAGE, 100, NORMAL_MODE)
                if fill == 0:
                    bglayer.fill(FOREGROUND_FILL)
                elif fill == 1:
                    bglayer.fill(BACKGROUND_FILL)
                elif fill == 2:
                    bglayer.fill(WHITE_FILL)
                elif fill == 3:
                    bglayer.fill(TRANSPARENT_FILL)
                img.add_layer(bglayer, 0)
                pdb.gimp_xcf_save(0, img, None, os.path.join(fullpath, "pages", "Template.xcf") , "Template.xcf")
                # Load the newly created book.
                self.load_book(os.path.join(fullpath, name+".book"))
                # TODO! Check if everything was created correctly.
                return True
            else:
                show_error_msg("Name was left empty")
        else:
            show_error_msg("Destination does not exist.")

    def load_book(self, bookfile):
        # Loads a selected book.
        if os.path.exists(bookfile):
            self.bookfile = bookfile
            self.bookname = os.path.splitext(os.path.basename(self.bookfile))[0]
            bookpath = os.path.dirname(self.bookfile)
            self.pagepath = os.path.join(bookpath, "pages")
            self.trashpath = os.path.join(bookpath, "trash")
            # Load the pages.
            f = open(self.bookfile, "r")
            metatext = f.read()
            metadata = json.loads(metatext)
            f.close()
            for p in metadata['pages']:
                # Create a page object, and add to a list.
                thumb = Thumb(os.path.join(self.pagepath, p))
                self.pagestore.append((p, thumb.thumbpix, True))
            self.pagestore.connect("row-deleted", self.row_deleted)
            self.pagestore.connect("row-inserted", self.row_inserted)
            self.pagestore.connect("row-changed", self.row_changed)
            return True

    def row_deleted(self, pagestore, destination_index):
        self.save()

    def row_inserted(self, pagestore, destination_index, tree_iter):
        self.save()

    def row_changed(self, pagestore, destination_index, tree_iter):
        self.save()

    def open_page(self, iconview, number):
        # Open the page the user clicked in GIMP.
        number = number[0]
        pagetoopen = os.path.join(self.pagepath, self.pagestore[number][0])
        img = pdb.gimp_file_load(pagetoopen, pagetoopen)
        img.clean_all()
        gimp.Display(img)

    def save(self):
        # Dump the pagestore to the *.book file, saving the book.
        metadata = []
        for p in self.pagestore:
            if p[0]:
                metadata.append(p[0])
        savetofile = json.dumps({ 'pages': metadata }, indent=4)
        bookfile = open(self.bookfile, "w")
        bookfile.write(savetofile)
        bookfile.close()

    def add_page(self, p, dest):
        # Copy the template to a new page.
        try:
            p = p+".xcf"
            unique = True
            for a in self.pagestore:
                if a[0] == p:
                    unique = False
            if unique:
                template = os.path.join(self.pagepath, self.pagestore[0][0])
                shutil.copy(template, os.path.join(self.pagepath, p))
                thumb = Thumb(os.path.join(self.pagepath, p))
                self.pagestore.insert(dest, ( p, thumb.thumbpix, True))
                return True
            else:
                show_error_msg("Page names must be unique")
        except Exception, err:
            show_error_msg(err)

    def rename_page(self, p):
        # Rename a page.
        p = p+".xcf"
        unique = True
        for a in self.pagestore:
            if a[0] == p:
                unique = False
            if unique:
                try:
                    shutil.move(os.path.join(self.pagepath, self.pagestore[self.selected][0]), os.path.join(self.pagepath, p))
                    self.pagestore[self.selected][0] = p
                    return True
                except Exception, err:
                    show_error_msg(err)
            else:
                show_error_msg("Page names must be unique")
            
    def delete_page(self):
        # Delete the selected page.
        try:
            p = self.pagestore[self.selected][0]
            shutil.move(os.path.join(self.pagepath, p), os.path.join(self.trashpath,strftime("%Y%m%d_%H%M%S_")+p))
            piter = self.pagestore.get_iter_from_string(str(self.selected))
            self.pagestore.remove(piter)
            return True
        except Exception, err:
            show_error_msg(err)

    def export_book(self, destination, format, settings):
        # Export the entire book.
        pass



class Main(gtk.Window):
    # Builds a GTK windows for managing the pages of a book.
    def __init__ (self):
        window = super(Main, self).__init__()
        self.set_title("Book")
        self.set_size_request(600, 600)
        self.set_position(gtk.WIN_POS_CENTER)
        self.loaded = False  # If there is a book loaded in the interface.
        
        # Main menu
        mb = gtk.MenuBar()

        filemenu = gtk.Menu()
        i_file = gtk.MenuItem("File")
        i_file.set_submenu(filemenu)
        
        agr = gtk.AccelGroup()
        self.add_accel_group(agr)

        file_new = gtk.ImageMenuItem(gtk.STOCK_NEW, agr)
        file_new.set_label("New Book...")
        key, mod = gtk.accelerator_parse("<Control>N")
        file_new.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
        file_new.connect("activate", self.new_book)
        filemenu.append(file_new)

        file_open = gtk.ImageMenuItem(gtk.STOCK_OPEN, agr)
        file_open.set_label("Open Book...")
        key, mod = gtk.accelerator_parse("<Control>O")
        file_open.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
        file_open.connect("activate", self.open_book)
        filemenu.append(file_open)

        sep1 = gtk.SeparatorMenuItem()
        filemenu.append(sep1)

        self.file_export = gtk.ImageMenuItem(gtk.STOCK_OPEN, agr)
        self.file_export.set_label("Export Book...")
        key, mod = gtk.accelerator_parse("<Control>E")
        self.file_export.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
        self.file_export.connect("activate", self.export_win)
        self.file_export.set_sensitive(False)
        filemenu.append(self.file_export)

        sep2 = gtk.SeparatorMenuItem()
        filemenu.append(sep2)

        file_close = gtk.ImageMenuItem(gtk.STOCK_CLOSE, agr)
        file_close.set_label("Close Book...")
        key, mod = gtk.accelerator_parse("<Control>W")
        file_close.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
        file_close.connect("activate", gtk.main_quit)
        filemenu.append(file_close)

        mb.append(i_file)

        # Main toolbar
        toolbar = gtk.Toolbar()
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        self.add_page = gtk.ToolButton(gtk.STOCK_NEW)
        self.add_page.connect("clicked", self.ask_add_page)
        self.add_page.set_sensitive(False)
        self.add_page.set_tooltip_text("Add a new page.")
        self.del_page = gtk.ToolButton(gtk.STOCK_DELETE)
        self.del_page.connect("clicked", self.ask_delete_page)
        self.del_page.set_sensitive(False)
        self.del_page.set_tooltip_text("Delete the selected page.")
        self.ren_page = gtk.ToolButton(gtk.STOCK_PROPERTIES)
        self.ren_page.connect("clicked", self.ask_rename_page)
        self.ren_page.set_sensitive(False)
        self.ren_page.set_tooltip_text("Rename the selected page.")
        toolbar.insert(self.add_page, 0)
        toolbar.insert(self.del_page, 1)
        toolbar.insert(self.ren_page, 2)

        self.vbox = gtk.VBox(False, 2)
        self.vbox.pack_start(mb, False, False, 0)
        self.vbox.pack_start(toolbar, False, False, 0)

        self.thumbs = gtk.IconView()
        self.thumbs.set_text_column(0)
        self.thumbs.set_pixbuf_column(1)
        self.thumbs.set_reorderable(True)
        self.thumbs.set_columns(2)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.add(self.thumbs)
        self.vbox.pack_start(self.scroll, True, True, 0)
        
        self.add(self.vbox)
        self.connect("destroy", gtk.main_quit)
        self.show_all()
        return window    

    def new_book(self, widget):
        # Helper for opening up the New Book window.
        self.close_book()
        nb = NewBookWin(self)

    def open_book(self, widget):
        # Interface for opening an existing book.
        o = gtk.FileChooserDialog("Open Book", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        o.set_default_response(gtk.RESPONSE_OK)
        f = gtk.FileFilter()
        f.set_name("GIMP Book")
        f.add_pattern("*.book")
        o.add_filter(f)
        response = o.run()
        if response == gtk.RESPONSE_OK:
            self.close_book()
            self.book = Book()
            self.book.load_book(o.get_filename())
            self.show_book()
            self.loaded = True
            self.enable_controls()
        o.destroy()

    def add_book(self, book):
        # Add a book to the main window. You still new to show it.
        self.book = book
        self.loaded = True
        self.show_book()
        self.enable_controls()

    def show_book(self):
        # Load the pages into an IconView.
        self.thumbs.connect("selection-changed", self.select_page)
        self.thumbs.connect("item-activated", self.book.open_page)
        self.thumbs.set_model(self.book.pagestore)
        self.set_title("GIMP Book - %s" % (self.book.bookname))
        self.show_all()
        
    def export_win(self, widget):
        # Settings for exporting the book.
        exportWin = ExportWin(self)

    def select_page(self, thumbs):
        # A page has been selected.
        if self.thumbs.get_selected_items():
            self.book.selected = self.thumbs.get_selected_items()[0][0]
        else:
            self.book.selected = -1

    def ask_add_page(self, widget):
        # Add a new page to the current book.
        dest = self.book.selected
        if self.book.selected < 1:
            dest = len(self.book.pagestore)
        if self.loaded:
            response, text = self.name_dialog("Add a Page", "Enter Page Description: ")
            if response == gtk.RESPONSE_ACCEPT:
                if text:
                    self.book.add_page(text, dest)
                else:
                    show_error_msg("No page name entered.")
        else:
            show_error_msg("You need to create or load a book, before adding pages to it.")

    def ask_rename_page(self, widget):
        # Rename the selected page.
        if self.book.selected > -1:
            response, text = self.name_dialog("Rename Page", "Ente Page Description: ")
            if response == gtk.RESPONSE_ACCEPT:
                if text:
                    self.book.rename_page(text)

    def ask_delete_page(self, widget):
        # Delete the selected page.
        areyousure = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, 'Delete page "%s"?' % (self.book.pagestore[self.book.selected][0]))
        response = areyousure.run()
        if response == gtk.RESPONSE_YES:
            self.book.delete_page()
            areyousure.destroy()

    def name_dialog(self, title, label):
        # Dialog for entering page names.
        # TODO! Show message on illegal characters and duplicate file creation.
        dialog = gtk.Dialog(title,
                            None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dialog.set_default_response(gtk.RESPONSE_ACCEPT)
        hbox = gtk.HBox(False, 4)
        hbox.show()
        dialog.vbox.pack_start(hbox)
        label = gtk.Label(label)
        label.show()
        hbox.pack_start(label)
        entry = gtk.Entry()
        entry.set_activates_default(True)
        entry.show()
        hbox.pack_start(entry)
        response = dialog.run()
        text = entry.get_text()
        dialog.destroy()
        return response, text

    def enable_controls(self):
        # Enable the controles that are disabled when no book is loaded.
        self.add_page.set_sensitive(True)
        self.del_page.set_sensitive(True)
        self.ren_page.set_sensitive(True)
        self.file_export.set_sensitive(True)

    def show_progress(self):
        # Add a progress bar to the bottom of the window.
        self.progress = gtk.ProgressBar()
        self.progress.size_allocate(gtk.gdk.Rectangle(0, 0, 200, 5))
        self.progress.queue_resize()
        self.vbox.pack_end(self.progress)

    def remove_progress(self):
        self.progress.destroy()

    def close_book(self):
        if self.loaded:
            self.thumbs.set_model()
            del self.book
            self.loaded = False

def show_book():
    # Display the book window.
    r = Main()
    gtk.main()

def show_error_msg( msg ):
    # Output error messages to the GIMP error console.
    origMsgHandler = pdb.gimp_message_get_handler()
    pdb.gimp_message_set_handler(ERROR_CONSOLE)
    pdb.gimp_message(msg)
    pdb.gimp_message_set_handler(origMsgHandler)


# This is the plugin registration function
register(
    "python_fu_book",    
    "Tool for managing multiple pages of a comic book, childrens book or your sketch book.",
    "GNU GPL v2 or later.",
    "Ragnar Brynjúlfsson",
    "Ragnar Brynjúlfsson",
    "July 2011",
    "<Toolbox>/Windows/Book...",
    "",
    [
    ],  
    [],
    show_book,
)

main()
