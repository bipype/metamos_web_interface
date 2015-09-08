#!/usr/bin/env python
import os
import sys
import subprocess
from time import sleep
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
os.environ['DJANGO_SETTINGS_MODULE'] = 'metAMOS_web_interface.settings'
from django.core.management import setup_environ
import metAMOS_web_interface.settings as settings
setup_environ(settings)
from metAMOS_web.models import SampleResults
import helpers

SUBPROCESS_ENV = os.environ.copy()
SUBPROCESS_ENV['SHELL'] = '/bin/bash'


def get_any_fasta(directory):
    # TODO: this is wrong, or we need to rename all files to *.fasta
    return [i for i in os.listdir(directory) if i.endswith('fasta')][0]


def run_metamos(sample_id, type_of_analysis):

    sample_dir = helpers.get_sample_dir(sample_id, type_of_analysis)
    output_dir = helpers.get_output_dir(sample_id, type_of_analysis)
    krona_xml_path, krona_html_path = helpers.get_krona_paths(output_dir)

    sample = SampleResults.objects.get(sample=sample_id, variant=type_of_analysis)
    sample.job_started = True
    sample.progress = 1
    sample.save()

    run_dir = os.path.join(sample_dir, 'rundirs')

    if not os.path.exists(run_dir):
        os.mkdir(run_dir)

    work_dir = os.path.join(run_dir, type_of_analysis)

    out_log = open('/tmp/bipype.out', 'w')
    err_log = open('/tmp/bipype.err', 'w')

    init_ps = subprocess.Popen(' '.join(
        ['/home/pszczesny/soft/metAMOS-1.5rc3/initPipeline',
         '-1',
         os.path.join(sample_dir, get_any_fasta(sample_dir)),   # TODO: ???????
         '-d',
         work_dir]
    ), env=SUBPROCESS_ENV, shell=True, stdout=out_log, stderr=err_log)
    init_ps.wait()

    sample.progress = 50
    sample.save()

    ps_run = subprocess.Popen(' '.join(
        ['/home/pszczesny/soft/metAMOS-1.5rc3/runPipeline',
         '-n',
         'FindORFS,MapReads,Validate,Abundance,Annotate,Scaffold,Propagate,Classify',
         '-a',
         type_of_analysis,
         '-d',
         work_dir]
    ), env=SUBPROCESS_ENV, shell=True, stdout=out_log, stderr=err_log)
    ps_run.wait()

    out_log.close()
    err_log.close()

    os.system('cp -a ' + work_dir + '/Assemble/out/out2/*.krona ' + krona_xml_path)
    sample.job_completed = True
    sample.progress = 100
    sample.save()


def check_and_add_sample(sample_id, type_of_analysis):
    if len(SampleResults.objects.filter(sample=sample_id, variant=type_of_analysis)) == 0:
        sample = SampleResults(sample=sample_id,
                               variant=type_of_analysis,
                               job_started=False,
                               job_completed=False)
        sample.save()


def run_queued_sample():
    try:
        sample = SampleResults.objects.filter(job_started=False)[0]
    except IndexError:   # nothing to do
        return
    run_metamos(sample_id=sample.sample, type_of_analysis=sample.variant)


if __name__ == '__main__':
    while True:
        run_queued_sample()
        sleep(1)
