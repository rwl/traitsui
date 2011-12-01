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

""" Defines the various text editors for the Muntjac user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from muntjac.api import TextField, PasswordField

from muntjac.data.property import IValueChangeListener
from muntjac.event.field_events import IBlurListener

from traits.api \
    import TraitError

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.text_editor file.
from traitsui.editors.text_editor \
    import evaluate_trait, ToolkitEditorFactory

from editor \
    import Editor

from editor_factory \
    import ReadonlyEditor as BaseReadonlyEditor

from constants \
    import OKColor

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor, IValueChangeListener, IBlurListener ):
    """ Simple style text editor, which displays a text field.
    """

    # Flag for window styles:
    base_style = TextField

    # Background color when input is OK:
    ok_color = OKColor

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Function used to evaluate textual user input:
    evaluate = evaluate_trait

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        wtype = self.base_style
        self.evaluate = factory.evaluate
        self.sync_value(factory.evaluate_name, 'evaluate', 'from')

        if not factory.multi_line or factory.is_grid_cell or factory.password:
            if factory.password:
                wtype = PasswordField
            else:
                wtype = TextField

        multi_line = (wtype is not TextField and wtype is not PasswordField)
        if multi_line:
            self.scrollable = True

        control = wtype()
        control.setValue( str(self.str_value) )

        if factory.auto_set and not factory.is_grid_cell:
            control.addListener(self, IValueChangeListener)
        else:
            # Assume enter_set is set, otherwise the value will never get
            # updated.
            control.addListener(self, IBlurListener)

        self.control = control
        self.set_error_state( False )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------

    def blur ( self, event ):
        """Fired when the field loses keyboard focus"""
        self.update_object()

    def valueChange ( self, event ):
        self.update_object()

    def update_object ( self ):
        """ Handles the user entering input data in the edit control.
        """
        if (not self._no_update) and (self.control is not None):
            try:
                self.value = self._get_user_value()

                if self._error is not None:
                    self._error = None
                    self.ui.errors -= 1

                self.set_error_state( False )

            except TraitError:
                pass

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        user_value = self._get_user_value()
        try:
            unequal = bool(user_value != self.value)
        except ValueError:
            # This might be a numpy array.
            unequal = True

        if unequal:
            self._no_update = True
            self.control.setValue( str(self.str_value) )
            self._no_update = False

        if self._error is not None:
            self._error = None
            self.ui.errors -= 1
            self.set_error_state( False )

    #---------------------------------------------------------------------------
    #  Gets the actual value corresponding to what the user typed:
    #---------------------------------------------------------------------------

    def _get_user_value ( self ):
        """ Gets the actual value corresponding to what the user typed.
        """
        value = self.control.getValue()

        value = unicode(value)

        try:
            value = self.evaluate( value )
        except:
            pass

        try:
            ret = self.factory.mapping.get(value, value)
        except TypeError:
            # The value is probably not hashable.
            ret = value

        return ret

    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------

    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        if self._error is None:
            self._error = True
            self.ui.errors += 1

        self.set_error_state( True )

    #---------------------------------------------------------------------------
    #  Returns whether or not the editor is in an error state:
    #---------------------------------------------------------------------------

    def in_error_state ( self ):
        """ Returns whether or not the editor is in an error state.
        """
        return (self.invalid or self._error)

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor ):
    """ Custom style of text editor, which displays a multi-line text field.
    """

    # FIXME: The wx version exposes a wx constant.
    # Flag for window style. This value overrides the default.
    base_style = TextField

#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyEditor ( BaseReadonlyEditor ):
    """ Read-only style of text editor, which displays a read-only text field.
    """

    base_style = PasswordField
