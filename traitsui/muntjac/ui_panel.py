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

"""Creates a panel-based Muntjac user interface for a specified UI object.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import cgi
import re

from muntjac.api \
    import SplitPanel, Window, HorizontalLayout, VerticalLayout, Label, \
           GridLayout, Panel, TabSheet, Accordion, Button

from muntjac.ui.alignment import Alignment

from muntjac.ui.abstract_layout import AbstractLayout

from muntjac.ui.component import IComponent

from traits.api \
    import Any, Instance, Undefined

from traitsui.api \
    import Group

from traits.trait_base \
    import enumerate

from traitsui.undo \
    import UndoHistory

from traitsui.help_template \
    import help_template

from traitsui.menu \
    import UndoButton, RevertButton, HelpButton

from helper \
    import position_window

from constants \
    import screen_dx, screen_dy, WindowColor

from ui_base \
    import BasePanel

from editor \
    import Editor


#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Pattern of all digits
all_digits = re.compile(r'\d+')


#-------------------------------------------------------------------------------
#  Create the different panel-based Muntjac user interfaces.
#-------------------------------------------------------------------------------

def ui_panel(ui, parent):
    """Creates a panel-based Muntjac user interface for a specified UI object.
    """
    _ui_panel_for(ui, parent, False)


def ui_subpanel(ui, parent):
    """Creates a subpanel-based Muntjac user interface for a specified UI
       object. A subpanel does not allow control buttons (other than those
       specified in the UI object) and does not show headers for view titles.
    """
    _ui_panel_for(ui, parent, True)


def _ui_panel_for(ui, parent, is_subpanel):
    """Creates a panel-based Muntjac user interface for a specified UI object.
    """
    ui.control = control = _Panel(ui, parent, is_subpanel).control

    control.parent = parent
    control._object = ui.context.get('object')
    control._ui = ui

    try:
        ui.prepare_ui()
    except:
        control.setParent(None)
        del control
        ui.control = None
        ui.result = False
        raise

    ui.restore_prefs()
    ui.result = True


class _Panel(BasePanel):
    """Muntjac user interface panel for Traits-based user interfaces.
    """

    def __init__(self, ui, parent, is_subpanel):
        """Initialise the object.
        """
        self.ui = ui
        history = ui.history
        view = ui.view

        # Reset any existing history listeners.
        if history is not None:
            history.on_trait_change(self._on_undoable, 'undoable',
                    remove=True)
            history.on_trait_change(self._on_redoable, 'redoable',
                    remove=True)
            history.on_trait_change(self._on_revertable, 'undoable',
                    remove=True)

        # Determine if we need any buttons or an 'undo' history.
        buttons = [self.coerce_button(button) for button in view.buttons]
        nr_buttons = len(buttons)
        has_buttons = (not is_subpanel and (nr_buttons != 1 or
                                            not self.is_button(buttons[0], '')))

        if nr_buttons == 0:
            if view.undo:
                self.check_button(buttons, UndoButton)
            if view.revert:
                self.check_button(buttons, RevertButton)
            if view.help:
                self.check_button(buttons, HelpButton)

        if not is_subpanel and (history is None):
            for button in buttons:
                if (self.is_button(button, 'Undo') or
                    self.is_button(button, 'Revert')):
                    history = ui.history = UndoHistory()
                    break

        # Create the panel.
        self.control = panel(ui)

        # Suppress the title if this is a subpanel or if we think it should be
        # superceded by the title of an "outer" widget (eg. a dock widget).
        title = view.title
        if (is_subpanel or (isinstance(parent, Window) and
                            not isinstance(parent.getParent(), Window)) or
                isinstance(parent, TabSheet)):
            title = ""


        if title != "" or has_buttons:
            layout = VerticalLayout()

            # Handle any view title.
            if title != "":
                layout.addWidget(heading_text(None, text=view.title).control)

            layout.addComponent(self.control)

            self.control = layout

            # Add any buttons.
            if has_buttons:

                # Add the special function buttons
                bbox = HorizontalLayout()

                for button in buttons:
                    if self.is_button(button, 'Undo'):
                        self.undo = self.add_button(button, bbox,
                                self._on_undo, False, 'Undo')
                        self.redo = self.add_button(button, bbox,
                                self._on_redo, False, 'Redo')
                        history.on_trait_change(self._on_undoable,
                                'undoable', dispatch = 'ui')
                        history.on_trait_change(self._on_redoable,
                                'redoable', dispatch = 'ui')
                    elif self.is_button(button, 'Revert'):
                        self.revert = self.add_button(button, bbox,
                                self._on_revert, False)
                        history.on_trait_change(self._on_revertable,
                                'undoable', dispatch = 'ui')
                    elif self.is_button(button, 'Help'):
                        self.add_button(button, bbox, self._on_help)
                    elif not self.is_button(button, ''):
                        self.add_button(button, bbox)

                layout.addComponent(bbox)


def panel(ui):
    """Creates a panel-based Muntjac user interface for a specified UI object.
       This function does not modify the UI object passed to it.  The object
       returned may be either a component or None.
    """
    # Bind the context values to the 'info' object:
    ui.info.bind_context()

    # Get the content that will be displayed in the user interface:
    content = ui._groups
    nr_groups = len(content)

    if nr_groups == 0:
        panel = None
    if nr_groups == 1:
        panel = _GroupPanel(content[0], ui).control
    elif nr_groups > 1:
        panel = TabSheet()
        _fill_panel(panel, content, ui)
        panel.ui = ui

    # If the UI is scrollable then wrap the panel in a Panel.
    if ui.scrollable and panel is not None:
        sa = Panel()
        sa.addComponent(panel)
#        sa.getParent().setResizable(True)
        panel = sa

    return panel


def _fill_panel(panel, content, ui, item_handler=None):
    """Fill a page based container panel with content.
    """
    active = 0

    for index, item in enumerate(content):
        page_name = item.get_label(ui)
        if page_name == "":
            page_name = "Page %d" % index

        if isinstance(item, Group):
            if item.selected:
                active = index

            gp = _GroupPanel(item, ui, suppress_label=True)
            page = gp.control
            sub_page = gp.sub_control

            # If the result is a TabSheet type with only one page, collapse it
            # down into just the page.
            if (isinstance(sub_page, TabSheet)
                    and sub_page.getComponentCount() == 1):
                sub_page = sub_page.getTab(0).getComponent()
            else:
                new = page
        else:
            new = VerticalLayout()
            new.setMargin(False)
            item_handler(item, new)

        # Add the content.
        if isinstance(panel, TabSheet):
            panel.addTab(new, page_name)
        else:
            panel.addComponent(new, page_name)

    panel.setSelectedTab(panel.getTab(active))


def _size_hint_wrapper(f, ui):
    """Wrap an existing sizeHint method with sizes from a UI object.
    """
    def sizeHint():
        size = f()
        if ui.view.width > 0:
            size.setWidth(ui.view.width)
        if ui.view.height > 0:
            size.setHeight(ui.view.height)
        return size
    return sizeHint

#-------------------------------------------------------------------------------
#  Displays a help window for the specified UI's active Group:
#-------------------------------------------------------------------------------

def show_help ( ui, button ):
    """ Displays a help window for the specified UI's active Group.
    """
    group    = ui._groups[ ui._active_group ]
    template = help_template()
    if group.help != '':
        header = template.group_help % cgi.escape( group.help )
    else:
        header = template.no_group_help
    fields = []
    for item in group.get_content( False ):
        if not item.is_spacer():
            fields.append( template.item_help % (
                           cgi.escape( item.get_label( ui ) ),
                           cgi.escape( item.get_help( ui ) ) ) )
    html = template.group_html % ( header, '\n'.join( fields ) )
    HTMLHelpWindow( button, html, .25, .33 )

#-------------------------------------------------------------------------------
#  Displays a pop-up help window for a single trait:
#-------------------------------------------------------------------------------

def show_help_popup ( event ):
    """ Displays a pop-up help window for a single trait.
    """
    control  = event.GetEventObject()
    template = help_template()

    # Note: The following check is necessary because under Linux, we get back
    # a control which does not have the 'help' trait defined (it is the parent
    # of the object with the 'help' trait):
    _help = getattr( control, 'help', None )
    if _help is not None:
        html = template.item_html % ( control.GetLabel(), _help )
        HTMLHelpWindow( control, html, .25, .13 )


class _GroupSplitter(SplitPanel):
    """ A splitter for a Traits UI Group with layout='split'.
    """

    def __init__(self, group):
        """ Store the group.
        """
        super(SplitPanel, self).__init__()
        self._group = group
        self._initialized = False

#    def resizeEvent(self, event):
#        """ Overridden to position the splitter based on the Group when the
#            application is initializing.
#
#            Because the splitter layout algorithm requires that the available
#            space be known, we have to wait until the UI that contains this
#            splitter gives it its initial size.
#        """
#        QtGui.QSplitter.resizeEvent(self, event)
#
#        parent = self.parent()
#        if (not self._initialized and parent and
#            (self.isVisible() or isinstance(parent, QtGui.QMainWindow))):
#            self._initialized = True
#            self._resize_items()

