#!/usr/bin/env python
import os
from paths import SAMPLE_PATH, WORKFLOWS_PATH
import models


def get_progress(**kwargs):

    from django.core.exceptions import ObjectDoesNotExist

    try:
        sample = models.SampleResults.objects.get(**kwargs)
        progress = sample.progress
    except ObjectDoesNotExist:
        progress = 0

    return progress


def create_krona_html(input_xml_path, output_html_path):
    os.system(
            'PERL5LIB=/home/pszczesny/soft/metAMOS-1.5rc3/Utilities/krona /home/pszczesny/soft/metAMOS-1.5rc3/Utilities/krona/ImportXML.pl'
            + input_xml_path + ' -o ' + output_html_path
            )


def get_krona_paths(output_dir):
    krona_xml_path = os.path.join(output_dir, 'krona.xml')
    krona_html_path = os.path.join(output_dir, 'krona.html')
    return krona_xml_path, krona_html_path


def get_sample_dir(sample_id, type_of_analysis):
    sample_source = type_of_analysis.split('_')[-1].upper()
    return os.path.join(SAMPLE_PATH[sample_source], sample_id.rstrip('.fastq'))


def get_output_dir(sample_id, type_of_analysis):
    sample_dir = get_sample_dir(sample_id, type_of_analysis)
    return os.path.join(sample_dir,
                        'bipype_output',
                        type_of_analysis)


def get_bipype_variant_list():
    return [i for i in os.listdir(WORKFLOWS_PATH) if i.startswith('bipype_')]

def get_sample_list():
    ans = {}
    for workflow in SAMPLE_PATH.keys():
        ans[workflow] = os.listdir(SAMPLE_PATH[workflow])
        ans[workflow] = [i for i in ans[workflow] if 'fastq' in i]
        #ans[workflow] = [i for i in ans[workflow] if not os.path.isfile(os.path.join(SAMPLE_PATH[workflow], i))]   # leave only directories
        #ans[workflow] = [i for i in ans[workflow] if i.startswith('Sample_')]                            # starting with Sample_
    return ans
    #return ['Sample_BF_B2_200', 'Sample_BH1_B2_200_seq11', 'Sample_GB_B2_200_seq11']   # return value for testing

def get_pretty_sample_list():
    sample_dict = get_sample_list()
    ans = []
    for k,v in sample_dict.iteritems():
        for i in v:
            ans.append(k + '/' + i)
    return ans

def get_workflows_for_samples(sample_source):
    workflows = get_bipype_variant_list()
    return [i for i in workflow if sample_source.lower() in i]

def get_workflow_pretty_names():
    return ['amplicons', 'biodiversity']

def get_right_workflow(sample_pretty_name, workflow_pretty_name):
    return [i for i in get_workflows_for_samples(sample_pretty_name.split('/')[0]) if workflow_pretty_name in i][0]

