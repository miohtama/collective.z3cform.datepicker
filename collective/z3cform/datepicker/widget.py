#-*- coding: utf-8 -*- 
"""

        Date + datetime selectors with jquery UI Javascript widget and many other features.

"""

__copyright__ = "2008-2009 Rok Garbas, 2009- Twinapex Research"
__authors__ = "Rok Garbas <rok.garbas@gmail.com>, Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__license__ = "GPL"

import types
        
from DateTime import DateTime
from zope.component import adapts
from zope.component import adapter
import zope.interface
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.app.form.interfaces import ConversionError
from zope.app.i18n import ZopeMessageFactory as _
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.i18n.format import DateTimeParseError
from zope.i18n.interfaces import IUserPreferredLanguages

import z3c.form
from z3c.form.browser import widget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.converter import CalendarDataConverter
from z3c.form.converter import FormatterValidationError
from z3c.form import validator

from collective.z3cform.datepicker.interfaces import IDatePickerWidget
from collective.z3cform.datepicker.interfaces import IDateTimePickerWidget
from collective.z3cform.datepicker.interfaces import IEmptyDateTimePickerWidget

class DatePickerWidget(widget.HTMLTextInputWidget, Widget):
    """ Datepicker widget. """
    implementsOnly(IDatePickerWidget)

    klass = u'datepicker-widget'
    size = 30 # we need a little bigger input box

    # 
    # for explanation how to set options look at:
    # http://docs.jquery.com/UI/Datepicker
   
    options = dict(
        # altField - we dont alow to change altField since we use it in our widget
        altFormat               = u'DD, d MM, yy',
        # appendText - we provide description different way
        beforeShow              = None,
        beforeShowDay           = None,
        buttonImage             = u'popup_calendar.gif',
        buttonImageOnly         = True,
        buttonText              = u'...',
        calculateWeek           = u'$.datepicker.iso8601Week',
        changeFirstDay          = True,
        changeMonth             = True,
        changeYear              = True,
        closeText               = u'Close',
        constrainInput          = True,
        currentText             = u'Today',
        # dateFormat - we use mm/dd/yy always
        dayNames                = ['Sunday', 'Monday', 'Tuesday', 'Wednesday',
                                   'Thursday', 'Friday', 'Saturday'],
        dayNamesMin             = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
        dayNamesShort           = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        defaultDate             = None,
        duration                = u'normal',
        firstDay                = 0,
        gotoCurrent             = False,
        hideIfNoPrevNext        = False,
        isRTL                   = False,
        maxDate                 = None,
        minDate                 = None,
        monthNames              = ['January', 'February', 'March', 'April', 'May',
                                   'June', 'July', 'August', 'September',
                                   'October', 'November', 'DecenextTextmber'],
        monthNamesShort         = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        navigationAsDateFormat  = False,
        nextText                = u'Next>',
        numberOfMonths          = 1,
        prevText                = u'<Prev',
        shortYearCutoff         = 10,
        showAnim                = u'show',
        showButtonPanel         = False,
        showOn                  = u'both',
        showOptions             = {},
        showOtherMonths         = False,
        stepMonths              = 1,
        yearRange               = u'-10:+10')

    events = dict(
        onChangeMonthYear       = None,
        onClose                 = None,
        onSelect                = None)

    @property
    def _options(self):
        return dict(
        altField   = '#'+self.id+u'-for-display',
        dateFormat = u'mm/dd/yy')

    def update(self):
        super(DatePickerWidget, self).update()
        widget.addFieldClass(self)

    @property
    def language(self):
        return IUserPreferredLanguages(self.request).getPreferredLanguages()[0]

    def compile_options(self):
        options = ''
        for name, value in self._options.items()+self.options.items():
            if value == None: value = 'null'
            elif type(value) == bool: value = str(value).lower()
            elif type(value) in [list, dict, int]: value = str(value)
            elif name in ['beforeShow','beforeShowDay','minDate','maxDate']: value = str(value)
            else: value = '"'+str(value)+'"'
            options += name+': '+str(value)+','
        for name, value in self.events.items():
            if not value: continue
            options += name+': '+str(value)+','
        return options[:-1]

    def datepicker_javascript(self):
        return '''/* <![CDATA[ */
            jq(document).ready(function(){
                datepicker = jq("#%(id)s").datepicker({%(options)s});
                jq("%(altField)s").attr("readonly", "readonly");
                jq("%(altField)s").addClass('embed');
                jq("%(altField)s").each(function() {
                    jq(this).val(jq.datepicker.formatDate("%(altFormat)s",
                        jq("#%(id)s").datepicker('getDate'),
                        {shortYearCutoff: %(shortYearCutoff)s,
                         dayNamesShort: %(dayNamesShort)s,
                         dayNames: %(dayNames)s,
                         monthNamesShort: %(monthNamesShort)s,
                         monthNames: %(monthNames)s}
                    ));
                });
                jq("#%(id)s-clear").click(function() { 
                    jq("#%(id)s").val('');
                    jq("%(altField)s").val('');
                });
            });
            /* ]]> */''' % dict(id=self.id,
                                options=self.compile_options(),
                                altField=self._options['altField'],
                                altFormat=self.options['altFormat'],
                                shortYearCutoff=self.options['shortYearCutoff'],
                                dayNamesShort=self.options['dayNamesShort'],
                                dayNames=self.options['dayNames'],
                                monthNamesShort=self.options['monthNamesShort'],
                                monthNames=self.options['monthNames'])


