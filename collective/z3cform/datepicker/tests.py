
# Python imports
import datetime

# Zope 3 imports
from zope.interface import Interface
from zope.schema import Date
from zope.schema import Datetime
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.component import adapts
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.i18n.locales import locales
from zope.app.pagetemplate import ViewPageTemplateFile

# Plone imports
from Products.statusmessages.interfaces import IStatusMessage

# z3c.form imports
from z3c.form.form import Form
from z3c.form.field import Fields
from z3c.form.button import buttonAndHandler
from z3c.form.interfaces import INPUT_MODE
from z3c.form.widget import FieldWidget
from plone.app.z3cform.layout import wrap_form

# Our imports
from collective.z3cform.datepicker.interfaces import IDateTimePickerWidget
from collective.z3cform.datepicker.widget import DatePickerFieldWidget
from collective.z3cform.datepicker.widget import DateTimePickerWidget, DateTimePickerFieldWidget
from collective.z3cform.datepicker.widget import EmptyDateTimePickerFieldWidget



class ITestForm(Interface):
    """ Simple test form.

    zope.schema package is used to define the data model of the form.

    Note distinction between Date and Datetime objects.
    """
    date = Date(
        title       = u'Date widget',
        required    = False,)

    datetime = Datetime(
        title       = u'DateTime widget',
        required    = True,)

    datetime2 = Datetime(
        title       = u'DateTime widget with special year range',
        required    = True,)

    optional_datetime = Datetime(
        title       = u'Optional date time field',
        required    = False,)

    required_datetime = Datetime(
        title       = u'Required date time field which must be filled in completely',
        required    = True,)

    custom_datetime = Datetime(
        title       = u'Customized date time input',
        required    = False,)

    custom_datetime2 = Datetime(
        title       = u'Custom date time input with new template and features',
        required    = False,)

    year_month = Datetime(
        title       = u'Only year and month needed for this datetime',
        required    = True,)

    american_date = Datetime(
        title       = u'American date sample format',
        required    = False,)


class CustomDateTimeWidget(DateTimePickerWidget):
    """ Example how to subclass DateTimeWidget propperly """
   
    @property
    def minutes(self):
        """ We use odd list of minutes. 

        We override a parent class property here.
        """
        return [ "13", "26", "55" ]

    @property
    def months(self):
        """ Override selection list drop down to return month names instead of numerical values. 
        
        We have also fixed template accordingly, see 
        """
        
        terms = []
        
        # self.language is two letter language-country code
        # extract language part        
        lang = self.language.split("-")[0]

        locale = locales.getLocale(lang, None, None) # see zope.i18n.locales.__init__

        month_names = locale.dates.calendars[u"gregorian"].months   
        # Construct zope.schema.Vocabulary run-time for the selected language
        for i in range(1, 12+1): # range is exclusive
            long_name, short_name = month_names[i]
            term = SimpleTerm(i, title=long_name)
            terms.append(term)

        vocab = SimpleVocabulary(terms)

        return vocab


def CustomDateTimePickerFieldWidgetFactory(field, request):
   """ All widgets are created by WidgetFactory.

   This creates widget instance and wraps it to FieldWidget.

   TODO: I am not quite sure what those magic decorators do...
   """
   return FieldWidget(field, CustomDateTimeWidget(request))
    
class CustomDateTimeWidgetWithTemplate(DateTimePickerWidget):
    """ Widget whose template has been overridden. 

    Template uses <input type="text"> instead of <select>
    """
  
    template = ViewPageTemplateFile("test_datetimepicker_input.pt")

    components = [ "months", "days", "years", "hours", "minutes" ]
    component_separators={"months":"/", "days" : "/", "hours" : ":" }

def CustomDateTimeWidgetWithTemplateFieldWidgetFactory(field, request):
   """ Maybe we are stretching function name here a bit """
   return FieldWidget(field, CustomDateTimeWidgetWithTemplate(request))
                            
class TestForm(Form):
    """ Sample test form mapped to http://yoursite/@@datepicker_test. 

    Show how to bind fields to widget factories.
    """

    ignoreContext = True
    fields = Fields(ITestForm)
    fields['date'].widgetFactory[INPUT_MODE] = DatePickerFieldWidget
    fields['datetime'].widgetFactory[INPUT_MODE] = DateTimePickerFieldWidget
    fields['datetime2'].widgetFactory[INPUT_MODE] = DateTimePickerFieldWidget
    fields['optional_datetime'].widgetFactory[INPUT_MODE] = EmptyDateTimePickerFieldWidget
    fields['required_datetime'].widgetFactory[INPUT_MODE] = EmptyDateTimePickerFieldWidget
    fields['year_month'].widgetFactory[INPUT_MODE] = EmptyDateTimePickerFieldWidget
    fields['american_date'].widgetFactory[INPUT_MODE] = DateTimePickerFieldWidget

    # Note that here we are using our custom widget which subclasses DateTimePicker
    fields['custom_datetime'].widgetFactory[INPUT_MODE] = CustomDateTimePickerFieldWidgetFactory
    fields['custom_datetime2'].widgetFactory[INPUT_MODE] = CustomDateTimeWidgetWithTemplateFieldWidgetFactory


    def updateWidgets(self):
        """ Customize form widgets for the example.

        Usually Form.updateWidgets() is proper place to override your widgets to customize them.

        Note that DateWidget (no time) might not support any advanced options.
        """
        Form.updateWidgets(self)

        #
        # Example how to set default datetime programmatically to a specific value
        # 
        now = datetime.datetime.now()
        self.fields['datetime'].field.default = now

        #
        # Example how to modify datetimewidget options
        # 
        self.widgets['datetime2'].years = range(2005, 2008)

        #
        # Example how to set widget properties just to ask year and month
        #
        self.widgets['year_month'].components = ["years", "months"]
        self.widgets['year_month'].component_separators={"years":"/"}
        self.widgets['year_month'].show_jquery_picker = False # Disable Javascript picker

        #
        # Example how to set datetime widget to look like american date format
        # 
        self.widgets['american_date'].components = ["months", "days", "years"]
        self.widgets['american_date'].component_separators={"months":"/", "days" : "/"}
        self.widgets['american_date'].show_jquery_picker = False # Disable Javascript picker

    @buttonAndHandler(u'Submit')
    def submit(self, action):
        data, errors = self.extractData()

        # Give some submit feedback -
        # note that IStatusMessage uses session and 
        # does not work through anonymizer proxy
        messages = IStatusMessage(self.request)
        
        # Check console to see what our cleaned data contains
        print str(data)

        messages.addStatusMessage("Got converted object values:" + str(data), type="info")

        if errors: return False
        return True

TestView = wrap_form(TestForm)

# Spice our life with some movies in this point
# http://www.youtube.com/watch?v=MuOvqeABHvQ
