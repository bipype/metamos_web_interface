#!/usr/bin/env python
import os

from paths import app_paths
from metAMOS_web.models import Results
from django.forms.forms import pretty_name
from django.utils.safestring import mark_safe

import job_manager
import shutil


def errors_to_messages(errors):
    messages = []
    for field, error in errors.iteritems():
        title = '<u>{0}</u> needs a correction:'.format(pretty_name(field))
        title = mark_safe(title)
        messages.append({
            'title': title,
            'contents': error.as_text().lstrip("* ").lower(),
            'type': 'warning'
        })
    return messages


def remove_results_by_library_id(library_id):
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


def get_results_object(**results_data):
    results_object = Results.objects.get(**results_data)
    return results_object.cast()


def get_bipype_variant_list():
    return [i for i in os.listdir(app_paths.workflows) if i.startswith('bipype_')]


def get_workflow_pretty_names():
    return ['amplicons', 'biodiversity']