class PartialDate(object):
    """ Marker object for dates that user did not fill in completely """
    def __repr__(self):
        return '<PARTIAL DATE>'

# Partial date time fill in marker object
# use is to compare
PARTIAL_DATE = PartialDate()

class DateTimePickerWidget(DatePickerWidget):
    """ DateTime picker widget. 

    Uses widget instance based attributes for configuration. Default values are class attributes. 

    components attribute will tell what parts and in which order date components are presented.

    years, months, days, hours and minutes are selection lists. They will be wrapped to zope.schema.vocabulary.SimpleVocabulary if provided as plain Python lists.
    """
    implementsOnly(IDateTimePickerWidget)
   
    klass = u'datetimepicker-widget'
    value = u''
    
    years = range(1980, 2021)
    months = range(1, 13)
    days = range(1, 32)
    
    options = DatePickerWidget.options.copy()
    options.update(dict(beforeShow='readLinked',
                        yearRange=str(years[0])+':'+str(years[-1])))
    events = DatePickerWidget.events.copy()
    events.update(dict(onSelect='updateLinked'))
    _options = dict(dateFormat='mm/dd/yy')

    # All availble date compontents - don't touch
    all_components = [ "years", "days", "months", "hours", "minutes" ]

    # Which date components are asked/required
    # override this in updateWidgets() for custom behavior
    # Order is important - default to european order
    components = [ "days", "months", "years", "hours", "minutes" ]
    
    # This will be rendered between selection lists, after [key] component
    component_separators = {
            "days" : ".",
            "months" : ".",
            "hours" : ":",
            "minutes" :  "",
            "years" : ""
        }

    # This controls whether Javascript picker is enabled
    # Note that you might also want disable extra files from portal_css and portal_javascripts, see profiles/default/*.xml
    show_jquery_picker = True    

    # This present selection input value which is means "user hasn't made a choice yet"
    empty_value_marker = "-"

    @property
    def hours(self):
        hours = []
        for i in range(0, 24):
            if i<10:
                hours.append('0'+str(i))
            else:
                hours.append(str(i))
        return hours

    @property
    def minutes(self):
        minutes = []
        for i in range(0, 60, 1):
            if i<10:
                minutes.append('0'+str(i))
            else:
                minutes.append(str(i))
        return minutes

    def datepicker_javascript(self):
        return '''/* <![CDATA[ */
            jq(document).ready(function(){
                // Prepare to show a date picker linked to three select controls 
                function readLinked() { 
                    jq("#%(id)s").val(jq("#%(id)s-months").val()+'/'+
                                      jq("#%(id)s-days").val()+'/'+
                                      jq("#%(id)s-years").val()+' '+
                                      jq("#%(id)s-hours").val()+':'+
                                      jq("#%(id)s-minutes").val());
                    return {}; 
                } 
                // Update three select controls to match a date picker selection 
                function updateLinked(date) { 
                    if (date != '') {
                        var datetime = date.split(" ");
                        if (datetime.length==1) {
                            date = datetime[0].split('/');
                            if (date.length==3) {
                                jq("#%(id)s-months").val(parseInt(date[0])); 
                                jq("#%(id)s-days").val(parseInt(date[1])); 
                                jq("#%(id)s-years").val(parseInt(date[2])); 
                            }
                        }
                        if (datetime.length==2) {
                            date = datetime[0].split('/');
                            var time = datetime[1].split(':');
                            if (date.length==3&&time.length==2) {
                                jq("#%(id)s-months").val(date[0]); 
                                jq("#%(id)s-days").val(date[1]); 
                                jq("#%(id)s-years").val(date[2]); 
                                jq("#%(id)s-hours").val(time[0]); 
                                jq("#%(id)s-minutes").val(time[1]); 
                            } 
                        }
                    }
                    readLinked();
                } 
                updateLinked(jq("#%(id)s").val());
                jq("#%(id)s-years").change(readLinked);
                jq("#%(id)s-months").change(readLinked);
                jq("#%(id)s-days").change(readLinked);
                jq("#%(id)s-hours").change(readLinked);
                jq("#%(id)s-minutes").change(readLinked);

                datepicker = jq("#%(id)s").datepicker({%(options)s});
                // Prevent selection of invalid dates through the select controls 
                jq("#%(id)s-months, #%(id)s-years").change(function () { 
                    var daysInMonth = 32 - new Date(jq("#%(id)s-years").val(), 
                        jq("#%(id)s-months").val() - 1, 32).getDate(); 
                    jq("#%(id)s-days option").attr("disabled", ""); 
                    jq("#%(id)s-days option:gt(" + (daysInMonth - 1) +")").attr("disabled", "disabled"); 
                    if (jq("#%(id)s-days").val() > daysInMonth) { 
                        jq("#%(id)s-days").val(daysInMonth); 
                    } 
                });
            });
            /* ]]> */''' % dict(id=self.id,options=self.compile_options())
                    
    def get_date_component(self, comp):
        """ Get datetime component for <input> or <select> value string presentation.

        This will prefill in input fields when the form is rendered. Input source can be

                * HTTP POST postback        

                * Extract stored data (previously saved datetime object)
        
        See z3c.form.converter.CalendarDataConverter
        
        @param comp: strftime formatter symbol
        """      

        formatters = {
                "years" : "%Y",
                "months" : "%m",
                "days" : "%d",                
                "hours" : "%H",
                "minutes" : "%M",
        }

        # Check if we have HTTP POST postback value to display
        if self.get_component_input_name(comp) in self.request:
            value = self.extract_component(comp, self.empty_value_marker)
            if value != self.empty_value_marker:
                return value

        # Get stored value if we are still empty
        if self.value == u'':
            return None        
    
        # match z3c.form.converter behavior here
        locale = self.request.locale
        formatter = locale.dates.getFormatter("dateTime", "short")
               
        try:
            value = formatter.parse(self.value)
        except:
            return None
        
        # TODO: What if the strftime return value has international letters?
        formatted = value.strftime(formatters[comp])

        return unicode(formatted)
        
    def is_checked(self, component, value):
        """ Selection list helper function.
        
        Called by template.
        """
        
        current_comp_value = self.get_date_component(component)
        
        if current_comp_value == None:
            return False

        # string to string match
        if unicode(current_comp_value) == unicode(value):
            return True        

        # Hack, strip leading zero from numbers and compare numerical values
        #print "comp:" +str(component)
        #print "value:" + str(value)
        #print "current:" + str(current_comp_value)
        
        try:
            value = int(str(value))
            current_comp_value = int(str(current_comp_value))
        except ValueError:
            return False

        if unicode(current_comp_value) == unicode(value):
            return True        

    def get_selection_lists(self):
        """ Get values for all selection list to display in non-Javascript input fields.

        Called once by template.

        This allows override selections by contry specific values, like month names
        by subclassing.

        @return: Dict of component id -> SimpleVocabulary instance mappings
        """

        result = {}

        assert len(self.components) > 0, "Bad components declaration for widget:" + str(self)

        for c in self.components:
            list = getattr(self, c)

            # Turn lists to vocabulary
            if not isinstance(list, SimpleVocabulary):
               assert type(list) == types.ListType
               terms = [ SimpleTerm(val, title=val) for val in list ]
               result[c] = SimpleVocabulary(terms)
            else:
               result[c] = list

        return result

    def get_component_input_name(self, component):
        """ How datetime component selection drop down name is encoded in the form.
        
        self.name contains z3c.form decorations.
        """
        return self.name + "-" + component


    def fill_in_partial_date(self, values):
        """ Put in missing datetime components to satisfy valid datetime requirements.

        When we fill in incomplete dates, what substitute values we use for parts
        we don't want to fill in, since datetime.datetime does not support
        invalid dates (missing months, hours, etc.)

        @param components: Dict of component -> value mappings
        """
        zero_component = {
                "years" : 1900,
                "months" : 1,
                "days" : 1,
                "hours" : 0,     
                "minutes" : 0,
        }

        for c in self.all_components:
            if not c in values:
                values[c] = zero_component[c]

    def get_all_components(self):
        """ Get all available date components.

        Called by template.

        Preserve order with self.components. 
        """
        components = self.components[:]
        for a in self.all_components:
            if not a in components:
                components.append(a)
        return components

    def extract_component(self, component, default=z3c.form.interfaces.NOVALUE):
        """ Extract one component of date time from HTTP POST request.

        @return: HTTP POST component value as string or default
        """
        component_value = self.request.get(self.get_component_input_name(component), default)      
        if component_value == u"":
            # Empty <input type="text"> field
            return default
        return component_value

    
    def extract(self, default=z3c.form.interfaces.NOVALUE):
        """ Non-Javascript based value reader.
        
        Scan all selection lists and form datetime based on them.

        @return: datetime formatted string if the input is succesfully filled
        @return: PARTIAL_DATE instance if the request was partially filled
        @return: NOVALUE instance if the request does not contain data for this widget (was HTTP GET -> fill in from the data storage)        
        """
        
        values = {}
    
        # How many date components are missing (filled in with dash)
        missing_components = []
        
        for c in self.components:

            # Developer input sanity check
            if not c in self.all_components:
                raise AssertionError("Got bad components declaration:" + str(self.components))

            # Get individual selection list value          
            
            component_value = self.extract_component(c, default)
            #print "Got value "+ str(component_value) + " for " + c
            if component_value == default:
                missing_components.append(c)
            else:
                values[c] = component_value

        if len(missing_components) > 0:
            # Some fields missing
            if len(missing_components) == len(self.components):
                # This field was completely unfilled
                # z3c.form machinary assumes that we return empty string in this case
                return z3c.form.interfaces.NOVALUE
            else:
                # partially filled in
                return PARTIAL_DATE

        # Fill in day values which are missing
        self.fill_in_partial_date(values)

        # convert to datepicker internal format
        # TODO: Check this is fixed and not tied to portal_properties
        formatted = "%s/%s/%s %s:%s" % (values["months"], values["days"], values["years"], values["hours"], values["minutes"])
        #print "Got:" + formatted + " " + str(self)
        return formatted

        
