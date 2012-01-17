#------------------------------------------------------------------------------
# Copyright (C) 2007 Riverbank Computing Limited
# Copyright (C) 2011 Richard Lincoln
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#------------------------------------------------------------------------------
from muntjac.addon.colorpicker.color_change_event import ColorChangeEvent

""" Defines the various color editors for the Muntjac user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from muntjac.addon.colorpicker.color_picker \
    import ColorPicker, ButtonStyle

from muntjac.addon.colorpicker.color \
    import Color

from traitsui.editors.color_editor \
    import ToolkitEditorFactory as BaseToolkitEditorFactory

from editor_factory \
    import SimpleEditor as BaseSimpleEditor, \
    TextEditor as BaseTextEditor, \
    ReadonlyEditor as BaseReadonlyEditor

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Standard color samples:
color_samples = []

#---------------------------------------------------------------------------
#  The Muntjac ToolkitEditorFactory class.
#---------------------------------------------------------------------------

## We need to add muntjac-specific methods to the editor factory (since all editors
## will be accessing these functions. Making these functions global functions
## in this file does not work quite well, since we want custom editors to
## override these methods easily.

class ToolkitEditorFactory(BaseToolkitEditorFactory):
    """ Muntjac editor factory for color editors.
    """

    #---------------------------------------------------------------------------
    #  Gets the Muntjac color equivalent of the object trait:
    #---------------------------------------------------------------------------

    def to_muntjac_color ( self, editor ):
        """ Gets the Muntjac color equivalent of the object trait.
        """
        if self.mapped:
            return getattr( editor.object, editor.name + '_' )

        return getattr( editor.object, editor.name )

    #---------------------------------------------------------------------------
    #  Gets the application equivalent of a Muntjac value:
    #---------------------------------------------------------------------------

    def from_muntjac_color ( self, color ):
        """ Gets the application equivalent of a Muntjac value.
        """
        return color

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified color value:
    #---------------------------------------------------------------------------

    def str_color ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        if isinstance(color, Color):
            alpha = color.getAlpha()
            if alpha == 255:
                return "(%d,%d,%d)" % (color.getRed(), color.getGreen(),
                        color.getBlue())

            return "(%d,%d,%d,%d)" % (color.getRed(), color.getGreen(),
                    color.getBlue(), alpha)

        return color

#-------------------------------------------------------------------------------
#  'SimpleColorEditor' class:
#-------------------------------------------------------------------------------

class SimpleColorEditor ( BaseSimpleEditor ):
    """ Simple style of color editor, which displays a text field whose
    background color is the color value. Selecting the text field displays
    a dialog box for selecting a new color value.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        color = self.factory.to_muntjac_color(self)
        self.control = ColorPicker(initialColor=color)
        self.control.setButtonStyle(ButtonStyle.BUTTON_AREA)
        self.control.setSizeFull()
        self.control.addCallback(self.update_object, ColorChangeEvent)

    #---------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    #---------------------------------------------------------------------------

#    def popup_editor(self):
#        """ Invokes the pop-up editor for an object trait.
#        """
#        color = self.factory.to_muntjac_color(self)
#        color = QtGui.QColorDialog.getColor(color, self.control)
#
#        if color.isValid():
#            self.value = self.factory.from_muntjac_color(color)
#            self.update_editor()

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------

    def update_object ( self ):
        """ Handles the user entering input data in the edit control.
        """
        color = self.control.getColor()
        self.value = self.factory.from_muntjac_color(color)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        super( SimpleColorEditor, self ).update_editor()
        color = self.factory.to_muntjac_color( self )
        self.control.setColor(color)

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified color value:
    #---------------------------------------------------------------------------

    def string_value ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        return self.factory.str_color( color )

#-------------------------------------------------------------------------------
#  'CustomColorEditor' class:
#-------------------------------------------------------------------------------

class CustomColorEditor ( SimpleColorEditor ):
    """ Custom style of color editor, which displays a color editor panel.
    """

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super(CustomColorEditor, self).init(parent)
        self.control.setButtonStyle(ButtonStyle.BUTTON_NORMAL)

##-------------------------------------------------------------------------------
##  'CustomColorEditor' class:
##-------------------------------------------------------------------------------
#
#class CustomColorEditor ( Editor ):
#    """ Custom style of color editor, which displays a color editor panel.
#    """
#
#    #---------------------------------------------------------------------------
#    #  Finishes initializing the editor by creating the underlying toolkit
#    #  widget:
#    #---------------------------------------------------------------------------
#
#    def init ( self, parent ):
#        """ Finishes initializing the editor by creating the underlying toolkit
#            widget.
#        """
#        color = self.factory.to_muntjac_color(self)
#        self.control = ColorPicker(initialColor=color)
#        self.control.setSizeFull()
#        self.control.addCallback(self.update_object, ColorChangeEvent)
#
#    #---------------------------------------------------------------------------
#    #  Updates the editor when the object trait changes external to the editor:
#    #---------------------------------------------------------------------------
#
#    def update_editor ( self ):
#        """ Updates the editor when the object trait changes externally to the
#            editor.
#        """
#        pass
#
#    #---------------------------------------------------------------------------
#    #  Handles the user entering input data in the edit control:
#    #---------------------------------------------------------------------------
#
#    def update_object ( self ):
#        """ Handles the user entering input data in the edit control.
#        """
#        color = self.control.getColor()
#        self.value = self.factory.from_muntjac_color(color)
#
#    #---------------------------------------------------------------------------
#    #  Returns the text representation of a specified color value:
#    #---------------------------------------------------------------------------
#
#    def string_value ( self, color ):
#        """ Returns the text representation of a specified color value.
#        """
#        return str_color( color )

#-------------------------------------------------------------------------------
#  'TextColorEditor' class:
#-------------------------------------------------------------------------------

class TextColorEditor ( BaseTextEditor ):
    """ Text style of color editor, which displays a text field whose
    background color is the color value.

    FIXME: Use CSSInject Muntjac add-on to set bg color
    """

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------

#    def update_object(self):
#        """ Handles the user changing the contents of the edit control.
#        """
#        self.value = unicode(self.control.getValue())
#        set_color( self )

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

#    def update_editor ( self ):
#        """ Updates the editor when the object trait changes externally to the
#            editor.
#        """
#        super( TextColorEditor, self ).update_editor()
#        set_color( self )

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified color value:
    #---------------------------------------------------------------------------

    def string_value ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        return self.factory.str_color( color )

#-------------------------------------------------------------------------------
#  'ReadonlyColorEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyColorEditor ( BaseReadonlyEditor ):
    """ Read-only style of color editor, which displays a read-only text field
    whose background color is the color value.
    """

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

#    def init ( self, parent ):
#        """ Finishes initializing the editor by creating the underlying toolkit
#            widget.
#        """
#        self.control = QtGui.QLineEdit()
#        self.control.setReadOnly(True)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

#    def update_editor ( self ):
#        """ Updates the editor when the object trait changes externally to the
#            editor.
#        """
#        super( ReadonlyColorEditor, self ).update_editor()
#        set_color( self )

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified color value:
    #---------------------------------------------------------------------------

    def string_value ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        return self.factory.str_color( color )


# Define the SimpleEditor, CustomEditor, etc. classes which are used by the
# editor factory for the color editor.
SimpleEditor   = SimpleColorEditor
CustomEditor   = CustomColorEditor
TextEditor     = TextColorEditor
ReadonlyEditor = ReadonlyColorEditor
