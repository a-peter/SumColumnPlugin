#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__   = 'GPL v3'
__copyright__ = '2019, Anselm Peter <anselm.peter@mail.de>'
__docformat__ = 'restructuredtext en'

try:
	from PyQt5 import QtWidgets as QtGui
	from PyQt5.Qt import (Qt, QIcon, QPixmap, QLabel, QDialog, QHBoxLayout, QProgressBar,
                          QTableWidgetItem, QFont, QLineEdit, QComboBox,
                          QVBoxLayout, QDialogButtonBox, QStyledItemDelegate, QDateTime,
                          QRegExpValidator, QRegExp, QTextEdit,
                          QListWidget, QAbstractItemView)
except ImportError as e:
    from PyQt4 import QtGui
    from PyQt4.Qt import (Qt, QIcon, QPixmap, QLabel, QDialog, QHBoxLayout, QProgressBar,
                          QTableWidgetItem, QFont, QLineEdit, QComboBox,
                          QVBoxLayout, QDialogButtonBox, QStyledItemDelegate, QDateTime,
                          QRegExpValidator, QRegExp, QTextEdit,
                          QListWidget, QAbstractItemView)
						  
def get_library_uuid(db):
	try:
		library_uuid = db.library_id
	except:
		library_uuid = ''
	return library_uuid

class CustomColumnComboBox(QComboBox):

	def __init__(self, parent, custom_columns={}, selected_column='', initial_items=['']):
		QComboBox.__init__(self, parent)
		self.populate_combo(custom_columns, selected_column, initial_items)

	def populate_combo(self, custom_columns, selected_column, initial_items=['']):
		self.clear()
		self.column_names = list(initial_items)
		if len(initial_items) > 0:
			self.addItems(initial_items)
		selected_idx = 0
		for idx, value in enumerate(initial_items):
			if value == selected_column:
				selected_idx = idx
		for key in sorted(custom_columns.keys()):
			self.column_names.append(key)
			self.addItem('%s (%s)'%(key, custom_columns[key]['name']))
			if key == selected_column:
				selected_idx = len(self.column_names) - 1
		self.setCurrentIndex(selected_idx)
		
	def select_column(self, key):
		selected_idx = 0
		for i, val in enumerate(self.column_names):
			if val == key:
				selected_idx = i
				break
		self.setCurrentIndex(selected_idx)

	def get_selected_column(self):
		return self.column_names[self.currentIndex()]

class CustomListWidget(QListWidget):
	def __init__(self, parent, custom_columns={}):
		QListWidget.__init__(self, parent)
		self.init_with_list(custom_columns)
		
	def init_with_list(self, custom_columns):
		self.clear()
		self.column_names = []
		for key in sorted(custom_columns.keys()):
			self.column_names.append(key)
			self.addItem('{0} ({1})'.format(custom_columns[key]['name'], key))
			
	def get_selected_column(self):
		if self.currentRow() != -1:
			row = self.column_names[self.currentRow()]
			return row
		else:
			return None
			
