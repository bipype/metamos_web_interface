#!/usr/bin/env python
import os
import shutil
import copy
import json
from django.forms.forms import pretty_name
from django.core.exceptions import ObjectDoesNotExist
from models import Results
from metadata import MetadataManager
from bootstrap_tables.widgets import BootstrapTableWidget
from forms import add_metadata_headers
import job_manager
from paths import app_paths


metadata = MetadataManager.from_file()


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

    libraries = copy.deepcopy(results_object.libraries)

    results_metadata = MetadataManager.from_dict(libraries)
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


def get_or_create(model, data):

    try:
        # for lookups, we need to dump values in JSON fields;

        # we don't want to do this on the same copy which
        # will be passed to creator in case of our fail.
        lookup_data = copy.copy(data)

        # Warning: assuming, that lists and dicts will always go to JSON fields
        for field_id, value in lookup_data.iteritems():
            if type(value) in [list, dict]:
                lookup_data[field_id] = json.dumps(value)

        results_object = model.objects.get(**lookup_data)

    except ObjectDoesNotExist:
        data['libraries'] = metadata.get_subset(data['library_ids'])
        data['path'] = app_paths.unique_path_for(data['type'])
        results_object = model.objects.create(**data)

    return results_object


def get_libraries_warnings(results_object):
    """
    Check whether libraries information are up-to date with currently loaded
    version of metadata worksheet; return appropriate message if they aren't.
    """
    messages = []

    libraries = metadata.get_subset(results_object.library_ids)

    # if libraries are not up to date
    if not results_object.libraries == libraries:

        new_data = MetadataManager.from_dict(libraries)
        old_data = MetadataManager.from_dict(results_object.libraries)

        changed_libraries = []

        for library_id in results_object.library_ids:
            if new_data.get_row(library_id) != old_data.get_row(library_id):
                changed_libraries.append(library_id)

        subject = 'libraries' if len(changed_libraries) > 1 else 'library'

        messages.append({
            'title': 'Metadata has changed!',
            'contents': 'Information about {0} of id: {1} used for this job '
                        'differ from these, which are in metadata file. '
                        'To recalculate these results with newer data, remove '
                        'them and then, start the job again. Metadata shown '
                        'below are these, which were used for this job, '
                        'not the one from current metadata file'.format(
                            subject,
                            ','.join(changed_libraries)
                        ),
            'type': 'warning'
        })

    return messages
