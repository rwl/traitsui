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

""" Defines the various button editors for the Muntjac user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from muntjac.api \
    import Button, NativeButton, CheckBox, OptionGroup

from muntjac.ui.button \
    import IClickListener

from muntjac.data.property \
    import IValueChangeListener

from traits.api \
    import Unicode, List, Str, on_trait_change

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.button_editor file.
from traitsui.editors.button_editor \
    import ToolkitEditorFactory

from editor import Editor

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor, IClickListener ):
    """ Simple style editor for a button.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The button label
    label = Unicode

    # The list of items in a drop-down menu, if any
    #menu_items = List

    # The selected item in the drop-down menu.
    selected_item = Str

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        label = self.factory.label or self.item.get_label(self.ui)
        self.control = Button( str(self.string_value(label)) )
        self.sync_value(self.factory.label_value, 'label', 'from')
        self.control.addListener(self, IClickListener)
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the 'label' trait being changed:
    #---------------------------------------------------------------------------

    def _label_changed(self, label):
        self.control.setCaption( str(self.string_value(label)) )

    #---------------------------------------------------------------------------
    #  Handles the user clicking the button by setting the value on the object:
    #---------------------------------------------------------------------------

    def buttonClick(self, event):
        self.update_object()

    def update_object(self):
        """ Handles the user clicking the button by setting the factory value
            on the object.
        """
        if self.selected_item != "":
            self.value = self.selected_item
        else:
            self.value = self.factory.value

        # If there is an associated view, then display it:
        if (self.factory is not None) and (self.factory.view is not None):
            self.object.edit_traits( view   = self.factory.view,
                                     parent = self.control )

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor, IValueChangeListener ):
    """ Custom style editor for a button, which can contain an image.
    """

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # FIXME: We ignore orientation, width_padding and height_padding.

        factory = self.factory
        style = factory.style
        label = str(self.string_value(factory.label))
        image = factory.image

        if style == 'checkbox':
            self.control = CheckBox(label)
            self.control.setImmediate(True)
            self.control.addListener(self, IClickListener)
            if image is not None:
                self.control.setIcon(image.create_icon())
        elif style == 'radio':
            self.control = OptionGroup('', [label])
            self.control.setNullSelectionAllowed(True)
            self.control.setImmediate(True)
            self.control.addListener(self, IValueChangeListener)
            if image is not None:
                self.control.setItemIcon(label, image.create_icon())
        elif style == 'toolbar':
            self.control = NativeButton(label)
            self.control.addListener(self, IClickListener)
            if image is not None:
                self.control.setIcon(image.create_icon())

        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user clicking the radion button:
    #---------------------------------------------------------------------------

    def valueChange(self, event):
        self.update_object()
