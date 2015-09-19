from django.forms import forms
from django.forms.fields import CharField
from django.forms.fields import ChoiceField
from bootstrap_tables.widgets import BootstrapTableSelect
from bootstrap_tables.widgets import BootstrapTableSelectMultiple
from bootstrap_tables.fields import BootstrapTableChoiceField
from bootstrap_tables.fields import BootstrapTableMultipleChoiceField
import helpers
from metadata import MetadataManager
import sys
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')


visible_on_start = ['library_name', 'library_comments', 'localization', 'type']
bipype_variant_list = helpers.get_workflow_pretty_names()
metadata = MetadataManager()
metadata.from_file()


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

    for header in metadata.headers:
        table.columns.add(field=header,
                          visible=bool(header in visible_on_start),
                          title=forms.pretty_name(header),
                          align='left',
                          sortable=True,
                          halign='left',
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

    table = BootstrapTableSelect(metadata.id_column)

    set_common_options(table, 'id_library_id')

    library_id = BootstrapTableChoiceField(
        choices=metadata.rows,
        widget=table)


class MetatranscriptomicsForm(forms.Form):

    table = BootstrapTableSelectMultiple(metadata.id_column)
    set_common_options(table, 'id_library_ids')

    reference_condition = field_with_bootstrap_class(CharField)

    input_template = '<input type="text" class="form-control input-sm" ' \
                     'name="conditions[{0}]" onclick="stopPropagation(event)">'

    table.columns.add(field='condition', title='Condition')

    rows = []
    for row in metadata.rows:
        library_id = row[metadata.id_index]
        condition_input = input_template.format(library_id)
        row.append(condition_input)
        rows.append(row)

    library_ids = BootstrapTableMultipleChoiceField(
        choices=rows,
        widget=table)


class RemoveResultsForm(forms.Form):

    table = BootstrapTableSelectMultiple(metadata.id_column)
    set_common_options(table, 'id_results_to_remove')

    results_to_remove = BootstrapTableMultipleChoiceField(
        choices=metadata.rows,
        widget=table)
