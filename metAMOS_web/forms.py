from django.forms import forms
from django.forms.fields import ChoiceField
from bootstrap_tables.widgets import BootstrapTableSelect
from django.forms.widgets import Select

import sys
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')
from helpers import get_pretty_sample_list, get_workflow_pretty_names

bipype_variant_list = get_workflow_pretty_names()
sample_list = get_pretty_sample_list()


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

    table.set(search=True)

    # showColumns is a switch, allowing to choose which columns are visible
    table.set(showColumns=True)

    # it moves our label toolbar field, which looks cool. If are going to change
    # default widget's id, please remember to update this line respectively.
    table.set(toolbar='label[for=id_selected_sample]')

    # let's set pagination, and switcher which allows to turn it off
    table.set(pagination=True, pageSize=5, showPaginationSwitch=True)

    # we want to have both header and contents horizontally centered so (h)align
    table.columns.add(field='nr', title='#', align='center',
                      sortable=True, halign='center')
    table.columns.add(field='sample', title='Name', sortable=True)

    # finally we are using our table widget here, instead of default Select().
    selected_sample = ChoiceField(choices=enumerate(sample_list),
                                  widget=table)
