"""
Provides fields to be used as replacements for Django's ChoiceField and
MultipleChoiceField fields; Fields from these module extends default validation
process to be able to validate properly widgets created with BootstrapTable.

This version was written for Django 1.4.*.
"""

from django.forms import fields as django_fields
from widgets import BootstrapTableWidget


def valid_value(self, value):

    if issubclass(type(self.widget), BootstrapTableWidget):
        choices = self.widget.get_valid_choices()
        return bool(value in choices)

    else:
        return super(type(self), self).valid_value(value)


class BootstrapTableMultipleChoiceField(django_fields.MultipleChoiceField):

    valid_value = valid_value


class BootstrapTableChoiceField(django_fields.ChoiceField):

    valid_value = valid_value
