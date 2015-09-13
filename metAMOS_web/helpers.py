#!/usr/bin/env python
import os
import urllib
from tempfile import mkdtemp
from django.core.exceptions import ObjectDoesNotExist
from paths import SAMPLE_PATH, WORKFLOWS_PATH
from metAMOS_web.models import Results
from django.forms.forms import pretty_name
import job_manager


def errors_to_messages(errors):
    messages = []
    for field, error in errors.iteritems():
        messages.append({
            'title': 'Please correct: "{0}"'.format(pretty_name(field)),
            'contents': error.as_text(),
            'type': 'warning'
        })
    return messages


def get_sample_dir(path):
    from string import Template
    return Template('$' + path + '.d').substitute(SAMPLE_PATH)


def get_output_dir(path, type_of_analysis):
    sample_dir = get_sample_dir(path)
    return os.path.join(sample_dir, 'bipype_output', type_of_analysis)


def remove_results_by_data(**data):
    results_objects = Results.objects.filter(**data)

    if not results_objects:
        return None

    try:

        for results_object in results_objects:

            # 1. remove job
            job_manager.remove_job(results_object.job)

            # 2. determine output dir and remove it (type-specific)
            if results_object.type == 'metatranscriptomics':
                output_dir = results_object.path
            else:
                output_dir = get_output_dir(results_object.path,
                                            results_object.type)
            # TODO
            print "Removing " + output_dir
            # rm -r output_dir

            # 3. remove result
            results_object.delete()
        return True

    except:                                          # TODO: specific exceptions
        return False


def get_results_object(**results_data):
    return Results.objects.get(**results_data)


def make_unique_dir(parent_dir):
    absolute_path = mkdtemp(dir=parent_dir)
    return os.path.basename(absolute_path)


def encode_path(path):
    """
    Yes, it is encoded and decoded twice; it's due to some restrictions
    within Apache servers; check: http://www.leakon.com/archives/865
    """
    path = urllib.quote(path, safe='')
    return  urllib.quote(path, safe='')


def decode_path(path):
    path = urllib.unquote(path)
    return urllib.unquote(path)


def create_krona_html(input_xml_path, output_html_path):
    os.system(
            'PERL5LIB=/home/pszczesny/soft/metAMOS-1.5rc3/Utilities/krona /home/pszczesny/soft/metAMOS-1.5rc3/Utilities/krona/ImportXML.pl'
            + input_xml_path + ' -o ' + output_html_path
            )


def get_krona_paths(output_dir):
    krona_xml_path = os.path.join(output_dir, 'krona.xml')
    krona_html_path = os.path.join(output_dir, 'krona.html')
    return krona_xml_path, krona_html_path


def get_bipype_variant_list():
    return [i for i in os.listdir(WORKFLOWS_PATH) if i.startswith('bipype_')]


def get_pretty_sample_list():
    samples = []
    for alias, real_path in SAMPLE_PATH.items():
        for a_file in os.listdir(real_path):
            if not a_file.endswith('.d'):
                samples.append(alias + '/' + a_file)
    return samples


def get_workflow_pretty_names():
    return ['amplicons', 'biodiversity']
