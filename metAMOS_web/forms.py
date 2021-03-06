from django.forms import forms
from django.forms.fields import CharField
from django.forms.fields import ChoiceField
from django.forms.forms import pretty_name
from django.utils.safestring import mark_safe
from bootstrap_tables.widgets import BootstrapTableSelect
from bootstrap_tables.widgets import BootstrapTableSelectMultiple
from bootstrap_tables.fields import BootstrapTableChoiceField
from bootstrap_tables.fields import BootstrapTableMultipleChoiceField
from metadata import MetadataManager


visible_on_start = ['library_name', 'library_comments', 'library_type', 'type']

metadata = MetadataManager.from_file()


def pretty_analysis_name(type_of_analysis):

    mappings = {
        'amplicons_its': 'Amplicons ITS',
        'amplicons_16s': 'Amplicons 16S',
        'metagenome_1': 'HUMAnN',
        'metagenome_3': 'MEGAN'
    }

    if type_of_analysis in mappings:
        return mappings[type_of_analysis]
    else:
        return type_of_analysis.replace('_', ' ').title()


def get_pretty_types_of_analyses():
    analyses = []
    for analysis in get_types_of_analyses():
        analyses.append(pretty_analysis_name(analysis))
    return analyses


def get_types_of_analyses():
    import os
    import re
    from paths import app_paths
    analyses = []
    for analysis in os.listdir(app_paths.workflows):
        match = re.match('bipype_(.*?)\.spec', analysis)
        if match:
            analyses.append(match.group(1))
    return analyses


def errors_to_messages(errors):
    messages = []
    for field, error in errors.iteritems():
        title = '<u>{0}</u> needs a correction:'.format(pretty_name(field))
        title = mark_safe(title)
        messages.append({
            'title': title,
            'contents': error.as_text().lstrip("* ").lower(),
            'type': 'warning'
        })
    return messages


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


def add_metadata_headers(table, meta_data):

    for header in meta_data.headers:
        table.columns.add(field=header,
                          visible=bool(header in visible_on_start),
                          title=forms.pretty_name(header),
                          align='left',
                          sortable=True,
                          halign='left',
                          valign='middle')


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

    add_metadata_headers(table, metadata)


class SelectSampleForm(forms.Form):
    """
    Create form allowing to choose our sample and type of analysis. Fields of
    this form are created outside __init__, so they aren't dynamically generated
    """
    choices = zip(get_types_of_analyses(), get_pretty_types_of_analyses())

    type_of_analysis = field_with_bootstrap_class(
        ChoiceField,
        choices=sorted(choices))

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
