from django.forms import forms
from django.forms.fields import ChoiceField
from bootstrap_tables.widgets import BootstrapTableSelect

import sys
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')
from helpers import get_pretty_sample_list, get_workflow_pretty_names

bipype_variant_list = get_workflow_pretty_names()
sample_list = get_pretty_sample_list()


class SelectSampleForm(forms.Form):
    select = BootstrapTableSelect('sample')
    select.set(search=True)
    select.columns.add(field='nr', title='#')
    select.columns.add(field='sample', title='Name', sortable=True)
    selected_sample = ChoiceField(choices=enumerate(sample_list), widget=select)
    selected_bipype_variant = ChoiceField(choices=zip(bipype_variant_list, bipype_variant_list))
