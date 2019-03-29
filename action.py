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

class InterfacePlugin(InterfaceAction):

	name = 'Sum Column'

	# Declare the main action associated with this plugin
	# The keyboard shortcut can be None if you dont want to use a keyboard
	# shortcut. Remember that currently calibre has no central management for
	# keyboard shortcuts, so try to use an unusual/unused shortcut.
	action_spec = ('Sum Column', None, 'Summiert die Werte einer konfigurierbaren Spalte für ausgewählte Bücher.', None)
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
		icon = get_icons('images/icon.png')

		self.menu = QMenu(self.gui)
		action = self.create_menu_action(self.menu, 'SumColumnConfig', '&Anpassen' + '...', triggered=self.show_configuration)
		action.setIcon(QIcon(I('config.png')))

		# The qaction is automatically created from the action_spec defined
		# above
		self.qaction.setMenu(self.menu)
		self.qaction.setIcon(icon)
		self.qaction.triggered.connect(self.toolbar_action)

	def toolbar_action(self):
		if not self._check_preconditions_for_sum():
			return
		column = config.get_library_config_field(self.gui.current_db, config.PREFS_KEY_COLUMN)
		book_ids = self.gui.library_view.get_selected_ids()
		print('summing up', column, 'for', len(book_ids), 'books')
		
		self._do_sum_up(book_ids, column)
		
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
		column = config.get_library_config_field(self.gui.current_db, config.PREFS_KEY_COLUMN)
		if not column:
			if not question_dialog(self.gui, self.name, '<p>' + 'Keine Spalte ausgewählt. Wollen Sie jetzt eine Spalte auswählen?', show_copy_button=False):
				return False
			self.show_configuration()
			return False
		return True

	def _do_sum_up(self, book_ids, column):
		db = self.gui.current_db
		# get the database label for the selected # format of the column
		lbl = db.field_metadata.key_to_label(column)
		print(column, 'is known as', lbl)
		sum = 0.0
		for book_id in book_ids:
			value = db.get_custom(book_id, label=lbl, index_is_id=True)
			if not value is None:
				try:
					sum += value
				except:
					print('Invalid value to sum up')
		print('sum is', sum)
		info_dialog(self.gui, 'Sum Column', '<p>' + 'Die Summe der Spalte ' + column + ' von ' + str(len(book_ids)) + ' Büchern ist ' + str(sum), show=True, show_copy_button=False)
		self.gui.status_bar.show_message('Summe ist %f' % sum)
	
	def show_configuration(self):
		self.interface_action_base_plugin.do_user_config(self.gui)
		
	def location_selected(self, location):
		self.is_library_selected = location == 'library'
		
