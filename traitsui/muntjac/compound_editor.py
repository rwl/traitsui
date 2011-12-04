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

""" Defines the compound editor and the compound editor factory for the
Muntjac user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from muntjac.api \
    import VerticalLayout

from traits.api \
    import Str

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.compound_editor file.
from traitsui.editors.compound_editor \
    import ToolkitEditorFactory

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'CompoundEditor' class:
#-------------------------------------------------------------------------------

class CompoundEditor ( Editor ):
    """ Editor for compound traits, which displays editors for each of the
    combined traits, in the appropriate style.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The kind of editor to create for each list item
    kind = Str

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = VerticalLayout()
        self.control.setSizeUndefined()

        # Add all of the component trait editors:
        self._editors = editors = []
        for factory in self.factory.editors:
            editor = getattr( factory, self.kind )( self.ui, self.object,
                                       self.name, self.description, None )
            editor.prepare(self.control)
            self.control.addComponent(editor.control)
            editors.append(editor)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        for editor in self._editors:
            editor.dispose()

        super( CompoundEditor, self ).dispose()

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor(CompoundEditor):

    # The kind of editor to create for each list item. This value overrides
    # the default.
    kind = 'simple_editor'

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor(CompoundEditor):

    # The kind of editor to create for each list item. This value overrides
    # the default.

    kind = 'custom_editor'