#    def _resize_items(self):
#        """ Size the splitter based on the 'width' or 'height' attributes
#            of the Traits UI view elements.
#        """
#        use_widths = self.getOrientation() == SplitPanel.ORIENTATION_HORIZONTAL
#
#        # Get the requested size for the items.
#        sizes = []
#        for item in self._group.content:
#            if use_widths:
#                sizes.append(item.width)
#            else:
#                sizes.append(item.height)
#
#        # Find out how much space is available.
#        if use_widths:
#            total = self.getWidth()
#        else:
#            total = self.getHeight()
#
#        # Allocate requested space.
#        avail = total
#        remain = 0
#        for i, sz in enumerate(sizes):
#            if avail <= 0:
#                break
#
#            if sz >= 0:
#                if sz >= 1:
#                    sz = min(sz, avail)
#                else:
#                    sz *= total
#
#                sz = int(sz)
#                sizes[i] = sz
#                avail -= sz
#            else:
#                remain += 1
#
#        # Allocate the remainder to those parts that didn't request a width.
#        if remain > 0:
#            remain = int(avail / remain)
#
#            for i, sz in enumerate(sizes):
#                if sz < 0:
#                    sizes[i] = remain
#
#        # If all requested a width, allocate the remainder to the last item.
#        else:
#            sizes[-1] += avail
#
#        self.setSizes(sizes)


