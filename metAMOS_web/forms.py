from django.forms import forms
from django.forms.fields import ChoiceField
from django.forms.fields import MultipleChoiceField
from django.forms.widgets import Select
from bootstrap_tables.widgets import BootstrapTableSelect
from bootstrap_tables.widgets import BootstrapTableSelectMultiple

import sys
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')
from helpers import get_pretty_sample_list, get_workflow_pretty_names

bipype_variant_list = get_workflow_pretty_names()
sample_list = get_pretty_sample_list()


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
    table.set(pagination=True, pageSize=5, pageList=[5, 10, 25, 50])
    table.set(showPaginationSwitch=True)

    # Move label into toolbar area, to make it look as a part of the table.
    table.set(toolbar='label[for={0}]'.format(field_id))

    # To have both header and contents horizontally centered so (h)align.
    table.columns.add(field='nr', title='#', align='center',
                      sortable=True, halign='center')
    table.columns.add(field='sample', title='Name', sortable=True)


class MetatranscriptomicsForm(forms.Form):
    pass


class RemoveSampleForm(forms.Form):

    table = BootstrapTableSelectMultiple('sample')
    set_common_options(table, 'id_samples_to_remove')

    # Use BootstrapTableSelect widget here, instead of default Select widget
    samples_to_remove = MultipleChoiceField(choices=enumerate(sample_list),
                                            widget=table)


class SelectSampleForm(forms.Form):
    """
    Create form allowing to choose our sample and type of analysis. Fields of
    this form are created outside __init__, so they aren't dynamically generated

    This form (if used in <form> with 'get' method) will generate response like:
    ?selected_bipype_variant=A&selected_sample=B, where:
        A belongs to bipype_variant_list,
        B belongs to sample_list
    """
    selected_bipype_variant = ChoiceField(
        choices=zip(bipype_variant_list, bipype_variant_list),
        label='Type of analysis',
        widget=Select(attrs={'class': 'form-control'})
    )

    table = BootstrapTableSelect('sample')
    set_common_options(table, 'id_selected_sample')

    # Use BootstrapTableSelect widget here, instead of default Select widget
    selected_sample = ChoiceField(choices=enumerate(sample_list), widget=table)
