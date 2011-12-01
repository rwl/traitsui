#------------------------------------------------------------------------------
# Copyright (C) 2007 Riverbank Computing Limited
# Copyright (C) 2011 Richard Lincoln
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

""" Defines the various Boolean editors for the Muntjac user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from muntjac.api import CheckBox, TextField
from muntjac.ui.button import IClickListener

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.boolean_editor file.
from traitsui.editors.boolean_editor \
    import ToolkitEditorFactory

from editor \
    import Editor

# This needs to be imported in here for use by the editor factory for boolean
# editors (declared in traitsui). The editor factory's text_editor
# method will use the TextEditor in the ui.
from text_editor \
    import SimpleEditor as TextEditor

from constants \
    import ReadonlyColor

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor, IClickListener ):
    """ Simple style of editor for Boolean values, which displays a check box.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = CheckBox()
        self.control.addListener(self, IClickListener)
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user clicking on the checkbox:
    #---------------------------------------------------------------------------

    def buttonClick ( self, event ):
        """ Handles the user clicking the checkbox.
        """
        self.value = event.getButton().booleanValue()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.setValue(self.value)

#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyEditor ( Editor ):
    """ Read-only style of editor for Boolean values, which displays static text
    of either "True" or "False".
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = TextField()
        self.control.setReadOnly(True)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #
    #  (Should normally be overridden in a subclass)
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if self.value:
            self.control.setValue('True')
        else:
            self.control.setValue('False')
