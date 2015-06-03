#!/usr/bin/env python
import os, sys
import subprocess
from uuid import uuid4
from time import sleep
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
os.environ['DJANGO_SETTINGS_MODULE'] = 'metAMOS_web_interface.settings'
from django.core.management import setup_environ
import django
import metAMOS_web_interface.settings as settings
from paths import SAMPLE_PATH
setup_environ(settings)
#django.setup()
from metAMOS_web.models import SampleResults

SUBPROCESS_ENV = os.environ.copy()
SUBPROCESS_ENV['SHELL'] = '/bin/bash'

def get_any_fasta(directory):
    return [i for i in os.listdir(directory) if i.endswith('fasta')][0]

def run_metamos(sample_id, bipype_variant):
    sample_source = bipype_variant.split('_')[-1].upper()
    output_path = os.path.join(SAMPLE_PATH[sample_source], sample_id, 'bipype_output', bipype_variant)
    krona_html_path = os.path.join(SAMPLE_PATH[sample_source], sample_id, 'bipype_output', bipype_variant + '/krona.html')
    sample = SampleResults.objects.get(sample=sample_id, variant=bipype_variant)
    sample.job_started = True
    sample.save()
    if not os.path.exists(os.path.join(SAMPLE_PATH[sample_source], sample_id, 'rundirs')):
        os.mkdir(os.path.join(SAMPLE_PATH[sample_source], sample_id, 'rundirs'))
    workdir = os.path.join(SAMPLE_PATH[sample_source], sample_id, 'rundirs', bipype_variant)
    out_log = open('/tmp/bipype.out', 'w')
    err_log = open('/tmp/bipype.err', 'w')
    init_ps = subprocess.Popen(' '.join(['/home/pszczesny/soft/metAMOS-1.5rc3/initPipeline', '-1', os.path.join(SAMPLE_PATH[sample_source], sample_id, 
        get_any_fasta(os.path.join(SAMPLE_PATH[sample_source], sample_id))), '-d',  workdir]), env=SUBPROCESS_ENV, shell=True, stdout=out_log, stderr=err_log)
    init_ps.wait()
    ps_run = subprocess.Popen(' '.join(['/home/pszczesny/soft/metAMOS-1.5rc3/runPipeline', '-n', 'FindORFS,MapReads,Validate,Abundance,Annotate,Scaffold,Propagate,Classify', 
        '-a', bipype_variant, '-d', workdir]), env=SUBPROCESS_ENV, shell=True, stdout=out_log, stderr=err_log)
    ps_run.wait()
    out_log.close()
    err_log.close()
    os.system('cp -a ' + workdir+ '/Assemble/out/out2/*.krona ' + output_path + '/krona.html')
    sample.job_completed = True
    sample.save()

def check_and_add_sample(sample_id, bipype_variant):
    if len(SampleResults.objects.filter(sample=sample_id, variant=bipype_variant)) == 0:
        sample = SampleResults(sample=sample_id, variant=bipype_variant, job_started=False, job_completed=False)
        sample.save()
    
def run_queued_sample():
    try:
        sample = SampleResults.objects.filter(job_started=False)[0]
    except IndexError:   # nothing to do
        return
    run_metamos(sample_id=sample.sample, bipype_variant=sample.variant)


if __name__=='__main__':
    while True:
        run_queued_sample()
        sleep(1)
