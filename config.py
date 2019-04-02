#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2019, Anselm Peter <anselm.peter@mail.de>'
__docformat__ = 'restructuredtext en'

import copy

try:
	from PyQt5.Qt import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QToolButton, QIcon
except ImportError:
	from PyQt4.Qt import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QToolButton, QIcon

from calibre.utils.config import JSONConfig

from calibre_plugins.sum_column.utils import (get_library_uuid, CustomColumnComboBox, CustomListWidget)

# Library specific configuration
PREFS_NAMESPACE = 'SumColumnPlugin'
PREFS_KEY_SETTINGS = 'settings'

PREFS_KEY_COLUMN = 'column' # no longer needed. for settings migration
PREFS_KEY_COLUMNS = 'columns'
PREFS_KEY_SCHEMA_VERSION = 'SchemaVersion'
DEFAULT_SCHEMA_VERSION = 2

DEFAULT_LIBRARY_VALUES = {
	PREFS_KEY_COLUMNS: {}
}

# Plugin specific configuration
STORE_NAME = 'Options'
DEFAULT_STORE_VALUES = {}

# This is where all preferences for this *plugin* will be stored
# Remember that this name (i.e. plugins/sum_column) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/sum_column')

# Set defaults
prefs.defaults[STORE_NAME] = DEFAULT_STORE_VALUES

def migrate_library(db, library_config):
	schema_version = library_config.get(PREFS_KEY_SCHEMA_VERSION, 0)
	if schema_version == DEFAULT_SCHEMA_VERSION:
		return
		
	library_config[PREFS_KEY_SCHEMA_VERSION] = DEFAULT_SCHEMA_VERSION
	
	if PREFS_KEY_COLUMN in library_config:
		print('Deleting', PREFS_KEY_COLUMN, 'from preferences')
		del library_config[PREFS_KEY_COLUMN]
	if PREFS_KEY_COLUMNS not in library_config:
		print('Adding', PREFS_KEY_COLUMNS, 'to preferences')
		library_config[PREFS_KEY_COLUMNS] = {}
	
	set_library_config(db, library_config)

def get_library_config(db):
	library_config = db.prefs.get_namespaced(PREFS_NAMESPACE, PREFS_KEY_SETTINGS, copy.deepcopy(DEFAULT_LIBRARY_VALUES))
	migrate_library(db, library_config)
	return library_config
	
def set_library_config(db, library_config):
	db.prefs.set_namespaced(PREFS_NAMESPACE, PREFS_KEY_SETTINGS, library_config)
	
def get_library_config_field(db, field):
	library_config = get_library_config(db)
	return library_config[field]

class ConfigWidget(QWidget):

	def __init__(self, plugin_action):
		QWidget.__init__(self)
		self.plugin_action = plugin_action
		self.gui = plugin_action.gui
		self.available_columns = self._get_custom_columns()
		self._initialize_layout()
		
	def save_settings(self):
		database = self.gui.current_db
		prefs = get_library_config(database)
		prefs[PREFS_KEY_COLUMNS] = self.destinationList.get_all_columns()
		set_library_config(database, prefs)

	def _get_custom_columns(self):
		valid_column_types = ['float','int']
		custom_columns = self.plugin_action.gui.library_view.model().custom_columns
		available_columns = {}
		for key, column in custom_columns.iteritems():
			datatype = column['datatype']
			if datatype in valid_column_types:
				available_columns[key] = column
		return available_columns

	def _initialize_layout(self):
		# Get the current database
		database = self.plugin_action.gui.current_db
		library_config = get_library_config(database)
		columns_from_preferences = library_config[PREFS_KEY_COLUMNS]
		
		# remove already configured columns from available columns
		for key in columns_from_preferences.keys():
			if key in self.available_columns:
				del self.available_columns[key]
						
		# Build the gui
		layoutH = QHBoxLayout()
		
		self.sourceList = CustomListWidget(self.gui, self.available_columns)
		self.sourceList.setToolTip(_('List of available columns'))
		layoutH.addWidget(self.sourceList)
		
		button_layout = QVBoxLayout()
		layoutH.addLayout(button_layout)
		
		self.use_btn = QToolButton(self.gui)
		self.use_btn.setIcon(QIcon(I('forward.png')))
		self.use_btn.setToolTip(_('Use the column for statistic'))
		self.use_btn.clicked.connect(self._add_row)
		
		self.no_use_btn = QToolButton(self.gui)
		self.no_use_btn.setIcon(QIcon(I('back.png')))
		self.no_use_btn.setToolTip(_('Don\'t use the column for statistics'))
		self.no_use_btn.clicked.connect(self._remove_row)
		
		button_layout.addWidget(self.use_btn)
		button_layout.addStretch(1)
		button_layout.addWidget(self.no_use_btn)
		
		self.destinationList = CustomListWidget(self.gui, columns_from_preferences)
		self.destinationList.setToolTip(_('List of evaluated columns'))
		layoutH.addWidget(self.destinationList)
						
		self.setLayout(layoutH)
		
	def _add_row(self):
		item = self.sourceList.remove_selected_item()
		self.destinationList.add_item(item)
		
	def _remove_row(self):
		item = self.destinationList.remove_selected_item()
		self.sourceList.add_item(item)
		