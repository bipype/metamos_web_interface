#!/usr/bin/env python
import os
from paths import SAMPLE_PATH, WORKFLOWS_PATH

def get_bipype_variant_list():
    return [i for i in os.listdir(WORKFLOWS_PATH) if i.startswith('bipype_')]

def get_sample_list():
    ans = {}
    for workflow in SAMPLE_PATH.keys():
        ans[workflow] = os.listdir(SAMPLE_PATH[workflow])
        ans[workflow] = [i for i in ans[workflow] if not os.path.isfile(os.path.join(SAMPLE_PATH[workflow], i))]   # leave only directories
        ans[workflow] = [i for i in ans[workflow] if i.startswith('Sample_')]                            # starting with Sample_
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

