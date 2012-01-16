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

""" Defines the various range editors and the range editor factory, for the
Muntjac user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import log10

from muntjac.api \
    import HorizontalLayout, Alignment, Label, Slider, TextField

from muntjac.data.property \
    import IValueChangeListener, ValueChangeEvent

from muntjac.event.field_events \
    import BlurEvent

from muntjac.ui.button \
    import ClickEvent

from muntjac.terminal.sizeable \
    import ISizeable

from traits.api \
     import TraitError, Str, Float, Any, Bool

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.range_editor file.
from traitsui.editors.range_editor \
    import ToolkitEditorFactory

from editor_factory \
    import TextEditor

from editor \
    import Editor

from constants \
    import OKColor, ErrorColor

from helper \
    import LeftButton, RightButton

#-------------------------------------------------------------------------------
#  'BaseRangeEditor' class:
#-------------------------------------------------------------------------------

class BaseRangeEditor ( Editor ):
    """ The base class for Range editors. Using an evaluate trait, if specified,
        when assigning numbers the object trait.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Function to evaluate floats/ints
    evaluate = Any

    #---------------------------------------------------------------------------
    #  Sets the associated object trait's value:
    #---------------------------------------------------------------------------

    def _set_value ( self, value ):
        if self.evaluate is not None:
            value = self.evaluate( value )
        Editor._set_value( self, value )

#-------------------------------------------------------------------------------
#  'SimpleSliderEditor' class:
#-------------------------------------------------------------------------------

