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

""" Defines the HTML "editor" for the Muntjac user interface toolkit.
    HTML editors interpret and display HTML-formatted text.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from urllib import urlopen

from muntjac.api \
    import RichTextArea, Label

from traits.api import Str

from editor import Editor

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Simple style editor for HTML.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Is the HTML editor scrollable? This values override the default.
    scrollable = True

    # External objects referenced in the HTML are relative to this URL
    base_url = Str

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = RichTextArea()
        self.control.setSizeFull()

        if self.factory.open_externally:
            raise NotImplementedError

        self.base_url = self.factory.base_url
        self.sync_value( self.factory.base_url_name, 'base_url', 'from' )

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        text = self.str_value
        if self.factory.format_text:
            text = self.factory.parse_text( text )
        if self.base_url:
            url = self.base_url
            if not url.endswith("/"):
                url += "/"
            self.control.setValue( text , urlopen ( url ) )
        else:
            self.control.setValue( text )

    #-- Event Handlers ---------------------------------------------------------

    def _base_url_changed ( self ):
        self.update_editor()

#-EOF--------------------------------------------------------------------------
