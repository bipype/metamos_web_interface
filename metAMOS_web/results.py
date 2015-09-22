#!/usr/bin/env python
import os

from metAMOS_web.models import Results
from metadata import MetadataManager
from bootstrap_tables.widgets import BootstrapTableWidget
from forms import add_metadata_headers
from django.forms.forms import pretty_name

import job_manager
import shutil


ANALYSES = {
    'amplicons_its': 'Amplicons ITS',
    'amplicons_16s': 'Amplicons 16S'
}


def pretty_analysis_name(type_of_analysis):
    return ANALYSES.get(type_of_analysis, type_of_analysis)


def get_without_paths(results_object, filename):

    path = os.path.join(results_object.input_dir, filename)

    with open(path, 'r') as f:
        contents = f.read()
        contents = contents.replace(results_object.input_dir + '/', '')
        contents = contents.replace(results_object.output_dir + '/', '')
    return contents


def get_list(results_object, skip=None):

    if skip is None:
        skip = []

    file_list = []

    output_dir = results_object.output_dir

    for root, dirs, files in os.walk(output_dir):

        for name in files:
            if name in skip:
                continue
            current_path = os.path.join(root.replace(output_dir, ''), name)
            if current_path.endswith('.html'):
                mode = 'html'
                icon = 'file'
            else:
                mode = 'download'
                icon = 'download-alt'
            current_file = {
                'mode': mode,
                'path': current_path,
                'icon': icon,
                'name': pretty_name(os.path.splitext(name)[0])
                }
            file_list.append(current_file)

    return file_list


def create_meta_table(results_object):

    results_metadata = MetadataManager()
    results_metadata.from_dict(results_object.libraries)
    data_table = BootstrapTableWidget('')
    # column in place of widget's checkbox or radio (we are using it here,
    # since it easier to create table from Widget, than from scratch)
    data_table.columns.add(field='empty', visible=False, switchable=False)
    add_metadata_headers(data_table, results_metadata)
    if results_object.type == 'metatranscriptomics':
        data_table.columns.add(field='condition', title='Condition',
                               align='left', sortable=True,
                               halign='left', valign='middle')
        rows = []
        for row in results_metadata.rows:
            library_id = row[results_metadata.id_index]
            condition = results_object.conditions[library_id]
            row.append(condition)
            rows.append(row)
    else:
        rows = results_metadata.rows
    data_table.set(showColumns=True)
    data_table.set(toolbar='#meta_table_header')
    data_table.choices = rows
    return data_table


def remove_by_library_id(library_id):
    # it is possible to rewrite this function with pre_delete signal in future

    # We have to look inside 'library_ids' field. Since this is JSON field, we
    # need to use JSON format to match appropriate results - so we are looking
    # for identificators enclosed by double quotes char (")
    conditions = {'library_ids__contains': '"{0}"'.format(library_id)}
    results_objects = Results.objects.filter(**conditions)

    if not results_objects:
        return None

    try:
        for results_object in results_objects:

            casted_object = results_object.cast()

            # 1. remove job
            job_manager.remove_job(casted_object.job)

            # 2. determine output dir and remove it (type-specific)
            results_dir = casted_object.dir_path

            print "Removing " + results_dir
            shutil.rmtree(results_dir, ignore_errors=True)

            # 3. remove result - it's strange but django requires here
            # uncasted instance of an object
            results_object.delete()
        return True
    except:                                          # TODO: specific exceptions
        return False


def get_object(**results_data):
    results_object = Results.objects.get(**results_data)
    return results_object.cast()