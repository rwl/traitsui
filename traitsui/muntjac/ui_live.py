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

"""Creates a Muntjac user interface for a specified UI object, where the UI is
   "live", meaning that it immediately updates its underlying object(s).
"""

from muntjac.api import HorizontalLayout

from traitsui.undo \
    import UndoHistory

from traitsui.menu \
    import UndoButton, RevertButton, OKButton, CancelButton, HelpButton

from ui_base \
    import BaseDialog

from ui_panel \
    import panel


#-------------------------------------------------------------------------------
#  Create the different 'live update' PyQt user interfaces.
#-------------------------------------------------------------------------------

def ui_live(ui, parent):
    """Creates a live, non-modal PyQt user interface for a specified UI object.
    """
    _ui_dialog(ui, parent, BaseDialog.NONMODAL)

def ui_livemodal(ui, parent):
    """Creates a live, modal PyQt user interface for a specified UI object.
    """
    _ui_dialog(ui, parent, BaseDialog.MODAL)

def ui_popup(ui, parent):
    """Creates a live, modal popup PyQt user interface for a specified UI
       object.
    """
    _ui_dialog(ui, parent, BaseDialog.POPUP)


def _ui_dialog(ui, parent, style):
    """Creates a live Muntjac user interface for a specified UI object.
    """
    if ui.owner is None:
        ui.owner = _LiveWindow()

    BaseDialog.display_ui(ui, parent, style)


class _LiveWindow(BaseDialog):
    """User interface window that immediately updates its underlying object(s).
    """

    def init(self, ui, parent, style):
        """Initialise the object.

           FIXME: Note that we treat MODAL and POPUP as equivalent until we
           have an example that demonstrates how POPUP is supposed to work.
        """
        self.ui = ui
        self.control = ui.control
        view = ui.view
        history = ui.history

        if self.control is not None:
            if history is not None:
                history.on_trait_change(self._on_undoable, 'undoable',
                        remove=True)
                history.on_trait_change(self._on_redoable, 'redoable',
                        remove=True)
                history.on_trait_change(self._on_revertable, 'undoable',
                        remove=True)

            ui.reset()
        else:
            self.create_dialog(parent, style)

        self.set_icon(view.icon)

        # Convert the buttons to actions.
        buttons = [self.coerce_button(button) for button in view.buttons]
        nr_buttons = len(buttons)

        no_buttons = ((nr_buttons == 1) and self.is_button(buttons[0], ''))

        has_buttons = ((not no_buttons) and ((nr_buttons > 0) or view.undo or
                view.revert or view.ok or view.cancel))

        if has_buttons or (view.menubar is not None):
            if history is None:
                history = UndoHistory()
        else:
            history = None

        ui.history = history

        if (not no_buttons) and (has_buttons or view.help):
            bbox = HorizontalLayout()
            bbox.setSpacing(True)

            # Create the necessary special function buttons.
            if nr_buttons == 0:
                if view.undo:
                    self.check_button(buttons, UndoButton)
                if view.revert:
                    self.check_button(buttons, RevertButton)
                if view.ok:
                    self.check_button(buttons, OKButton)
                if view.cancel:
                    self.check_button(buttons, CancelButton)
                if view.help:
                    self.check_button(buttons, HelpButton)

            for raw_button, button in zip(view.buttons, buttons):
                default = raw_button == view.default_button

                if self.is_button(button, 'Undo'):
                    self.undo = self.add_button(button, bbox,
                            self._on_undo, False, default=default)
                    history.on_trait_change(self._on_undoable, 'undoable',
                            dispatch='ui')
                    if history.can_undo:
                        self._on_undoable(True)

                    self.redo = self.add_button(button, bbox,
                            self._on_redo, False, 'Redo')
                    history.on_trait_change(self._on_redoable, 'redoable',
                            dispatch='ui')
                    if history.can_redo:
                        self._on_redoable(True)

                elif self.is_button(button, 'Revert'):
                    self.revert = self.add_button(button, bbox,
                            self._on_revert, False, default=default)
                    history.on_trait_change(self._on_revertable, 'undoable',
                            dispatch='ui')
                    if history.can_undo:
                        self._on_revertable(True)

                elif self.is_button(button, 'OK'):
                    self.ok = self.add_button(button, bbox,
                            self._on_ok, default=default)
                    ui.on_trait_change(self._on_error, 'errors', dispatch='ui')

                elif self.is_button(button, 'Cancel'):
                    self.add_button(button, bbox,
                            self._on_cancel, default=default)

                elif self.is_button(button, 'Help'):
                    self.add_button(button, bbox,
                            self._on_help, default=default)

                elif not self.is_button(button, ''):
                    self.add_button(button, bbox, default=default)

        else:
            bbox = None

        self.add_contents(panel(ui), bbox)

    def close(self, rc=True):
        """Close the dialog and set the given return code.
        """
        super(_LiveWindow, self).close(rc)

        self.undo = self.redo = self.revert = None

    def _on_finished(self, result):
        """Handles the user finishing with the dialog.
        """
        accept = bool(result)

        if not accept and self.ui.history is not None:
            self._on_revert()

        self.close(accept)

    #---------------------------------------------------------------------------
    #  Handles the user clicking the 'OK' button:
    #---------------------------------------------------------------------------

    def _on_ok ( self, event = None ):
        """ Handles the user clicking the **OK** button.
        """
        if self.ui.handler.close( self.ui.info, True ):
            self.close()
            return True

        return False

    #---------------------------------------------------------------------------
    #  Handles the user clicking the 'Cancel' button:
    #---------------------------------------------------------------------------

    def _on_cancel ( self, event = None ):
        """ Handles the user clicking the **Cancel** button.
        """
        self.close(False)