class SimpleSliderEditor ( BaseRangeEditor ):
    """ Simple style of range editor that displays a slider and a text field.

    The user can set a value either by moving the slider or by typing a value
    in the text field.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Low value for the slider range
    low = Any

    # High value for the slider range
    high = Any

    # Formatting string used to format value and labels
    format = Str

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if not factory.low_name:
            self.low = factory.low

        if not factory.high_name:
            self.high = factory.high

        self.format = factory.format

        self.evaluate = factory.evaluate
        self.sync_value( factory.evaluate_name, 'evaluate', 'from' )

        self.sync_value( factory.low_name,  'low',  'from' )
        self.sync_value( factory.high_name, 'high', 'from' )

        self.control = panel = HorizontalLayout()
        panel.setMargin(False)
        panel.setSizeUndefined()

        fvalue = self.value

        try:
            if not (self.low <= fvalue <= self.high):
                fvalue = self.low
            fvalue_text = self.format % fvalue
        except:
            fvalue_text = ''
            fvalue      = self.low

        ivalue = self._convert_to_slider(fvalue)

        self._label_lo = Label()
        if factory.label_width > 0:
            self._label_lo.setWidth(factory.label_width, 'px')
        panel.addComponent(self._label_lo)
        panel.setComponentAlignment(self._label_lo, Alignment.MIDDLE_RIGHT)

        self.control.slider = slider = Slider()
        slider.setImmediate(True)
        slider.setOrientation(Slider.ORIENTATION_HORIZONTAL)

        slider.setMin(self.low)
        slider.setMax(self.high)

        slider.setValue(ivalue)
        slider.addCallback(self.update_object_on_scroll, ValueChangeEvent)
        panel.addComponent(slider)
        panel.setComponentAlignment(slider, Alignment.MIDDLE_RIGHT)

        self._label_hi = Label()
        panel.addComponent(self._label_hi)
        panel.setComponentAlignment(self._label_hi, Alignment.MIDDLE_RIGHT)
        if factory.label_width > 0:
            self._label_hi.setWidth(factory.label_width, 'px')

        self.control.text = text = TextField()
        text.setValue( str(fvalue_text) )
        text.addCallback(self.update_object_on_enter, BlurEvent)

        # The default size is a bit too big and probably doesn't need to grow.
        z = log10( float(self.high) )
        text.setWidth(z + 1, ISizeable.UNITS_EM)

        panel.addComponent(text)

        low_label = factory.low_label
        if factory.low_name != '':
            low_label = self.format % self.low

        high_label = factory.high_label
        if factory.high_name != '':
            high_label = self.format % self.high

        self._label_lo.setValue(str(low_label))
        self._label_hi.setValue(str(high_label))

        self.set_tooltip(slider)
        self.set_tooltip(self._label_lo)
        self.set_tooltip(self._label_hi)
        self.set_tooltip(text)

    #---------------------------------------------------------------------------
    #  Handles the user changing the current slider value:
    #---------------------------------------------------------------------------

    def update_object_on_scroll ( self, event ):
        """ Handles the user changing the current slider value.
        """
        pos = event.getProperty().getValue()
        value = self._convert_from_slider(pos)
        self.control.text.setValue( str(self.format % value) )
        self.value = value

    #---------------------------------------------------------------------------
    #  Handle the user pressing the 'Enter' key in the edit control:
    #---------------------------------------------------------------------------

    def update_object_on_enter ( self, event ):
        """ Handles the user pressing the Enter key in the text field.
        """
        try:
            try:
                value = eval(unicode(self.control.text.getValue()).strip())
            except Exception:
                # The entered something that didn't eval as a number, (e.g.,
                # 'foo') pretend it didn't happen
                value = self.value
                self.control.text.setValue(str(value))

            if not self.factory.is_float:
                value = int(value)

            self.value = value
            self.control.slider.setValue(self._convert_to_slider(self.value))
        except TraitError:
            pass

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        low   = self.low
        high  = self.high
        try:
            text = self.format % value
            1 / (low <= value <= high)
        except:
            text  = ''
            value = low

        ivalue = self._convert_to_slider(value)

        self.control.text.setValue( str(text) )

#        blocked = self.control.slider.blockSignals(True)
        self.control.slider.setValue(ivalue)
#        self.control.slider.blockSignals(blocked)

    #---------------------------------------------------------------------------
    #  Returns the editor's control for indicating error status:
    #---------------------------------------------------------------------------

    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self.control.text

    #---------------------------------------------------------------------------
    #  Handles the 'low'/'high' traits being changed:
    #---------------------------------------------------------------------------

    def _low_changed ( self, low ):
        if self.value < low:
            if self.factory.is_float:
                self.value = float( low )
            else:
                self.value = int( low )

        if self.control is not None:
            self.control.slider.setMin(low)

        if self._label_lo is not None:
            self._label_lo.setValue( str(self.format % low) )
            self.update_editor()

    def _high_changed ( self, high ):
        if self.value > high:
            if self.factory.is_float:
                self.value = float( high )
            else:
                self.value = int( high )

        if self.control is not None:
            self.control.slider.setMax(high)

        if self._label_hi is not None:
            self._label_hi.setValue( str(self.format % high) )
            self.update_editor()

    def _convert_to_slider(self, value):
        """ Returns the slider setting corresponding to the user-supplied value.
        """
        if self.high > self.low:
#            ivalue = int( (float( value - self.low ) /
#                           (self.high - self.low)) * 10000.0 )
            ivalue = int(value)
        else:
            ivalue = self.low

            if ivalue is None:
                ivalue = 0

        if ivalue < self.low:
            ivalue = self.low
        elif ivalue > self.high:
            ivalue = self.high

        return ivalue

    def _convert_from_slider(self, ivalue):
        """ Returns the float or integer value corresponding to the slider
        setting.
        """
#        value = self.low + ((float( ivalue ) / 10000.0) *
#                            (self.high - self.low))
        value = ivalue
        if not self.factory.is_float:
            value = int(round(value))
        return value

#-------------------------------------------------------------------------------
class LogRangeSliderEditor ( SimpleSliderEditor ):
#-------------------------------------------------------------------------------
    """ A slider editor for log-spaced values
    """

    def _convert_to_slider(self, value):
        """ Returns the slider setting corresponding to the user-supplied value.
        """
        value = max(value, self.low)
        ivalue = int( (log10(value) - log10(self.low)) /
                      (log10(self.high) - log10(self.low)) * 10000.0)
        return ivalue

    def _convert_from_slider(self, ivalue):
        """ Returns the float or integer value corresponding to the slider
        setting.
        """
        value = float( ivalue ) / 10000.0 * (log10(self.high) -log10(self.low))
        # Do this to handle floating point errors, where fvalue may exceed
        # self.high.
        fvalue = min(self.low*10**(value), self.high)
        if not self.factory.is_float:
            fvalue = int(round(fvalue))
        return fvalue

#-------------------------------------------------------------------------------
#  'LargeRangeSliderEditor' class:
#-------------------------------------------------------------------------------

class LargeRangeSliderEditor ( BaseRangeEditor ):
    """ A slider editor for large ranges.

    The editor displays a slider and a text field. A subset of the total range
    is displayed in the slider; arrow buttons at each end of the slider let
    the user move the displayed range higher or lower.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Low value for the slider range
    low = Any(0)

    # High value for the slider range
    high = Any(1)

    # Low end of displayed range
    cur_low = Float

    # High end of displayed range
    cur_high = Float

    # Flag indicating that the UI is in the process of being updated
    ui_changing = Bool(False)

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory

        # Initialize using the factory range defaults:
        self.low = factory.low
        self.high = factory.high
        self.evaluate = factory.evaluate

        # Hook up the traits to listen to the object.
        self.sync_value( factory.low_name,  'low',  'from' )
        self.sync_value( factory.high_name, 'high', 'from' )
        self.sync_value( factory.evaluate_name, 'evaluate', 'from' )

        self.init_range()
        low  = self.cur_low
        high = self.cur_high

        self._set_format()

        self.control = panel = HorizontalLayout()
        panel.setMargin(False)

        fvalue = self.value

        try:
            fvalue_text = self._format % fvalue
            1 / (low <= fvalue <= high)
        except:
            fvalue_text = ''
            fvalue      = low

        if high > low:
            ivalue = int( (float( fvalue - low ) / (high - low)) * 10000 )
        else:
            ivalue = low

        # Lower limit label:
        self.control.label_lo = label_lo = Label()
        panel.addComponent(label_lo)
        panel.setComponentAlignment(self._label_lo, Alignment.MIDDLE_RIGHT)

        # Lower limit button:
        self.control.button_lo = LeftButton()
        self.control.button_lo.addCallback(self.reduce_range, ClickEvent)
        panel.addComponent(self.control.button_lo)

        # Slider:
        self.control.slider = slider = Slider()
        slider.setImmediate(True)
        slider.setOrientation(Slider.ORIENTATION_HORIZONTAL)

        slider.setMin(0)
        slider.setMax(10000)

        slider.setValue(ivalue)
        slider.addCallback(self.update_object_on_scroll, ValueChangeEvent)
        panel.addComponent(slider)
        panel.setComponentAlignment(slider, Alignment.MIDDLE_RIGHT)

        # Upper limit button:
        self.control.button_hi = RightButton()
        self.control.button_hi.addCallback(self.increase_range, ClickEvent)
        panel.addComponent(self.control.button_hi)
