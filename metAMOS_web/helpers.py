#!/usr/bin/env python
import os
import urllib
from tempfile import mkdtemp
from paths import SAMPLE_PATH, WORKFLOWS_PATH
from metAMOS_web.models import Results
from django.forms.forms import pretty_name
from django.utils.safestring import mark_safe
import job_manager
import shutil
import re


def real_path(path):
    """
    Returns real location of the object on the server; by default
    server-specific part of path is hidden away from end-user.
    """
    from string import Template
    return Template('$' + path).substitute(SAMPLE_PATH)


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


def remove_results_by_data(**data):
    # it is possible to rewrite this function with pre_delete signal in future
    results_objects = Results.objects.filter(**data)

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


def make_unique_dir(parent_dir):
    absolute_path = mkdtemp(dir=parent_dir)
    return os.path.basename(absolute_path)


def encode_path(path):
    """
    Yes, it is encoded and decoded twice; it's due to some restrictions
    within Apache servers; check: http://www.leakon.com/archives/865
    """
    path = urllib.quote(path, safe='')
    return urllib.quote(path, safe='')


def decode_path(path):
    path = urllib.unquote(path)
    return urllib.unquote(path)


def get_bipype_variant_list():
    return [i for i in os.listdir(WORKFLOWS_PATH) if i.startswith('bipype_')]


def get_pretty_sample_list():
    samples = []
    for alias, real_dir_path in SAMPLE_PATH.items():
        for a_file in os.listdir(real_dir_path):
            if not (a_file.endswith('.d') or a_file.endswith('.py')) and a_file.find('fast') != -1:
                samples.append(alias + '/' + a_file)
    return samples


def get_paired_samples(sample_list):
    """
    Complies list of samples, where elements are strings containing pairs of
    reads (reads are separated by space). To match reads from given sample_list,
    this function looks for presence of _R1_ and _R2_ substrings in filenames.
    If the pair couldn't be created because there is a missing complementary
    read - the existing one will be skipped.
    """
    catch_r = re.compile('_R\d_')

    bases = set(catch_r.sub('', x) for x in sample_list)
    r1 = filter(lambda x: '_R1_' in x, sample_list)
    r2 = filter(lambda x: '_R2_' in x, sample_list)

    paired_sample_list = []

    for base in bases:

        try:

            r1_file = filter(lambda x: catch_r.sub('', x) == base, r1)[0]
            r2_file = filter(lambda x: catch_r.sub('', x) == base, r2)[0]

            # spaces are not allowed in filenames - it is forced by
            # metatranscriptomics_bipype so here we can take advantage of it
            # and use a space as an universal separator. But only to be certain
            # we are an assertion here, so samples whose names doesn't abide
            # with this rule could be quickly localized.
            assert ' ' not in r1_file and ' ' not in r2_file
            entry = ' '.join([r1_file, r2_file])

            paired_sample_list.append(entry)

        except IndexError:
            # there is a missing read (R1 or R2) for the base, so skip this one.
            pass

    return paired_sample_list


def get_workflow_pretty_names():
    return ['amplicons', 'biodiversity']
