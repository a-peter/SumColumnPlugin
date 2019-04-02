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
	"""Class to manage calibre columns
	
	This special ListWidget takes a list of calibre columns.
	The columns are added as a special string formatted with
	name and internal name.
	
	Adding and removing of entries with calibre data is supported
	with methods add_item and remove_selected_item.
	"""
	
	def __init__(self, parent, custom_columns={}):
		QListWidget.__init__(self, parent)
		self.init_with_list(custom_columns)
		
	def init_with_list(self, custom_columns):
		self.clear()
		self.column_names = []
		self.custom_columns = {}
		for key in sorted(custom_columns.keys()):
			self._add_item(key, custom_columns[key])
			
	def add_item(self, value_pair):
		"""Adds a new calibre column_names
		
		The method expects a tuple with two entries. The first
		entry contains the internal search name with preceeding # sign.
		The second entry of the tuple contains the data of the calibre
		column."""
		if value_pair != None:
			if value_pair[0] in self.custom_columns:
				print('{0} already in list'.format(value_pair[0]))
				return
			self._add_item(value_pair[0], value_pair[1])

	def _add_item(self, row, data):
		self.column_names.append(row)
		self.custom_columns[row] = data
		self.addItem('{0} ({1})'.format(data['name'], row))
		#print('added', value_pair)
			
	def remove_selected_item(self):
		""" Removes the selected line
		
		Returns the removed pair of internal name and calibre data."""
		if self.currentRow() != -1:
			# prepare data
			item_index = self.currentRow()
			row = self.column_names[item_index]
			value_pair = (row, self.custom_columns[row])
			
			# remove data from lists
			del self.column_names[item_index]
			del self.custom_columns[row]
			self.takeItem(item_index)
			
			# for debug:
			#print('removed', value_pair)
			#print(self.column_names)
			#print(self.custom_columns)
			
			return value_pair
		else:
			return None
			
	def get_selected_column(self):
		"""Returns the internal name of the calibre column"""
		if self.currentRow() != -1:
			row = self.column_names[self.currentRow()]
			return row
		else:
			return None
			
	def get_selected_item(self):
		"""Returns the selected item as a tuple"""
		if self.currentRow() != -1:
			row = self.column_names[self.currentRow()]
			return (row, self.custom_columns[row])
		else:
			return None
			