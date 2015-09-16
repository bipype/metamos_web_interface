from django.forms import forms
from django.forms.fields import CharField
from django.forms.fields import ChoiceField
from bootstrap_tables.widgets import BootstrapTableSelect
from bootstrap_tables.widgets import BootstrapTableSelectMultiple
from bootstrap_tables.fields import BootstrapTableChoiceField
from bootstrap_tables.fields import BootstrapTableMultipleChoiceField
import helpers
import sys
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')


bipype_variant_list = helpers.get_workflow_pretty_names()
sample_list = helpers.get_pretty_sample_list()


def field_with_bootstrap_class(field, **kwargs):
    """
    A decorator which initializes given field, adding 'form-control' class
    to its widget, so this field will be displayed nicely in a form.

    Args:
        field - a django field (class derived from django.forms.fields.Field,
            like: BooleanField, CharField)

    Keyword args:
        widget - allows to pass custom widget to given field; note that both:
            classes and instances derived from django.forms.widgets.Widget are
            allowed here. If an instance is detected, the function will append
            form-control class to existing attributes, without overwriting them.
        All other keyword arguments will be passed to field's initializer.
    """
    from inspect import isclass
    from django.forms.widgets import Widget
    from django.forms.fields import Field

    assert isclass(field) and issubclass(field, Field)

    classes = 'form-control'

    widget = kwargs.pop('widget', False) or field.widget

    if isclass(widget) and issubclass(widget, Widget):
        widget = widget(attrs={'class': classes})
    elif isinstance(widget, Widget):
        old_class = widget.attrs.get('class', '')
        classes = ' '.join(filter(bool, [old_class, classes]))
        widget.attrs.update({'class': classes})
    else:
        raise TypeError('widget should be a class or an instance of class '
                        'derived from django.forms.widgets.Widget')

    kwargs['widget'] = widget

    return field(**kwargs)


def set_common_options(table, field_id):
    """
    On object 'table' of class BootstrapTableWidget or subclasses set common
    properties like pagination, search engine etc and add, which will be used
    in both instances.
    """
    table.set(search=True)

    # showColumns is a switch, allowing to choose which columns are visible.
    table.set(showColumns=True)

    # Set pagination, and a switch which allows turning pagination off.
    table.set(pagination=True, pageSize=10, pageList=[5, 10, 25, 50, 100])
    table.set(showPaginationSwitch=True)

    # Move label into toolbar area, to make it look as a part of the table.
    table.set(toolbar='label[for={0}]'.format(field_id))

    table.columns.add(field='nr', title='#', align='center',
                      sortable=True, halign='center', valign='middle')
    table.columns.add(field='sample', title='Name', sortable=True,
                      valign='middle')


class SelectSampleForm(forms.Form):
    """
    Create form allowing to choose our sample and type of analysis. Fields of
    this form are created outside __init__, so they aren't dynamically generated

    This form (if used in <form> with 'get' method) will generate response like:
    ?selected_bipype_variant=A&selected_sample=B, where:
        A belongs to bipype_variant_list,
        B belongs to sample_list
    """
    type_of_analysis = field_with_bootstrap_class(
        ChoiceField,
        choices=zip(bipype_variant_list, bipype_variant_list))

    table = BootstrapTableSelect('sample')
    set_common_options(table, 'id_selected_sample')

    # Use BootstrapTableSelect widget here, instead of default Select widget.
    # Note, that fields created with widgets from bootstrap_tables package
    # doesn't need to be wrapped with field_with_bootstrap_class() function.
    selected_sample = BootstrapTableChoiceField(
        choices=enumerate(sample_list),
        widget=table)


class SelectSampleWithMetaDataForm(forms.Form):

    type_of_analysis = field_with_bootstrap_class(
        ChoiceField,
        choices=zip(bipype_variant_list, bipype_variant_list))

    #
    #  CODE BELOW FOR TEST PURPOSES ONLY
    #

    meta_table = BootstrapTableSelect('library_id')
    meta_table.set(search=True)

    # showColumns is a switch, allowing to choose which columns are visible.
    meta_table.set(showColumns=True)

    # Set pagination, and a switch which allows turning pagination off.
    meta_table.set(pagination=True, pageSize=10, pageList=[5, 10, 25, 50, 100])
    meta_table.set(showPaginationSwitch=True)

    # Move label into toolbar area, to make it look as a part of the table.
    meta_table.set(toolbar='label[for={0}]'.format('id_selected_sample_test'))

    headers, rows = helpers.load_metadata()

    # TODO: Add here other required columns
    if 'library_id' not in headers:
        raise KeyError('library_id column needed')

    for header in headers:
        meta_table.columns.add(
            field=header,
            title=forms.pretty_name(header),
            align='center', sortable=True, halign='center', valign='middle')

    selected_sample_test = BootstrapTableChoiceField(
        choices=rows,
        widget=meta_table)


class MetatranscriptomicsForm(forms.Form):

    table = BootstrapTableSelectMultiple('sample')
    set_common_options(table, 'id_selected_files')
    table.columns.add(field='condition', title='Condition')

    reference_condition = field_with_bootstrap_class(CharField)

    input_template = '<input type="text" class="form-control input-sm" ' \
                     'name="conditions[{0}]" onclick="stopPropagation(event)">'

    paired_sample_list = helpers.get_paired_samples(sample_list)

    rows = []
    for i, samples in enumerate(paired_sample_list):
        condition_input = input_template.format(samples)
        row = [i, samples, condition_input]
        rows.append(row)

    selected_files = BootstrapTableMultipleChoiceField(
        choices=rows,
        widget=table)


class RemoveSampleForm(forms.Form):

    table = BootstrapTableSelectMultiple('sample')
    set_common_options(table, 'id_samples_to_remove')

    samples_to_remove = BootstrapTableMultipleChoiceField(
        choices=enumerate(sample_list),
        widget=table)

