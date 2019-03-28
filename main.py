#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2019, Anselm Peter <anselm.peter@web.de>'
__docformat__ = 'restructuredtext en'

if False:
    # This is here to keep my python error checker from complaining about
    # the builtin functions that will be defined by the plugin loading system
    # You do not need this code in your plugins
    get_icons = get_resources = None

import copy

from PyQt5.Qt import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel

from calibre.utils.config import JSONConfig

from calibre_plugins.sum_column.config import prefs
from calibre_plugins.sum_column.utils import (get_library_uuid, CustomColumnComboBox)

PREFS_NAMESPACE = 'SumColumnPlugin'
PREFS_KEY_SETTINGS = 'settings'

KEY_CUSTOM_COLUMN = 'customColumn'

STORE_NAME = 'Options'

DEFAULT_STORE_VALUES = {
                        }

DEFAULT_LIBRARY_VALUES = {
                          KEY_CUSTOM_COLUMN: ''
                          }

# This is where all preferences for this plugin will be stored
plugin_prefs = JSONConfig('plugins/SumColumn')

# Set defaults
plugin_prefs.defaults[STORE_NAME] = DEFAULT_STORE_VALUES


def migrate_library_config_if_required(db, library_config):
    schema_version = library_config.get(KEY_SCHEMA_VERSION, 0)
    if schema_version == DEFAULT_SCHEMA_VERSION:
        return
    # We have changes to be made - mark schema as updated
    library_config[KEY_SCHEMA_VERSION] = DEFAULT_SCHEMA_VERSION

    # Any migration code in future will exist in here.
    if schema_version < 1.61:
        if 'customColumn' in library_config:
            print('Migrating Count Pages plugin custom column for pages to new schema')
            library_config[KEY_PAGES_CUSTOM_COLUMN] = library_config['customColumn']
            del library_config['customColumn']
        store_prefs = plugin_prefs[STORE_NAME]
        if KEY_PAGES_ALGORITHM not in library_config:
            print('Migrating Count Pages plugin algorithm for pages to new schema')
            library_config[KEY_PAGES_ALGORITHM] = store_prefs.get('algorithm', 0)
            # Unfortunately cannot delete since user may have other libraries
        if 'algorithmWords' in store_prefs:
            print('Deleting Count Pages plugin word algorithm')
            del store_prefs['algorithmWords']
            plugin_prefs[STORE_NAME] = store_prefs        

    set_library_config(db, library_config)

def get_library_config(db):
    library_id = get_library_uuid(db)
    library_config = None
    # Check whether this is a configuration needing to be migrated from json into database
    if 'libraries' in plugin_prefs:
        libraries = plugin_prefs['libraries']
        if library_id in libraries:
            # We will migrate this below
            library_config = libraries[library_id]
            # Cleanup from json file so we don't ever do this again
            del libraries[library_id]
            if len(libraries) == 0:
                # We have migrated the last library for this user
                del plugin_prefs['libraries']
            else:
                plugin_prefs['libraries'] = libraries

    if library_config is None:
        library_config = db.prefs.get_namespaced(PREFS_NAMESPACE, PREFS_KEY_SETTINGS,
                                                 copy.deepcopy(DEFAULT_LIBRARY_VALUES))
    migrate_library_config_if_required(db, library_config)
    return library_config

						  
class SumColumnDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        # The current database shown in the GUI
        # db is an instance of the class LibraryDatabase from db/legacy.py
        # This class has many, many methods that allow you to do a lot of
        # things. For most purposes you should use db.new_api, which has
        # a much nicer interface from db/cache.py
        self.db = gui.current_db

		# Find user defined columns of type int or float
		avail_columns = self.get_custom_columns()
		for key, column in avail_columns.iteritems():
			print(key, column)
		print(avail_columns)
        #library_config = get_library_config(self.gui.current_db)

		# prepare gui
        self.l = QVBoxLayout()
        self.setLayout(self.l)

        column_label = QLabel("Spalte", self) # QLabel(_('&Custom column:'), self)
        toolTip = ('Leave this blank if you do not want to count pages')
        column_label.setToolTip(toolTip)
		
		column_from_preferences = '' #library_config.get(KEY_PAGES_CUSTOM_COLUMN, '')
        self.column_combo = CustomColumnComboBox(self, avail_columns, column_from_preferences)
        self.column_combo.setToolTip(toolTip)
        column_label.setBuddy(self.column_combo)
        
		self.l.addWidget(column_label)
		self.l.addWidget(self.column_combo)
		
		#page_group_box_layout.addWidget(page_column_label, 0, 0, 1, 1)
        #page_group_box_layout.addWidget(self.page_column_combo, 0, 1, 1, 2)


        self.label = QLabel(prefs['hello_world_msg'])
        self.l.addWidget(self.label)

        self.setWindowTitle('Sum Column')
        self.setWindowIcon(icon)

        self.about_button = QPushButton('About', self)
        self.about_button.clicked.connect(self.about)
        self.l.addWidget(self.about_button)

        self.marked_button = QPushButton(
            'Show books with only one format in the calibre GUI', self)
        self.marked_button.clicked.connect(self.marked)
        self.l.addWidget(self.marked_button)

        self.view_button = QPushButton(
            'View the most recently added book', self)
        self.view_button.clicked.connect(self.view)
        self.l.addWidget(self.view_button)

        self.update_metadata_button = QPushButton(
            'Update metadata in a book\'s files', self)
        self.update_metadata_button.clicked.connect(self.update_metadata)
        self.l.addWidget(self.update_metadata_button)

        self.conf_button = QPushButton(
                'Configure this plugin', self)
        self.conf_button.clicked.connect(self.config)
        self.l.addWidget(self.conf_button)

        self.resize(self.sizeHint())
		

    def about(self):
        # Get the about text from a file inside the plugin zip file
        # The get_resources function is a builtin function defined for all your
        # plugin code. It loads files from the plugin zip file. It returns
        # the bytes from the specified file.
        #
        # Note that if you are loading more than one file, for performance, you
        # should pass a list of names to get_resources. In this case,
        # get_resources will return a dictionary mapping names to bytes. Names that
        # are not found in the zip file will not be in the returned dictionary.
        text = get_resources('about.txt')
        QMessageBox.about(self, 'About Sum Column',
                text.decode('utf-8'))

    def marked(self):
        ''' Show books with only one format '''
        db = self.db.new_api
        matched_ids = {book_id for book_id in db.all_book_ids() if len(db.formats(book_id)) == 1}
        # Mark the records with the matching ids
        # new_api does not know anything about marked books, so we use the full
        # db object
        self.db.set_marked_ids(matched_ids)

        # Tell the GUI to search for all marked records
        self.gui.search.setEditText('marked:true')
        self.gui.search.do_search()

    def view(self):
        ''' View the most recently added book '''
        most_recent = most_recent_id = None
        db = self.db.new_api
        for book_id, timestamp in db.all_field_for('timestamp', db.all_book_ids()).iteritems():
            if most_recent is None or timestamp > most_recent:
                most_recent = timestamp
                most_recent_id = book_id

        if most_recent_id is not None:
            # Get a reference to the View plugin
            view_plugin = self.gui.iactions['View']
            # Ask the view plugin to launch the viewer for row_number
            view_plugin._view_calibre_books([most_recent_id])

    def update_metadata(self):
        '''
        Set the metadata in the files in the selected book's record to
        match the current metadata in the database.
        '''
        from calibre.ebooks.metadata.meta import set_metadata
        from calibre.gui2 import error_dialog, info_dialog

        # Get currently selected books
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, 'Cannot update metadata',
                             'No books selected', show=True)
        # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        db = self.db.new_api
        for book_id in ids:
            # Get the current metadata for this book from the db
            mi = db.get_metadata(book_id, get_cover=True, cover_as_data=True)
            fmts = db.formats(book_id)
            if not fmts:
                continue
            for fmt in fmts:
                fmt = fmt.lower()
                # Get a python file object for the format. This will be either
                # an in memory file or a temporary on disk file
                ffile = db.format(book_id, fmt, as_file=True)
                ffile.seek(0)
                # Set metadata in the format
                set_metadata(ffile, mi, fmt)
                ffile.seek(0)
                # Now replace the file in the calibre library with the updated
                # file. We dont use add_format_with_hooks as the hooks were
                # already run when the file was first added to calibre.
                db.add_format(book_id, fmt, ffile, run_hooks=False)

        info_dialog(self, 'Updated files',
                'Updated the metadata in the files of %d book(s)'%len(ids),
                show=True)

    def config(self):
        self.do_user_config(parent=self)
        # Apply the changes
        self.label.setText(prefs['hello_world_msg'])

    def get_custom_columns(self):
        column_types = ['float','int']
        custom_columns = self.gui.library_view.model().custom_columns
        available_columns = {}
        for key, column in custom_columns.iteritems():
            typ = column['datatype']
            if typ in column_types:
                available_columns[key] = column
        return available_columns
