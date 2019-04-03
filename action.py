#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2019, Anselm Peter <anselm.peter@mail.de>'
__docformat__ = 'restructuredtext en'

if False:
	# This is here to keep my python error checker from complaining about
	# the builtin functions that will be defined by the plugin loading system
	# You do not need this code in your plugins
	get_icons = get_resources = None

try:
	from PyQt5.Qt import QToolButton, QMenu, QIcon
except ImportError:
	from PyQt4.Qt import QToolButton, QMenu, QIcon

# The class that all interface action plugins must inherit from
from calibre.gui2 import question_dialog, info_dialog
from calibre.gui2.actions import InterfaceAction

import calibre_plugins.sum_column.config as config

try:
    load_translations()
except NameError:
    pass # load_translations() added in calibre 1.9

class InterfacePlugin(InterfaceAction):

	name = 'Sum Column'

	# Declare the main action associated with this plugin
	# The keyboard shortcut can be None if you dont want to use a keyboard
	# shortcut. Remember that currently calibre has no central management for
	# keyboard shortcuts, so try to use an unusual/unused shortcut.
	action_spec = (_('Sum Column'), None, _('Sums up the values of a configurable column for selected books.'), None)
	popup_type = QToolButton.MenuButtonPopup
	action_type = 'current'

	# inherited method
	def genesis(self):
		self.is_library_selected = True
		# This method is called once per plugin, do initial setup here

		# Set the icon for this interface action
		# The get_icons function is a builtin function defined for all your
		# plugin code. It loads icons from the plugin zip file. It returns
		# QIcon objects, if you want the actual data, use the analogous
		# get_resources builtin function.
		#
		# Note that if you are loading more than one icon, for performance, you
		# should pass a list of names to get_icons. In this case, get_icons
		# will return a dictionary mapping names to QIcons. Names that
		# are not found in the zip file will result in null QIcons.
		self.icon = get_icons('images/icon.png')
		
		self.build_menu()

		# The qaction is automatically created from the action_spec defined
		# above
		self.qaction.setMenu(self.menu)
		self.qaction.setIcon(self.icon)
		self.qaction.triggered.connect(self.toolbar_action)

	def build_menu(self):
		# build up menu
		self.menu = QMenu(self.gui)

		action = self.create_menu_action(self.menu, 'SumColumnExecute', _('&Execute'), triggered=self.toolbar_action)
		action.setIcon(self.icon)
		
		self.menu.addSeparator()
		
		action = self.create_menu_action(self.menu, 'SumColumnConfig', _('&Configure') + '...', triggered=self.show_configuration)
		action.setIcon(QIcon(I('config.png')))		
		
	def toolbar_action(self):
		if not self._check_preconditions_for_sum():
			return
		columns = config.get_library_config_field(self.gui.current_db, config.PREFS_KEY_COLUMNS)
		book_ids = self.gui.library_view.get_selected_ids()
		print('summing up', columns.keys(), 'for', len(book_ids), 'books')
		
		self._do_sum_up(book_ids, columns)
		
	def _check_preconditions_for_sum(self):
		# Test if any library is active in calibre
		if not self.is_library_selected:
			print('No library selected, aborting')
			return False
		# Test if at least one book is selected
		rows = self.gui.library_view.selectionModel().selectedRows()
		if not rows or len(rows) == 0:
			print('No rows selected, aborting')
			return False
		# Test if a column to sum is selected in the configuration
		columns = config.get_library_config_field(self.gui.current_db, config.PREFS_KEY_COLUMNS)
		if not columns or len(columns)==0:
			if not question_dialog(self.gui, self.name, '<p>' + _('No column(s) selected. Do you want to select columns to sum up now?'), show_copy_button=False):
				return False
			self.show_configuration()
			return False
		return True

	def _do_sum_up(self, book_ids, columns):
		db = self.gui.current_db
		# get the database label for the selected # format of the columns
		labels = {}
		for key in columns.keys():
			column_name = '%s' % db.field_metadata[key].get('name')
			column_label = db.field_metadata.key_to_label(key) 
			labels[column_label] = [column_name, 0]
			# print('%s (%s) is known as %s' % (key, column_name, column_label) )

		sum = 0.0
		for book_id in book_ids:
			for label in labels.keys():
				value = db.get_custom(book_id, label=label, index_is_id=True)
				if not value is None:
					try:
						labels[label][1] += value
					except:
						print('Invalid value "{0}" to sum up'.format(value))

		self._show_result(labels, len(book_ids))
	
	def _show_result(self, labels = {}, number_of_books = 0):
		status = []
		if (number_of_books == 1):
			message = _('The sum is for {0} book <br/><table>').format(str(number_of_books))
		else:
			message = _('The sum is for {0} books <br/><table>').format(str(number_of_books))
		for k,v in labels.items():
			message += '<tr><td>{0}</td><td>=</td><td>{1}</td></tr>'.format(v[0], v[1])
			status.append('{0} = {1}'.format(v[0],v[1]))
		message += '</table>'
		info_dialog(self.gui, 'Sum Column', '<p>' + message, show=True, show_copy_button=False)
		self.gui.status_bar.show_message(', '.join(status))
		print(', '.join(status))
		
	def show_configuration(self):
		self.interface_action_base_plugin.do_user_config(self.gui)
		
	def location_selected(self, location):
		self.is_library_selected = location == 'library'
		
