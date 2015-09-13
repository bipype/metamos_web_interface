from django.db import models
import json
import sys
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')


# TODO: move to other file (model_fields.py??), add import
class JSONField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        try:
            return json.loads(value)
        except ValueError:
            return
        except TypeError:
            return value

    def get_db_prep_save(self, value, connection):
        value = json.dumps(value)
        return super(JSONField, self).get_db_prep_save(value, connection)


class Job(models.Model):
    started = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    progress = models.IntegerField(default=0)
    error = models.TextField()


class Results(models.Model):
    """

    """
    path = models.CharField(max_length=256, primary_key=True)
    type = models.CharField(max_length=256)
    job = models.OneToOneField(Job, null=True)


class SampleResults(Results):
    """
    path - unique path; represents path to original sample
    """
    pass


class MetaResults(Results):
    """
    path - unique path; represents path to output dir with results
    """
    generate_csv = models.BooleanField(default=False)
    reference_condition = models.CharField(max_length=256)
    files = JSONField()
