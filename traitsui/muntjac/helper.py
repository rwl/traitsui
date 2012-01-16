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

""" Defines helper functions and classes used to define Muntjac-based trait
    editors and trait editor factories.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import os.path

from muntjac.api \
    import Button, Window, VerticalLayout, Panel, Application

from muntjac.main import muntjac

from muntjac.ui.component \
    import IComponent

from muntjac.ui.button \
    import IClickListener

from muntjac.terminal.theme_resource \
    import ThemeResource

from traits.api \
    import Enum, CTrait, BaseTraitHandler, TraitError

from traitsui.ui_traits \
    import convert_image, SequenceTypes

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Layout orientation for a control and its associated editor
Orientation = Enum( 'horizontal', 'vertical' )

#-------------------------------------------------------------------------------
#  Convert an image file name to a cached QPixmap:
#-------------------------------------------------------------------------------

def pixmap_cache(name, path=None):
    """ Return the QPixmap corresponding to a filename. If the filename does not
        contain a path component, 'path' is used (or if 'path' is not specified,
        the local 'images' directory is used).
    """
    if name[:1] == '@':
        image = convert_image(name.replace(' ', '_').lower())
        if image is not None:
            return image.create_image()

    name_path, name = os.path.split(name)
    name = name.replace(' ', '_').lower()
    if name_path:
        filename = os.path.join(name_path, name)
    else:
        if path is None:
            filename = os.path.join(os.path.dirname(__file__), 'images', name)
        else:
            filename = os.path.join(path, name)
    filename = os.path.abspath(filename)

    pm = QtGui.QPixmap()
    if not QtGui.QPixmapCache.find(filename, pm):
        pm.load(filename)
        QtGui.QPixmapCache.insert(filename, pm)
    return pm

#-------------------------------------------------------------------------------
#  Positions a window on the screen with a specified width and height so that
#  the window completely fits on the screen if possible:
#-------------------------------------------------------------------------------

def position_window ( window, width = None, height = None, parent = None ):
    """ Positions a window on the screen with a specified width and height so
        that the window completely fits on the screen if possible.
    """
    # Get the available geometry of the screen containing the window.
    context = window.getApplication().getContext()
    webBrowser = context.getBrowser()
    screen_dx = webBrowser.getScreenWidth()
    screen_dy = webBrowser.getScreenHeight()

    # Use the frame geometry even though it is very unlikely that the X11 frame
    # exists at this point.
    width = width or window.getWidth()
    height = height or window.getHeight()

    if parent is None:
        parent = window.getParent()

    if parent is None:
        # Center the popup on the screen.
        window.center()
        return

    # Calculate the desired size of the popup control:
    if isinstance(parent, IComponent):
        x = parent.getPositionX()
        y = parent.getPositionY()
        cdx = parent.getWidth()
        cdy = parent.getHeight()

        # Get the frame height of the parent and assume that the window will
        # have a similar frame.  Note that we would really like the height of
        # just the top of the frame.
        fheight = 0
    else:
        # Special case of parent being a screen position and size tuple (used
        # to pop-up a dialog for a table cell):
        x, y, cdx, cdy = parent

        fheight = 0

    x -= (width - cdx) / 2
    y += cdy + fheight

    # Position the window (making sure it will fit on the screen).
    window.setPositionX(max(0, min(x, screen_dx - width)))
    window.setPositionY(max(0, min(y, screen_dy - height)))

#-------------------------------------------------------------------------------
#  Restores the user preference items for a specified UI:
#-------------------------------------------------------------------------------

def restore_window ( ui ):
    """ Restores the user preference items for a specified UI.
    """
    prefs = ui.restore_prefs()
    if prefs is not None:
        x, y, w, h = prefs
        ui.control.setPositionX(x)
        ui.control.setPositionY(y)
        ui.control.setWidth(w)
        ui.control.setHeight(h)

#-------------------------------------------------------------------------------
#  Saves the user preference items for a specified UI:
#-------------------------------------------------------------------------------

def save_window ( ui ):
    """ Saves the user preference items for a specified UI.
    """
    w = ui.control
    ui.save_prefs( (w.getPositionX(), w.getPositionY(),
                    w.getWidth(), w.getHeight()) )

#-------------------------------------------------------------------------------
#  Recomputes the mappings for a new set of enumeration values:
#-------------------------------------------------------------------------------

def enum_values_changed ( values ):
    """ Recomputes the mappings for a new set of enumeration values.
    """

    if isinstance( values, dict ):
        data = [ ( str( v ), n ) for n, v in values.items() ]
        if len( data ) > 0:
            data.sort( lambda x, y: cmp( x[0], y[0] ) )
            col = data[0][0].find( ':' ) + 1
            if col > 0:
                data = [ ( n[ col: ], v ) for n, v in data ]
    elif not isinstance( values, SequenceTypes ):
        handler = values
        if isinstance( handler, CTrait ):
            handler = handler.handler
        if not isinstance( handler, BaseTraitHandler ):
            raise TraitError, "Invalid value for 'values' specified"
        if handler.is_mapped:
            data = [ ( str( n ), n ) for n in handler.map.keys() ]
            data.sort( lambda x, y: cmp( x[0], y[0] ) )
        else:
            data = [ ( str( v ), v ) for v in handler.values ]
    else:
        data = [ ( str( v ), v ) for v in values ]

    names           = [ x[0] for x in data ]
    mapping         = {}
    inverse_mapping = {}
    for name, value in data:
        mapping[ name ] = value
        inverse_mapping[ value ] = name

    return ( names, mapping, inverse_mapping )

#-------------------------------------------------------------------------------
#  Safely tries to pop up an FBI window if etsdevtools.debug is installed
#-------------------------------------------------------------------------------

def open_fbi():
    try:
        from etsdevtools.developer.helper.fbi import if_fbi
        if not if_fbi():
            import traceback
            traceback.print_exc()
    except ImportError:
        pass

#-------------------------------------------------------------------------------
#  Dock-related stubs.
#-------------------------------------------------------------------------------

DockStyle = Enum('horizontal', 'vertical', 'tab', 'fixed')

#-------------------------------------------------------------------------------
#  Main window
#-------------------------------------------------------------------------------

class MainWindow(Window):

    def __init__(self, caption=''):
        super(MainWindow, self).__init__(caption, None)

        self._menuBar = Panel()
        self._toolBar = Panel()
        self._centralComponent = Panel()
        self._statusBar = Panel()

        self.addComponent(self._menuBar)
        self.addComponent(self._toolBar)
        self.addComponent(self._centralComponent)
        self.addComponent(self._statusBar)

    def setMenuBar(self, c):
        self._menuBar = c

    def getMenuBar(self):
        return self._menuBar

    def setToolBar(self, c):
        self._toolBar = c

    def getToolBar(self):
        return self._toolBar

    def setCentralComponent(self, c):
        self._centralComponent = c

    def getCentralComponent(self):
        return self._centralComponent

    def setStatusBar(self, c):
        self._statusBar = c

    def getStatusBar(self, c):
        return self._statusBar

#-------------------------------------------------------------------------------
#  Simple application
#-------------------------------------------------------------------------------

class SimpleApplication(Application, IClickListener):

    ui = None

    def init(self):
        self._mw = mw = Window()

#        ct = Button('Configure traits...', self)
#        mw.addComponent(ct)

        self.setMainWindow(self._mw)

        self.configureTraits()

    def configureTraits(self):
        self._mw.addWindow(self.ui)
        self.ui.center()

    def buttonClick(self, event):
        if self._mw.getParent() is not None:
            self.getMainWindow().showNotification('Already configuring traits')
        else:
            self.configureTraits()


class MuntjacApplication(Application):

    _hasTraits = None

#    def __init__(self, hasTraits):
#        super(MuntjacApplication, self).__init__()
#        self._hasTraits = hasTraits

    def init(self):
        self._mw = mw = Window()
        self._hasTraits.configure_traits(parent=mw)
        self.setMainWindow(self._mw)


def configure_traits(obj):

#    def app_factory():
#        app = MuntjacApplication(obj)
#        return app

    MuntjacApplication._hasTraits = obj

    muntjac(MuntjacApplication, nogui=True, debug=True)

#-------------------------------------------------------------------------------
#  Left button
#-------------------------------------------------------------------------------

class LeftButton(Button):

    def __init__(self, *args):
        super(LeftButton, self).__init__(*args)
        size = '16'
        icon = 'arrow-left.png'
        res = ThemeResource('../runo/icons/' + size + '/' + icon)
        self.setIcon(res)

#-------------------------------------------------------------------------------
#  Right button
#-------------------------------------------------------------------------------

class RightButton(Button):

    def __init__(self, *args):
        super(RightButton, self).__init__(*args)
        size = '16'
        icon = 'arrow-right.png'
        res = ThemeResource('../runo/icons/' + size + '/' + icon)
        self.setIcon(res)
