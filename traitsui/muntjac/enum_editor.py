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

""" Defines the various editors and the editor factory for single-selection
    enumerations, for the Muntjac user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from string import capitalize

from muntjac.api \
    import ComboBox, ListSelect, OptionGroup

from muntjac.data.property \
    import IValueChangeListener

from muntjac.event.field_events \
    import IBlurListener

from traits.api \
    import Bool, Property

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.enum_editor file.
from traitsui.editors.enum_editor \
    import ToolkitEditorFactory

from editor \
    import Editor

from constants \
    import OKColor, ErrorColor

from helper \
    import enum_values_changed

#-------------------------------------------------------------------------------
#  'BaseEditor' class:
#-------------------------------------------------------------------------------

class BaseEditor ( Editor ):
    """ Base class for enumeration editors.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current set of enumeration names:
    names = Property

    # Current mapping from names to values:
    mapping = Property

    # Current inverse mapping from values to names:
    inverse_mapping = Property

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if factory.name != '':
            self._object, self._name, self._value = \
                self.parse_extended_name( factory.name )
            self.values_changed()
            self._object.on_trait_change( self._values_changed,
                                          ' ' + self._name, dispatch = 'ui' )
        else:
            factory.on_trait_change( self.rebuild_editor, 'values_modified',
                                     dispatch = 'ui' )

    #---------------------------------------------------------------------------
    #  Gets the current set of enumeration names:
    #---------------------------------------------------------------------------

    def _get_names ( self ):
        """ Gets the current set of enumeration names.
        """
        if self._object is None:
            return self.factory._names

        return self._names

    #---------------------------------------------------------------------------
    #  Gets the current mapping:
    #---------------------------------------------------------------------------

    def _get_mapping ( self ):
        """ Gets the current mapping.
        """
        if self._object is None:
            return self.factory._mapping

        return self._mapping

    #---------------------------------------------------------------------------
    #  Gets the current inverse mapping:
    #---------------------------------------------------------------------------

    def _get_inverse_mapping ( self ):
        """ Gets the current inverse mapping.
        """
        if self._object is None:
            return self.factory._inverse_mapping

        return self._inverse_mapping

    #---------------------------------------------------------------------------
    #  Rebuilds the contents of the editor whenever the original factory
    #  object's 'values' trait changes:
    #---------------------------------------------------------------------------

    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** trait changes.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Recomputes the cached data based on the underlying enumeration model:
    #---------------------------------------------------------------------------

    def values_changed ( self ):
        """ Recomputes the cached data based on the underlying enumeration model.
        """
        self._names, self._mapping, self._inverse_mapping = \
            enum_values_changed( self._value() )

    #---------------------------------------------------------------------------
    #  Handles the underlying object model's enumeration set being changed:
    #---------------------------------------------------------------------------

    def _values_changed ( self ):
        """ Handles the underlying object model's enumeration set being changed.
        """
        self.values_changed()
        self.rebuild_editor()

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self._object is not None:
            self._object.on_trait_change( self._values_changed,
                                          ' ' + self._name, remove = True )
        else:
            self.factory.on_trait_change( self.rebuild_editor,
                                          'values_modified', remove = True )

        super( BaseEditor, self ).dispose()

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( BaseEditor, IValueChangeListener, IBlurListener ):
    """ Simple style of enumeration editor, which displays a combo box.
    """

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super( SimpleEditor, self ).init( parent )

        self.control = control = ComboBox()
        control.setNullSelectionAllowed(False)
        control.setImmediate(True)
        for n in self.names:
            control.addItem( str(n) )

        control.addListener(self, IValueChangeListener)

        if self.factory.evaluate is not None:
            control.setTextInputAllowed(True)
            control.addListener(self, IBlurListener)

        self._no_enum_update = 0
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user selecting a new value from the combo box:
    #---------------------------------------------------------------------------

    def blur(self, event):
        self.update_text_object( str(event.getProperty()) )

    def valueChange ( self, event ):
        self.update_object( str(event.getProperty()) )

    def update_object (self, text):
        """ Handles the user selecting a new value from the combo box.
        """
        if self._no_enum_update == 0:
            self._no_enum_update += 1

            try:
                self.value = self.mapping[unicode(text)]
            except:
                pass

            self._no_enum_update -= 1

    #---------------------------------------------------------------------------
    #  Handles the user typing text into the combo box text entry field:
    #---------------------------------------------------------------------------

    def update_text_object(self, text):
        """ Handles the user typing text into the combo box text entry field.
        """
        if self._no_enum_update == 0:
            value = unicode(text)

            try:
                value = self.mapping[value]
            except:
                try:
                    value = self.factory.evaluate(value)
                except Exception, excp:
                    self.error( excp )
                    return

            self._no_enum_update += 1
            self.value = value
