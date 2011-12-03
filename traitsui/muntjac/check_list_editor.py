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

""" Defines the various editors for multi-selection enumerations, for the
Muntjac user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import logging
from string import capitalize

from muntjac.api import GridLayout, CheckBox, ComboBox
from muntjac.data.property import IValueChangeListener
from muntjac.data.util.indexed_container import IndexedContainer
from muntjac.ui.button import IClickListener

from traits.api \
    import List, Unicode, TraitError

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.check_list_editor file.
from traitsui.editors.check_list_editor \
    import ToolkitEditorFactory

from editor_factory \
    import TextEditor as BaseTextEditor

from editor \
    import EditorWithList

logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( EditorWithList, IValueChangeListener ):
    """ Simple style of editor for checklists, which displays a combo box.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Checklist item names
    names = List( Unicode )

    # Checklist item values
    values = List

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.create_control( parent )
        super( SimpleEditor, self ).init( parent )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Creates the initial editor control:
    #---------------------------------------------------------------------------

    def create_control ( self, parent ):
        """ Creates the initial editor control.
        """
        self.control = ComboBox()
        self.control.setMultiSelect(False)
        self.control.setNullSelectionAllowed(True)
        self.control.setImmediate(True)
        self.control.addListener(self, IValueChangeListener)

    #---------------------------------------------------------------------------
    #  Handles the list of legal check list values being updated:
    #---------------------------------------------------------------------------

    def list_updated ( self, values ):
        """ Handles updates to the list of legal checklist values.
        """
        sv = self.string_value
        if (len( values ) > 0) and isinstance( values[0], basestring ):
            values = [ ( x, sv( x, capitalize ) ) for x in values ]
        self.values = valid_values = [ x[0] for x in values ]
        self.names  =                [ x[1] for x in values ]

        # Make sure the current value is still legal:
        modified  = False
        cur_value = parse_value( self.value )
        for i in range( len( cur_value ) - 1, -1, -1 ):
            if cur_value[i] not in valid_values:
                try:
                    del cur_value[i]
                    modified = True
                except TypeError:
                    logger.warn('Unable to remove non-current value [%s] from '
                        'values %s', cur_value[i], values)
        if modified:
            if isinstance( self.value, basestring ):
                cur_value = ','.join( cur_value )
            self.value = cur_value

        self.rebuild_editor()

    #---------------------------------------------------------------------------
    #  Rebuilds the editor after its definition is modified:
    #---------------------------------------------------------------------------

    def rebuild_editor ( self ):
        """ Rebuilds the editor after its definition is modified.
        """
        control = self.control
        c = IndexedContainer()
        for name in self.names:
            c.addItem(name)
        control.setContainerDataSource(c)
        self.update_editor()

    #---------------------------------------------------------------------------
    #  Handles the user selecting a new value from the combo box:
    #---------------------------------------------------------------------------

    def valueChange(self, event):
        v = str(event.getProperty())
        self.update_object(v)

    def update_object ( self, text ):
        """ Handles the user selecting a new value from the combo box.
        """
        if unicode(text) in self.names:
            value = self.values[self.names.index(unicode(text))]
            if not isinstance(self.value, basestring):
                value = [value]
        elif not isinstance(self.value, basestring):
            value = []
        else:
            value = ''
        self.value = value

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        try:
            self.control.select( parse_value(self.value)[0] )
        except:
            pass

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor, IClickListener ):
    """ Custom style of editor for checklists, which displays a set of check
        boxes.
    """

    #---------------------------------------------------------------------------
    #  Creates the initial editor control:
    #---------------------------------------------------------------------------

    def create_control ( self, parent ):
        """ Creates the initial editor control.
        """
        self.control = GridLayout()
        self.control.setMargin(False)
        self.control.setSpacing(True)

    #---------------------------------------------------------------------------
    #  Rebuilds the editor after its definition is modified:
    #---------------------------------------------------------------------------

    def rebuild_editor ( self ):
        """ Rebuilds the editor after its definition is modified.
        """
        # Clear any existing content:
        self.control.removeAllComponents()

        cur_value = parse_value( self.value )

        # Create a sizer to manage the radio buttons:
        labels = self.names
        values = self.values
        n      = len( labels )
        cols   = self.factory.cols
        rows   = (n + cols - 1) / cols
        incr   = [ n / cols ] * cols
        rem    = n % cols
        for i in range( cols ):
            incr[i] += (rem > i)
        incr[-1] = -(reduce( lambda x, y: x + y, incr[:-1], 0 ) - 1)

        self.control.setRows(rows)
        self.control.setColumns(cols)

        # Add the set of all possible choices:
        layout = self.control
        index = 0
        for i in range( rows ):
            for j in range( cols ):
                if n > 0:
                    cb = CheckBox( str(labels[index]) )
                    cb.setImmediate(True)
                    cb.value = values[index]

                    if cb.value in cur_value:
                        cb.setValue(True)
                    else:
                        cb.setValue(False)

                    cb.addListener(self, IClickListener)

                    layout.addComponent(cb, j, i)

                    index += incr[j]
                    n -= 1

    #---------------------------------------------------------------------------
    #  Handles the user clicking one of the 'custom' check boxes:
    #---------------------------------------------------------------------------

    def buttonClick(self, event):
        cb = event.getButton()
        self.update_object(cb)

    def update_object(self, cb):
        """ Handles the user clicking one of the custom check boxes.
        """
        cur_value = parse_value(self.value)
        if cb.getValue():
            cur_value.append(cb.value)
        elif cb.value in cur_value:
            cur_value.remove(cb.value)

        if isinstance(self.value, basestring):
            cur_value = ','.join(cur_value)

        self.value = cur_value

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        new_values = parse_value( self.value )
        for cb in self.control.getComponentIterator():
            if cb.value in new_values:
                cb.setValue(True)
            else:
                cb.setValue(False)

#-------------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------------

class TextEditor ( BaseTextEditor ):
    """ Text style of editor for checklists, which displays a text field.
    """

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------

    def update_object ( self, event=None ):
        """ Handles the user changing the contents of the edit control.
        """
#        try:
        value = unicode(self.control.getValue())
        value = eval( value )
#        except:
#            pass
#        try:
        self.value = value
#        except TraitError:
#            pass

#-------------------------------------------------------------------------------
#  Parse a value into a list:
#-------------------------------------------------------------------------------

def parse_value ( value ):
    """ Parses a value into a list.
    """
    if value is None:
        return []
    if type( value ) is not str:
        return value[:]
    return [ x.strip() for x in value.split( ',' ) ]