class PartialDateError(zope.schema.ValidationError):
    """ Please fill in the date completely """
    
    # TODO: Docstring above is displayed to the user unless this exception is caught and localized

class EmptyDateTimePickerWidget(DateTimePickerWidget):
    """ Datetime picker widget which allows you to skip the value selection. 

    Incomplete values are marked with dash (-) in selection drop down.
    """

    implementsOnly(IEmptyDateTimePickerWidget)
   
    klass = u'optionaldatetimepicker-widget'
    value = u''
    
    
    def __init__(self, *args, **kwargs):
        DateTimePickerWidget.__init__(self, *args, **kwargs)
        #print str(args) + str(kwargs)

    def wrap_selection_list_with_no_option(self, options):
        """ Helper method to add an empty option to the selection list start.

        @param options: SimpleVocabulary instance
        """
        assert isinstance(options, SimpleVocabulary), "Got in bad options:" + str(options) + " " + str(self)
        empty_term = SimpleTerm(value=self.empty_value_marker, title=self.empty_value_marker)
        terms = [ empty_term ]
        for term in options:
            terms.append(term)

        return SimpleVocabulary(terms)
        
    def extract_component(self, component, default=z3c.form.interfaces.NOVALUE):
        """ Extract one component of date time from request.
        """
        component_value = DateTimePickerWidget.extract_component(self, component)
        if component_value == self.empty_value_marker:
            return default

        return component_value

    def get_selection_lists(self):
        """ Include "no" option in every selection list.

        """
        lists = DateTimePickerWidget.get_selection_lists(self)
        for key, value in lists.items():
            lists[key] = self.wrap_selection_list_with_no_option(value) 
        return lists