#        panel.setComponentAlignment(self.control.button_hi, Alignment.MIDDLE_RIGHT)

        # Upper limit label:
        self.control.label_hi = label_hi = Label()
        panel.addComponent(label_hi)

        # Text entry:
        self.control.text = text = TextField('', str(fvalue_text))
        text.addCallback(self.update_object_on_enter, BlurEvent)

        # The default size is a bit too big and probably doesn't need to grow.
        z = log10( float(self.high) )
        text.setWidth(z + 1, ISizeable.UNITS_EM)

        panel.addComponent(text)

        label_lo.setValue(str(low))
        label_hi.setValue(str(high))

        self.set_tooltip(slider)
        self.set_tooltip(label_lo)
        self.set_tooltip(label_hi)
        self.set_tooltip(text)

        # Update the ranges and button just in case.
        self.update_range_ui()

    #---------------------------------------------------------------------------
    #  Handles the user changing the current slider value:
    #---------------------------------------------------------------------------

    def update_object_on_scroll(self, pos):
        """ Handles the user changing the current slider value.
        """
        value = self.cur_low + ((float(pos) / 10000.0) * (self.cur_high - self.cur_low))

        self.control.text.setValue( str(self._format % value) )

        if self.factory.is_float:
            self.value = value
        else:
            self.value = int(value)

    #---------------------------------------------------------------------------
    #  Handle the user pressing the 'Enter' key in the edit control:
    #---------------------------------------------------------------------------

    def update_object_on_enter(self):
        """ Handles the user pressing the Enter key in the text field.
        """
        try:
            self.value = eval(unicode(self.control.text.text()).strip())
        except TraitError:
            pass

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        low   = self.low
        high  = self.high
        try:
            text = self._format % value
            1 / (low <= value <= high)
        except:
            value = low
        self.value = value

        if not self.ui_changing:
            self.init_range()
            self.update_range_ui()

    def update_range_ui ( self ):
        """ Updates the slider range controls.
        """
        low, high = self.cur_low, self.cur_high
        value = self.value
        self._set_format()
        self.control.label_lo.setValue( str(self._format % low) )
        self.control.label_hi.setValue( str(self._format % high) )

        if high > low:
            ivalue = int( (float( value - low ) / (high - low)) * 10000.0 )
        else:
            ivalue = low

