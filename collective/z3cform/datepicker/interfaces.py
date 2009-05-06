#-*- coding: utf-8 -*- 

#############################################################################
#                                                                           #
#   Copyright (c) 2008 Rok Garbas <rok.garbas@gmail.com>                    #
#                                                                           #
# This program is free software; you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation; either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################


from z3c.form.interfaces import ITextWidget


class IDatePickerWidget(ITextWidget):
    """A datepicker widget.
    """
class IDateTimePickerWidget(ITextWidget):
    """A datepicker widget.
    """

class IEmptyDateTimePickerWidget(ITextWidget):
    """ Datetime picker widget which allows you to skip the value selection.

    The initial value of this widget has no real date, but
    each component is marked with a dash. If user wishes to 
    enter a date, each component must be filled in. No component can be 
    left partially filled.

    If value is not selected the field will return z3cfield.NOVALUE
    """
    
