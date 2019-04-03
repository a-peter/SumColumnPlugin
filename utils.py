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
			
			return value_pair
		else:
			return None
			
	def get_all_columns(self):
		return self.custom_columns