#        blocked = self.control.slider.blockSignals(True)
        self.control.slider.setValue( ivalue )
#        self.control.slider.blockSignals(blocked)

        text = self._format % self.value
        self.control.text.setText( str(text) )
        self.control.button_lo.setEnabled(low != self.low)
        self.control.button_hi.setEnabled(high != self.high)

    def init_range ( self ):
        """ Initializes the slider range controls.
        """
        value     = self.value
        low, high = self.low, self.high
        if (high is None) and (low is not None):
            high = -low

        mag = abs( value )
        if mag <= 10.0:
            cur_low  = max( value - 10, low )
            cur_high = min( value + 10, high )
        else:
            d        = 0.5 * (10**int( log10( mag ) + 1 ))
            cur_low  = max( low,  value - d )
            cur_high = min( high, value + d )

        self.cur_low, self.cur_high = cur_low, cur_high

    def reduce_range(self):
        """ Reduces the extent of the displayed range.
        """
        low, high = self.low, self.high
        if abs( self.cur_low ) < 10:
            self.cur_low  = max( -10, low )
            self.cur_high = min( 10, high )
        elif self.cur_low > 0:
            self.cur_high = self.cur_low
            self.cur_low  = max( low, self.cur_low / 10 )
        else:
            self.cur_high = self.cur_low
            self.cur_low  = max( low, self.cur_low * 10 )

        self.ui_changing = True
        self.value       = min( max( self.value, self.cur_low ), self.cur_high )
        self.ui_changing = False
        self.update_range_ui()

    def increase_range(self):
        """ Increased the extent of the displayed range.
        """
        low, high = self.low, self.high
        if abs( self.cur_high ) < 10:
            self.cur_low  = max( -10, low )
            self.cur_high = min(  10, high )
        elif self.cur_high > 0:
            self.cur_low  = self.cur_high
            self.cur_high = min( high, self.cur_high * 10 )
        else:
            self.cur_low  = self.cur_high
            self.cur_high = min( high, self.cur_high / 10 )

        self.ui_changing = True
        self.value       = min( max( self.value, self.cur_low ), self.cur_high )
        self.ui_changing = False
        self.update_range_ui()

    def _set_format ( self ):
        self._format = '%d'
        factory      = self.factory
        low, high    = self.cur_low, self.cur_high
        diff         = high - low
        if factory.is_float:
            if diff > 99999:
                self._format = '%.2g'
            elif diff > 1:
                self._format = '%%.%df' % max( 0, 4 -
                                                  int( log10( high - low ) ) )
            else:
                self._format = '%.3f'

    #---------------------------------------------------------------------------
    #  Returns the editor's control for indicating error status:
    #---------------------------------------------------------------------------

    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self.control.text

    #---------------------------------------------------------------------------
    #  Handles the 'low'/'high' traits being changed:
    #---------------------------------------------------------------------------

    def _low_changed ( self, low ):
        if self.control is not None:
            if self.value < low:
                if self.factory.is_float:
                    self.value = float( low )
                else:
                    self.value = int( low )

            self.update_editor()

    def _high_changed ( self, high ):
        if self.control is not None:
            if self.value > high:
                if self.factory.is_float:
                    self.value = float( high )
                else:
                    self.value = int( high )

            self.update_editor()

#-------------------------------------------------------------------------------
#  'SimpleSpinEditor' class:
#-------------------------------------------------------------------------------