class _GroupPanel(object):
    """A sub-panel for a single group of items. It may be either a layout or a
       widget.
    """

    def __init__(self, group, ui, suppress_label=False):
        """Initialise the object.
        """
        # Get the contents of the group:
        content = group.get_content()

        # Save these for other methods.
        self.group = group
        self.ui = ui

        if group.orientation == 'horizontal':
            self.horizontal = True
        else:
            self.horizontal = False

        # outer is the top-level widget or layout that will eventually be
        # returned.  sub is the TabSheet or Accordion corresponding to any
        # 'tabbed' or 'fold' layout.  It is only used to collapse nested
        # widgets.  inner is the object (not necessarily a layout) that new
        # controls should be added to.
        outer = sub = inner = None

        # Get the group label.
        if suppress_label:
            label = ""
        else:
            label = group.label

        # Create a border if requested.
        if group.show_border:
            outer = Panel(label)
            if self.horizontal:
                inner = HorizontalLayout()
            else:
                inner = VerticalLayout()
            inner.setSizeUndefined()
            inner.addComponent(outer)

        elif label != "":
            if self.horizontal:
                outer = inner = HorizontalLayout()
            else:
                outer = inner = VerticalLayout()
            inner.setSizeUndefined()
            inner.addComponent(heading_text(None, text=label).control)

        # Add the layout specific content.
        if len(content) == 0:
            pass

        elif group.layout == 'flow':
            raise NotImplementedError, "the 'flow' layout isn't implemented"

        elif group.layout == 'split':
            # Create the splitter.
            splitter = _GroupSplitter(group)
            if self.horizontal:
                splitter.setOrientation(SplitPanel.ORIENTATION_HORIZONTAL)
            else:
                splitter.setOrientation(SplitPanel.ORIENTATION_VERTICAL)

            if outer is None:
                outer = splitter
            else:
                inner.addComponent(splitter)

            # Create an editor.
            editor = SplitterGroupEditor(control=outer, splitter=splitter,
                    ui=ui)
            self._setup_editor(group, editor)

            self._add_splitter_items(content, splitter)

        elif group.layout in ('tabbed', 'fold'):
            # Create the TabSheet or Accordion.
            if group.layout == 'tabbed':
                sub = TabSheet()
            else:
                sub = Accordion()

            _fill_panel(sub, content, self.ui, self._add_page_item)

            if outer is None:
                outer = sub
            else:
                inner.addComponent(sub)

            # Create an editor.
            editor = TabbedFoldGroupEditor(container=sub, control=outer, ui=ui)
            self._setup_editor(group, editor)

        else:
            # See if we need to control the visual appearence of the group.
            if group.visible_when != '' or group.enabled_when != '':
                # Make sure that outer is a widget or a layout.
                if outer is None:
                    outer = inner = HorizontalLayout()
                    outer.setSizeUndefined()

                # Create an editor.
                self._setup_editor(group, GroupEditor(control=outer))

            if isinstance(content[0], Group):
                layout = self._add_groups(content, inner)
            else:
                layout = self._add_items(content, inner)