#            self._set_background(OKColor)
            self._no_enum_update -= 1

    def update_autoset_text_object(self):
        # Don't get the final text with the editingFinished signal
        if self.control:
            text = self.control.getValue()
            return self.update_text_object(text)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if self._no_enum_update == 0:
            self._no_enum_update += 1
            if self.factory.evaluate is None:
                try:
                    itemId = self.inverse_mapping[self.value]
                    self.control.select( str(itemId) )
                except:
                    itemId = self.control.getNullSelectionItemId()
                    self.control.select( str(itemId) )
            else:
                try:
                    self.control.setValue( str(self.str_value) )
                except:
                    self.control.setValue('')
            self._no_enum_update -= 1

    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------

    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        self.control.setComponentError( str(excp) )

    #---------------------------------------------------------------------------
    #  Rebuilds the contents of the editor whenever the original factory
    #  object's 'values' trait changes:
    #---------------------------------------------------------------------------

    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** trait changes.
        """
        self.control.removeAllItems()
        for n in self.names:
            self.control.addItem( str(n) )

        self.update_editor()

#-------------------------------------------------------------------------------
#  'RadioEditor' class:
#-------------------------------------------------------------------------------

class RadioEditor ( BaseEditor, IValueChangeListener ):
    """ Enumeration editor, used for the "custom" style, that displays radio
        buttons.
    """

    # Is the button layout row-major or column-major?
    row_major = Bool( False )

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super( RadioEditor, self ).init( parent )

        self.control = OptionGroup()
        self.control.setImmediate(True)
        self.control.setMultiSelect(False)
        self.control.addListener(self, IValueChangeListener)

        self.rebuild_editor()

    #---------------------------------------------------------------------------
    #  Handles the user clicking one of the 'custom' radio buttons:
    #---------------------------------------------------------------------------

    def valueChange(self, event):
        v = event.getProperty().getValue()
        self.value = self.mapping[v]


#    def update_object ( self, index ):
#        """ Handles the user clicking one of the custom radio buttons.
#        """
#        try:
#            self.value = self.mapping[self.names[index]]
#        except:
#            pass

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        label = value#self.string_value(value, capitalize)
        self.control.select( str(label) )

    #---------------------------------------------------------------------------
    #  Rebuilds the contents of the editor whenever the original factory
    #  object's 'values' trait changes:
    #---------------------------------------------------------------------------

    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** trait changes.
        """
        # Clear any existing content:
        self.control.removeAllItems()

        # Get the current trait value:
        cur_name = self.str_value

        # Create a sizer to manage the radio buttons:
        names   = self.names

        for name in names:
            label = name#self.string_value(name, capitalize)
            self.control.addItem( str(label) )

        label = cur_name#self.string_value(cur_name, capitalize)
        self.control.select( str(label) )

#-------------------------------------------------------------------------------
#  'ListEditor' class:
#-------------------------------------------------------------------------------

class ListEditor ( BaseEditor, IValueChangeListener ):
    """ Enumeration editor, used for the "custom" style, that displays a list
        box.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super( ListEditor, self ).init( parent )

        self.control = control = ListSelect()
        control.addListener(self, IValueChangeListener)
        control.setImmediate(True)
        control.setNullSelectionAllowed(False)
        if len(self.names) <= 10:
            control.setRows(len(self.names))
        else:
            control.setRows(10)

        self.rebuild_editor()
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user selecting a list box item:
    #---------------------------------------------------------------------------

    def valueChange(self, event):
        v = str(event.getProperty())
        self.update_object(v)

    def update_object(self, text):
        """ Handles the user selecting a list box item.
        """
        value = unicode(text)

        try:
            value = self.mapping[ value ]
        except:
            try:
                value = self.factory.evaluate( value )
            except:
                pass

        try:
            self.value = value
        except:
            pass

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        control = self.control

        try:
            value = self.inverse_mapping[self.value]

            control.select( str(value) )
        except:
            pass

    #---------------------------------------------------------------------------
    #  Rebuilds the contents of the editor whenever the original factory
    #  object's 'values' trait changes:
    #---------------------------------------------------------------------------

    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** trait changes.
        """
        self.control.removeAllItems()

        for name in self.names:
            self.control.addItem( str(name) )

        self.update_editor()