class SimpleSpinEditor ( BaseRangeEditor ):
    """ A simple style of range editor that displays a spin box control.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Low value for the slider range
    low = Any

    # High value for the slider range
    high = Any

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if not factory.low_name:
            self.low = factory.low

        if not factory.high_name:
            self.high = factory.high

        self.sync_value( factory.low_name,  'low',  'from' )
        self.sync_value( factory.high_name, 'high', 'from' )
        low  = self.low
        high = self.high

        from muntjac.ui.stepper.int_stepper import IntStepper
        self.control = IntStepper()
        self.control.setImmediate(True)
        self.control.setMin(low)
        self.control.setMax(high)
        self.control.setValue(self.value)
        self.control.addCallback(self.update_object, ValueChangeEvent)
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handle the user selecting a new value from the spin control:
    #---------------------------------------------------------------------------

    def update_object(self, event):
        """ Handles the user selecting a new value in the spin box.
        """
        value = event.getProperty().getValue()
        self._locked = True
        try:
            self.value = value
        finally:
            self._locked = False

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if not self._locked:
            try:
                self.control.setValue(int(self.value))
            except:
                pass

    #---------------------------------------------------------------------------
    #  Handles the 'low'/'high' traits being changed:
    #---------------------------------------------------------------------------

    def _low_changed ( self, low ):
        if self.value < low:
            if self.factory.is_float:
                self.value = float( low )
            else:
                self.value = int( low )

        if self.control:
            self.control.setMin(low)
            self.control.setValue(int(self.value))

    def _high_changed ( self, high ):
        if self.value > high:
            if self.factory.is_float:
                self.value = float( high )
            else:
                self.value = int( high )

        if self.control:
            self.control.setMax(high)
            self.control.setValue(int(self.value))

#-------------------------------------------------------------------------------
#  'RangeTextEditor' class:
#-------------------------------------------------------------------------------

class RangeTextEditor ( TextEditor ):
    """ Editor for ranges that displays a text field. If the user enters a
    value that is outside the allowed range, the background of the field
    changes color to indicate an error.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Function to evaluate floats/ints
    evaluate = Any

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        TextEditor.init( self, parent )
        self.evaluate = self.factory.evaluate
        self.sync_value( self.factory.evaluate_name, 'evaluate', 'from' )

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------

    def update_object (self):
        """ Handles the user entering input data in the edit control.
        """
        try:
            value = eval(unicode(self.control.getValue()))
            if self.evaluate is not None:
                value = self.evaluate(value)
            self.value = value
        except:
            self.control.setComponentError('invalid value')

#-------------------------------------------------------------------------------
#  'SimpleEnumEditor' factory adaptor:
#-------------------------------------------------------------------------------

def SimpleEnumEditor ( parent, factory, ui, object, name, description ):
    return CustomEnumEditor( parent, factory, ui, object, name, description,
                             'simple' )

#-------------------------------------------------------------------------------
#  'CustomEnumEditor' factory adaptor:
#-------------------------------------------------------------------------------

def CustomEnumEditor ( parent, factory, ui, object, name, description,
                       style = 'custom' ):
    """ Factory adapter that returns a enumeration editor of the specified
    style.
    """
    if factory._enum is None:
        import traitsui.editors.enum_editor as enum_editor
        factory._enum = enum_editor.ToolkitEditorFactory(
                            values = range( factory.low, factory.high + 1 ),
                            cols   = factory.cols )

    if style == 'simple':
        return factory._enum.simple_editor( ui, object, name, description,
                                            parent )

    return factory._enum.custom_editor( ui, object, name, description, parent )

#-------------------------------------------------------------------------------
#  Defines the mapping between editor factory 'mode's and Editor classes:
#-------------------------------------------------------------------------------

# Mapping between editor factory modes and simple editor classes
SimpleEditorMap = {
    'slider':  SimpleSliderEditor,
    'xslider': LargeRangeSliderEditor,
    'spinner': SimpleSpinEditor,
    'enum':    SimpleEnumEditor,
    'text':    RangeTextEditor,
    'low':     LogRangeSliderEditor
}
# Mapping between editor factory modes and custom editor classes
CustomEditorMap = {
    'slider':  SimpleSliderEditor,
    'xslider': LargeRangeSliderEditor,
    'spinner': SimpleSpinEditor,
    'enum':    CustomEnumEditor,
    'text':    RangeTextEditor,
    'low':     LogRangeSliderEditor
}