#            for c in layout.getComponentIterator():
#                layout.setComponentAlignment(c, Alignment.TOP_LEFT)

            if outer is None:
                outer = layout
            elif layout is not inner:
                inner.addComponent(layout)

        # Publish the top-level widget, layout or None.
        self.control = outer

        # Publish the optional sub-control.
        self.sub_control = sub

    def _add_splitter_items(self, content, splitter):
        """Adds a set of groups or items separated by splitter bars.
        """
        for item in content:

            # Get a panel for the Item or Group.
            if isinstance(item, Group):
                panel = _GroupPanel(item, self.ui, suppress_label=True).control
            else:
                panel = self._add_items([item])

            # Add the panel to the splitter.
            if panel is not None:
                layout = panel.getParent()
                if layout is not None:
                    for c in layout.getComponentIterator():
                        layout.setComponentAlignment(c, Alignment.TOP_LEFT)

                splitter.addComponent(panel)

    def _setup_editor(self, group, editor):
        """Setup the editor for a group.
        """
        if group.id != '':
            self.ui.info.bind(group.id, editor)

        if group.visible_when != '':
            self.ui.add_visible(group.visible_when, editor)

        if group.enabled_when != '':
            self.ui.add_enabled(group.enabled_when, editor)

    def _add_page_item(self, item, layout):
        """Adds a single Item to a page based panel.
        """
        self._add_items([item], layout)

    def _add_groups(self, content, outer):
        """Adds a list of Group objects to the panel, creating a layout if
           needed.  Return the outermost layout.
        """
        # Use the existing layout if there is one.
        if outer is None:
            if self.horizontal:
                outer = HorizontalLayout()
            else:
                outer = VerticalLayout()

            outer.setSizeUndefined()

        # Process each group.
        for subgroup in content:
            panel = _GroupPanel(subgroup, self.ui).control

            if isinstance(panel, IComponent):
                outer.addComponent(panel)
            else:
                # The sub-group is empty which seems to be used as a way of
                # providing some whitespace.
                outer.addComponent(Label(' '))

        return outer

    def _add_items(self, content, outer=None):
        """Adds a list of Item objects, creating a layout if needed.  Return
           the outermost layout.
        """
        # Get local references to various objects we need:
        ui = self.ui
        info = ui.info
        handler = ui.handler

        group = self.group
        show_left = group.show_left
        padding = group.padding
        columns = group.columns

        # See if a label is needed.
        show_labels = False
        for item in content:
            show_labels |= item.show_label

        # See if a grid layout is needed.
        if show_labels or columns > 1:
            inner = GridLayout(columns * 2, len(content))
            inner.setSpacing(True)
            inner.setSizeUndefined()

            if outer is None:
                outer = inner
            else:
                outer.addComponent(inner)

            row = 0
            if show_left:
                label_alignment = Alignment.MIDDLE_RIGHT
            else:
                label_alignment = Alignment.MIDDLE_LEFT

        else:
            # Use the existing layout if there is one.
            if outer is None:
                if self.horizontal:
                    outer = HorizontalLayout()
                else:
                    outer = VerticalLayout()
                outer.setSizeUndefined()

            inner = outer

            row = -1
            label_alignment = 0

        # Process each Item in the list:
        col = -1
        for item in content:

            # Keep a track of the current logical row and column unless the
            # layout is not a grid.
            col += 1
            if row >= 0 and col >= columns:
                col = 0
                row += 1

            # Get the name in order to determine its type:
            name = item.name

            # Check if is a label:
            if name == '':
                label = item.label
                if label != "":

                    # Create the label widget.
                    if item.style == 'simple':
                        label = Label(label)
                    else:
                        label = heading_text(None, text=label).control

                    self._add_widget(inner, label, row, col, show_labels)

                    if item.emphasized:
                        self._add_emphasis(label)

                # Continue on to the next Item in the list:
                continue

            # Check if it is a separator:
            if name == '_':
                cols = columns

                # See if the layout is a grid.
                if row >= 0:
                    # Move to the start of the next row if necessary.
                    if col > 0:
                        col = 0
                        row += 1

