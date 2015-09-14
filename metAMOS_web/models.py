from django.db import models
import json
import sys
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')
import paths
import os

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
    """
    path - unique path; represents path to original sample
    """

    @property
    def html_path(self):
        """
        Returns path to main HTML file with results. 
        """
        return os.path.join(self.out_dir_path, 'krona.html')

    @property
    def real_path(self):
        """
        Returns real location of the object on the server; by default
        server-specific part of path is hidden away from end-user.
        """
        from string import Template
        # use of substitution dict from paths.SAMPLE_PATH
        return Template('$' + self.path).substitute(paths.SAMPLE_PATH)

    @property
    def dir_path(self):
        """
        Returns path to dir where all results should be kept 
        """
        return self.real_path + '.d'

    @property
    def out_dir_path(self):
        """
        Returns path to dir where final outputs should be placed
        """
        return os.path.join(self.dir_path, 'bipype_output', self.type)



class MetaResults(Results):
    """
    path - unique path; represents path to dir with results
    """
    generate_csv = models.BooleanField(default=False)
    reference_condition = models.CharField(max_length=256)
    files = JSONField()

    @property
    def html_path(self):
        """
        Returns path to main HTML file with results. 
        """
        import os
        return os.path.join(self.dir_path, 'index.html')

    @property
    def real_path(path):
        """
        Returns real location of the object on the server; by default
        server-specific part of path is hidden away from end-user.
        """
        return os.path.join(paths.PATH_METATR_OUT_DIR, path)

    @property
    def dir_path(self):
        """
        Returns path to dir where all results should be kept 
        """
        return self.path