@adapter(IDatePickerWidget, IFormLayer)
@implementer(IFieldWidget)
def DatePickerFieldWidget(field, request):
   """IFieldWidget factory for DatePickerFieldWidget."""
   return FieldWidget(field, DatePickerWidget(request))

@adapter(IDateTimePickerWidget, IFormLayer)
@implementer(IFieldWidget)
def DateTimePickerFieldWidget(field, request):
   """IFieldWidget factory for DateTimePickerFieldWidget."""
   return FieldWidget(field, DateTimePickerWidget(request))

@adapter(IEmptyDateTimePickerWidget, IFormLayer)
@implementer(IFieldWidget)
def EmptyDateTimePickerFieldWidget(field, request):
   """IFieldWidget factory for EmptyDateTimePickerFieldWidget."""
   return FieldWidget(field, EmptyDateTimePickerWidget(request))


class DateTimeConverter(CalendarDataConverter):
    """A special data converter for datetimes."""

    adapts(IDatetime, IDateTimePickerWidget)
    type = 'dateTime'
    
    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        
        #print "Converting to widget value:" + str(value)
        
        if value is self.field.missing_value:
            return u''        
        
        return self.formatter.format(value)    

    def toFieldValue(self, value):
        """See interfaces.IDataConverter""" 

        if value == u'':
            return self.field.missing_value
        elif value == PARTIAL_DATE:
            # The user had filled in the date only partially
            # TODO: How to localize
            raise PartialDateError()
            
        try:
            return self.formatter.parse(value, pattern="M/d/yyyy H:m")
        except DateTimeParseError, err:
            raise FormatterValidationError(err.args[0], value)

class EmptyDateTimeConverter(DateTimeConverter):

    adapts(IDatetime, IEmptyDateTimePickerWidget)
    type = 'dateTime'


class DateConverter(CalendarDataConverter):
    """A special data converter for datetimes."""

    adapts(IDate, IDatePickerWidget)
    type = 'date'

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""

       
        if value == u'':
            return self.field.missing_value
        try:
            return self.formatter.parse(value, pattern="M/d/yyyy")
        except DateTimeParseError, err:
            raise FormatterValidationError(err.args[0], value)

