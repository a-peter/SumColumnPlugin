#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2019, Anselm Peter <anselm.peter@mail.de>'
__docformat__ = 'restructuredtext en'

import copy

try:
	from PyQt5.Qt import QWidget, QGridLayout, QLabel, QHBoxLayout, QVBoxLayout
except ImportError:
	from PyQt4.Qt import QWidget, QGridLayout, QLabel, QHBoxLayout, QVBoxLayout

from calibre.utils.config import JSONConfig

from calibre_plugins.sum_column.utils import (get_library_uuid, CustomColumnComboBox)

# Library specific configuration
PREFS_NAMESPACE = 'SumColumnPlugin'
PREFS_KEY_SETTINGS = 'settings'

PREFS_KEY_COLUMN = 'column'
PREFS_KEY_SCHEMA_VERSION = 'SchemaVersion'
DEFAULT_SCHEMA_VERSION = 1

DEFAULT_LIBRARY_VALUES = {
	PREFS_KEY_COLUMN: ''
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
		
		print(dir(self.plugin_action))

		# Find user defined columns of type int or float
		self.available_columns = self._get_custom_columns()
		#for key, column in self.available_columns.iteritems():
		#	print(key, "###", column)
		#print(self.available_columns)

		self._initialize_layout()
		
	def save_settings(self):
		database = self.plugin_action.gui.current_db
		prefs = get_library_config(database)
		
		prefs[PREFS_KEY_COLUMN] = unicode(self.column_combo.get_selected_column())
		
		set_library_config(database, prefs)

	def _get_custom_columns(self):
		valid_column_types = ['float','int']
		custom_columns = self.plugin_action.gui.library_view.model().custom_columns
		self.available_columns = {}
		for key, column in custom_columns.iteritems():
			datatype = column['datatype']
			if datatype in valid_column_types:
				self.available_columns[key] = column
		return self.available_columns

	def _initialize_layout(self):
		# Get the current database
		database = self.plugin_action.gui.current_db
		library_config = get_library_config(database)

		layoutV = QVBoxLayout()
		
		layoutH = QHBoxLayout()
				
		# Build the OLD gui
		layoutGrid = QGridLayout()

		toolTip = _('Column to be summed up')
		column_label = QLabel(_('Column'), self)
		column_label.setToolTip(toolTip)

		column_from_preferences = library_config[PREFS_KEY_COLUMN]
		self.column_combo = CustomColumnComboBox(self, self.available_columns, column_from_preferences)
		self.column_combo.setToolTip(toolTip)
		layoutGrid.addWidget(column_label, 0, 0, 1, 1)
		layoutGrid.addWidget(self.column_combo, 0, 1, 1, 2)
		
		layoutH.addLayout(layoutGrid)
		layoutV.addLayout(layoutH)
		self.setLayout(layoutV)