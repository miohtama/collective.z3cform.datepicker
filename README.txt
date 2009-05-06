
jqueryui datepicker integration for z3cform's and plone.

* Date picking

* Date time picking

* Date time picking without value (i.e. default = None). This applies for optional fields whose value the user might want to leave out.

`Source code available at github <http://github.com/garbas/collective.z3cform.datepicker>`_.

Code examples
=============

Few code examples are available in collective.z3cform.datepicker.tests module. 

Available examples:

1. How to change the default values (years span) etc.

2. J

Enable tests
============

1. Add line <include file="test.zcml" /> to collective/z3cform/datepicker/configure.zcml 

2. Go to http://yoursite/@@datepicker_test

TODO
----

* auto languages (loading right language js file)

* custom date(time) format

* No posting value if the user doesn't make a selection (otherwise all
  optional fields are populated with 1/1/1980)

* Initial value for datewidget support (no datetimewidget.pt only does
   this)

   01:56 < davisagli_> garbas_: in general I like it and would like to use it
   for the date fields in dexterity, but there are a few ways in which 
   it's not quite as good as the existing Archetypes date widget
   01:56 < davisagli_> garbas_: it needs to have the ability to select *no*
   date (e.g., if the field is not required)
   01:57 < davisagli_> garbas_: it needs to be usable when the backend storage
   yields a date with timezone info (this can be supported by using 
   zope.datetime.parseDatetimetz to parse the string from the widget)
   01:58 < davisagli_> garbas_: the typical case with content is the
   effective and expiration dates, which are DateTimes but not required
   01:59 < davisagli_> garbas_: it would be nice if it used full month
   names instead of numbers in the UI, to make it more clear which field
   is which (since this is different in USA from other parts of the world)
   01:59 <davisagli_> garbas_: and it would be nice if the time selection could
   be configured to either 12 hour or 24 hour clock, depending on the locale