#                    # Skip the row we are about to do.
#                    row += 1

                    # Allow for the columns.
                    if show_labels:
                        cols *= 2

                for i in range(cols):
                    if self.horizontal:
                        # Add a vertical separator:
                        line = Panel()
                        line.setWidth('2px')
                        line.setHeight('-1px')
                        if row < 0:
                            inner.addComponent(line)
                        else:
                            inner.addComponent(line, row, i)
                    else:
                        # Add a horizontal separator:
                        line = Label('<hr />', Label.CONTENT_XHTML)
                        line.setWidth('100%')  # FIXME: explicit container size
                        if row < 0:
                            inner.addComponent(line)
                        else:
                            inner.addComponent(line, i, row)

                # Continue on to the next Item in the list:
                continue

            # Convert a blank to a 5 pixel spacer:
            if name == ' ':
                name = '5'

            # Check if it is a spacer:
            if all_digits.match( name ):

                # If so, add the appropriate amount of space to the layout:
                spacer = Label('')
                if self.horizontal:
                    # Add a horizontal spacer:
                    spacer.setWidth(name + 'px')
                else:
                    # Add a vertical spacer:
                    spacer.setHeight(name + 'px')

                self._add_widget(inner, spacer, row, col, show_labels)

                # Continue on to the next Item in the list:
                continue

            # Otherwise, it must be a trait Item:
            object      = eval( item.object_, globals(), ui.context )
            trait       = object.base_trait( name )
            desc        = trait.desc or ''
            fixed_width = False

            # Handle any label.
            if item.show_label:
                label = self._create_label(item, ui, desc)
                self._add_widget(inner, label, row, col, show_labels,
                                 label_alignment)
            else:
                label = None

            # Get the editor factory associated with the Item:
            editor_factory = item.editor
            if editor_factory is None:
                editor_factory = trait.get_editor()

                # If still no editor factory found, use a default text editor:
                if editor_factory is None:
                    from text_editor import ToolkitEditorFactory
                    editor_factory = ToolkitEditorFactory()

                # If the item has formatting traits set them in the editor
                # factory:
                if item.format_func is not None:
                    editor_factory.format_func = item.format_func

                if item.format_str != '':
                    editor_factory.format_str = item.format_str

                # If the item has an invalid state extended trait name, set it
                # in the editor factory:
                if item.invalid != '':
                    editor_factory.invalid = item.invalid

            # Create the requested type of editor from the editor factory:
            factory_method = getattr( editor_factory, item.style + '_editor' )
            editor         = factory_method( ui, object, name, item.tooltip,
                                        None).set(
                                 item        = item,
                                 object_name = item.object )

            # Tell the editor to actually build the editing widget.  Note that
            # "inner" is a layout.  This shouldn't matter as individual editors
            # shouldn't be using it as a parent anyway.  The important thing is
            # that it is not None (otherwise the main TraitsUI code can change
            # the "kind" of the created UI object).
            editor.prepare(inner)
            control = editor.control

            # Set the initial 'enabled' state of the editor from the factory:
            editor.enabled = editor_factory.enabled

            # Add emphasis to the editor control if requested:
            if item.emphasized:
                self._add_emphasis(control)

            # Give the editor focus if it requested it:
            if item.has_focus:
                control.focus()

            # Set the correct size on the control, as specified by the user:
            stretch = 0
            scrollable = editor.scrollable
            item_width = item.width
            item_height = item.height
            if (item_width != -1) or (item_height != -1):
                is_horizontal = self.horizontal

                min_size = control.minimumSizeHint()
                width = min_size.width()
                height = min_size.height()

                if (0.0 < item_width <= 1.0) and is_horizontal:
                    stretch = int(100 * item_width)

                item_width = int(item_width)
                if item_width < -1:
                    item_width  = -item_width
                else:
                    item_width = max(item_width, width)

                if (0.0 < item_height <= 1.0) and (not is_horizontal):
                    stretch = int(100 * item_height)

                item_height = int(item_height)
                if item_height < -1:
                    item_height = -item_height
                else:
                    item_height = max(item_height, height)

                control.setWidth(max(item_width, 0))
                control.setHeight(max(item_height, 0))

            # Bind the editor into the UIInfo object name space so it can be
            # referred to by a Handler while the user interface is active:
            Id = item.id or name
            info.bind( Id, editor, item.id )

            # Also, add the editors to the list of editors used to construct
            # the user interface:
            ui._editors.append( editor )

            # If the handler wants to be notified when the editor is created,
            # add it to the list of methods to be called when the UI is
            # complete:
            defined = getattr( handler, Id + '_defined', None )
            if defined is not None:
                ui.add_defined( defined )

            # If the editor is conditionally visible, add the visibility
            # 'expression' and the editor to the UI object's list of monitored
            # objects:
            if item.visible_when != '':
                ui.add_visible( item.visible_when, editor )

            # If the editor is conditionally enabled, add the enabling
            # 'expression' and the editor to the UI object's list of monitored
            # objects:
            if item.enabled_when != '':
                ui.add_enabled( item.enabled_when, editor )

            # Add the created editor control to the layout with the appropriate
            # size and stretch policies:
            ui._scrollable |= scrollable
