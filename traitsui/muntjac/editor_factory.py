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

""" Defines the base Muntjac classes the various styles of editors used in a
Traits-based user interface.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import warnings

from muntjac.api import TextField, Label
from muntjac.data.property import IValueChangeListener
from muntjac.event.field_events import IFocusListener

from traits.api \
    import TraitError

from traitsui.editor_factory \
    import EditorFactory as BaseEditorFactory

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'EditorFactory' class
#   Deprecated alias for traitsui.editor_factory.EditorFactory
#-------------------------------------------------------------------------------

class EditorFactory(BaseEditorFactory):
    """ Deprecated alias for traitsui.editor_factory.EditorFactory.
    """

    def __init__(self, *args, **kwds):
        super(EditorFactory, self).__init__(*args, **kwds)
        warnings.warn("DEPRECATED: Use traitsui.editor_factory."
            ".EditorFactory instead.", DeprecationWarning)

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Base class for simple style editors, which displays a text field
    containing the text representation of the object trait value. Clicking in
    the text field displays an editor-specific dialog box for changing the
    value.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = _SimpleField(self)
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    #
    #  (Normally overridden in a subclass)
    #---------------------------------------------------------------------------

    def popup_editor(self):
        """ Invokes the pop-up editor for an object trait.
        """
        pass

#-------------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------------

class TextEditor ( Editor, IValueChangeListener ):
    """ Base class for text style editors, which displays an editable text
    field, containing a text representation of the object trait value.
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
        self.control.setValue( str(self.str_value) )
        self.control.addListener(self, IValueChangeListener)
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------

    def valueChange(self, event):
        """ Handles the user changing the contents of the edit control.
        """
        try:
            self.value = unicode(self.control.getValue())
        except TraitError:
            pass

#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyEditor ( Editor ):
    """ Base class for read-only style editors, which displays a read-only text
    field, containing a text representation of the object trait value.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = Label()
        self.control.setValue( str(self.str_value) )

#        if self.item.resizable is True or self.item.height != -1.0:
#            self.control.setSizePolicy(QtGui.QSizePolicy.Expanding,
#                                       QtGui.QSizePolicy.Expanding)
#            self.control.setWordWrap(True)

        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.setValue( str(self.str_value) )

#-------------------------------------------------------------------------------
#  '_SimpleField' class:
#-------------------------------------------------------------------------------

class _SimpleField(TextField, IFocusListener):

    def __init__(self, editor):
        TextField.__init__(self, editor.str_value)

#        self.setReadOnly(True)
        self._editor = editor

        self.addListener(self, IFocusListener)

    def focus(self, event):
#        QtGui.QLineEdit.mouseReleaseEvent(self, e)
#
#        if e.button() == QtCore.Qt.LeftButton:
            self._editor.popup_editor()
