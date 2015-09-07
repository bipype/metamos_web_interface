from django.db import models
import sys
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')


# Create your models here.
class SampleResults(models.Model):
    sample = models.CharField(max_length=256)
    variant = models.CharField(max_length=256)
    job_started = models.BooleanField(default=False)
    job_completed = models.BooleanField(default=False)
