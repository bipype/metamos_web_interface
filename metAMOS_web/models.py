import json
import os
from django.db import models
from paths import app_paths

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
    # TODO: this should be renamed to dir_name
    path = models.CharField(max_length=256, primary_key=True)
    type = models.CharField(max_length=256)
    job = models.OneToOneField(Job, null=True)
    libraries = JSONField()
    library_ids = JSONField()

    @property
    def dir_path(self):
        """
        Path to dir where all files related to this results should be kept
        """
        return os.path.join(app_paths.storage, self.type, self.path)

    @property
    def output_dir(self):
        """
        Path to dir where final results should be placed
        """
        return os.path.join(self.dir_path, 'output')

    @property
    def run_dir(self):
        """
        Path to dir where final results should be placed
        """
        return os.path.join(self.dir_path, 'run')

    @property
    def input_dir(self):
        """
        """
        return os.path.join(self.dir_path, 'input')

    def cast(self):
        for name in dir(self):
            try:
                attr = getattr(self, name)
                if isinstance(attr, self.__class__):
                    return attr
            except:
                pass
        return self


class SampleResults(Results):

    @property
    def html_path(self):
        """
        Returns path to main HTML file with results. 
        """
        return os.path.join(self.output_dir, 'krona.html')


class MetaResults(Results):

    reference_condition = models.CharField(max_length=256)
    conditions = JSONField()