#            item_resizable  = ((item.resizable is True) or
#                               ((item.resizable is Undefined) and scrollable))
#            if item_resizable:
#                stretch = stretch or 50
#                self.resizable = True
#            elif item.springy:
#                stretch = stretch or 50
#            policy = control.sizePolicy()
#            if self.horizontal:
#                policy.setHorizontalStretch(stretch)
#                if item_resizable or item.springy:
#                    policy.setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
#            else:
#                policy.setVerticalStretch(stretch)
#                if item_resizable or item.springy:
#                    policy.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
#            control.setSizePolicy(policy)

            # FIXME: Need to decide what to do about border_size and padding
            self._add_widget(inner, control, row, col, show_labels)

            # Save the reference to the label control (if any) in the editor:
            editor.label_control = label

        return outer

    def _add_widget(self, layout, w, row, column, show_labels,
                    label_alignment=None):
        """Adds a widget to a layout taking into account the orientation and
           the position of any labels.
        """
        # If the widget really is a widget then remove any margin so that it
        # fills the cell.
        if not isinstance(w, AbstractLayout):
            wl = w.getParent()
            if wl is not None:
                wl.setMargin(False)

        # See if the layout is a grid.
        if row < 0:
            layout.addComponent(w)

        else:
            if self.horizontal:
                # Flip the row and column.
                row, column = column, row

            if show_labels:
                # Convert the "logical" column to a "physical" one.
                column *= 2

                # Determine whether to place widget on left or right of
                # "logical" column.
                if (label_alignment is not None and not self.group.show_left) or \
                   (label_alignment is None and self.group.show_left):
                    column += 1

            layout.addComponent(w, column, row)
            if label_alignment is not None:
                layout.setComponentAlignment(w, label_alignment)


    def _create_label(self, item, ui, desc, suffix = ':'):
        """Creates an item label.
        """
        label = item.get_label(ui)
        if (label == '') or (label[-1:] in '?=:;,.<>/\\"\'-+#|'):
            suffix = ''

        control = Label(label + suffix)
        control.setSizeUndefined()

        if item.emphasized:
            self._add_emphasis(control)

        # FIXME: Decide what to do about the help.
        control.help = item.get_help(ui)

        return control

    def _add_emphasis(self, control):
        """Adds emphasis to a specified control's font.
        """
        control.addStyleName('emph')


