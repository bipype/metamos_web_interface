import os
import urllib
import tempfile
import string


def encode(path):
    return urllib.quote(path, safe='')


def decode(path):
    return urllib.unquote(path)


def make_unique(parent_dir):
        absolute_path = tempfile.mkdtemp(dir=parent_dir)
        return os.path.basename(absolute_path)


def expand(paths_dict):
    for alias, path in paths_dict.iteritems():
        path = string.Template(path).substitute(paths_dict)
        paths_dict[alias] = os.path.expanduser(path)
    return paths_dict


class Paths(object):

    PATHS = {
        'tmp': '/tmp',
        'metAMOS': '~/soft/metAMOS-1.5rc3/',
        'workflows': '$metAMOS/Utilities/config',
        'storage': '~/storage/metamos_web_interface/',
        'bipype': '~/soft/bipype_new/bipype',
        'interface_root': '~/soft/metAMOS_web_interface',
        'metadata': '$interface_root/biogaz_libraries_metadata_sample.xlsx'
    }

    def __init__(self):
        self.PATHS = expand(self.PATHS)

    def __getattr__(self, alias):
        return self.PATHS[alias]

    def unique_path_for(self, type_of_analysis):

        path = os.path.join(self.storage, type_of_analysis)

        if not os.path.exists(path):
            os.makedirs(path)

        return make_unique(path)

app_paths = Paths()
