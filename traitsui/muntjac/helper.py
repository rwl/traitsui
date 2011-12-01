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

""" Defines helper functions and classes used to define Muntjac-based trait
    editors and trait editor factories.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import os.path

from muntjac.api import Button

from muntjac.ui.component import IComponent

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