class GroupEditor(Editor):
    """ A pseudo-editor that allows a group to be managed.
    """

    def __init__(self, **traits):
        """ Initialise the object.
        """
        self.set(**traits)


class SplitterGroupEditor(GroupEditor):
    """ A pseudo-editor that allows a group with a 'split' layout to be managed.
    """

    # The SplitPanel for the group
    splitter = Instance(_GroupSplitter)

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs(self, prefs):
        """ Restores any saved user preference information associated with the
            editor.
        """
        if isinstance(prefs, dict):
            structure = prefs.get('structure')
        else:
            structure = prefs

        self.splitter.setSplitPosition(structure)

    def save_prefs(self):
        """ Returns any user preference information associated with the editor.
        """
        return { 'structure': str(self.splitter.getSplitPosition()) }


class TabbedFoldGroupEditor(GroupEditor):
    """ A pseudo-editor that allows a group with a 'tabbed' or 'fold' layout to
        be managed.
    """

    # The TabSheet or Accordion for the group
    container = Any

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs(self, prefs):
        """ Restores any saved user preference information associated with the
            editor.
        """
        if isinstance(prefs, dict):
            current_index = prefs.get('current_index')
        else:
            current_index = prefs

        tab = self.container.getSelectedTab( int(current_index) )
        self.container.setSelectedTab(tab)

    def save_prefs(self):
        """ Returns any user preference information associated with the editor.
        """
        tab = self.container.getSelectedTab()
        return { 'current_index': str(self.container.getTabPosition(tab)) }


#-------------------------------------------------------------------------------
#  'HTMLHelpWindow' class:
#-------------------------------------------------------------------------------

class HTMLHelpWindow ( Window ):
    """ Window for displaying Traits-based help text with HTML formatting.
    """

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, parent, html, scale_dx, scale_dy ):
        """ Initializes the object.
        """
        super(HTMLHelpWindow, self).__init__()
        self.setParent(parent)

        layout = VerticalLayout()
        layout.setMargin(False)

        # Create the html control
        html_control = Label(html)
        html_control.setContentMode(Label.CONTENT_XHTML)
        layout.addComponent(html_control)

        # Create the OK button
        ok = Button('OK')
        # FIXME: add event handler
        layout.addComponent(ok)
        layout.setComponentAlignment(ok, Alignment.BOTTOM_RIGHT)

        # Position and show the dialog
        position_window(self, parent=parent)
        self.show()

#-------------------------------------------------------------------------------
#  Creates a PyFace HeadingText control:
#-------------------------------------------------------------------------------

HeadingText = None

def heading_text(*args, **kw):
    """Create a PyFace HeadingText control.
    """
    global HeadingText

    if HeadingText is None:
        from pyface.ui.muntjac.heading_text import HeadingText

    return HeadingText(*args, **kw)
