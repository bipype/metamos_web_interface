from django.db import models
from django.forms import forms
from django.forms.fields import ChoiceField
import sys
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')
from helpers import get_pretty_sample_list, get_workflow_pretty_names

bipype_variant_list = get_workflow_pretty_names()
sample_list = get_pretty_sample_list()

# Create your models here.
class SampleResults(models.Model):
    sample = models.CharField(max_length=256)
    variant = models.CharField(max_length=256)
    job_started = models.BooleanField(default=False)
    job_completed = models.BooleanField(default=False)

class SelectSampleForm(forms.Form):
    selected_sample = ChoiceField(choices=zip(sample_list, sample_list))
    selected_bipype_variant = ChoiceField(choices=zip(bipype_variant_list, bipype_variant_list))
