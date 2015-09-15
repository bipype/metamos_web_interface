#!/usr/bin/env python
import os
import sys
import subprocess
from time import sleep
import paths

CWD = os.getcwd()
DIRNAME = os.path.dirname(CWD)
sys.path.append(DIRNAME)
sys.path.append(CWD)
sys.path.append(os.path.join(DIRNAME, 'metAMOS_web_interface'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'metAMOS_web_interface.settings'
from django.core.management import setup_environ
import metAMOS_web_interface.settings as settings
setup_environ(settings)
import shutil
import glob

from job_manager import JobManager

SUBPROCESS_ENV = os.environ.copy()
SUBPROCESS_ENV['SHELL'] = '/bin/bash'


def update_progress(job, value):
    print "Progress: " + str(value)
    job.progress = value
    job.save()


def run_metamos(job, results_object):
    """
    Args:
        results_object - an instance of SampleResults object
    """
    sample = results_object

    if not os.path.exists(sample.out_dir_path):
        os.makedirs(sample.out_dir_path)

    update_progress(job, 5)

    run_dir = os.path.join(sample.dir_path, 'rundirs')

    if not os.path.exists(run_dir):
        os.mkdir(run_dir)

    work_dir = os.path.join(run_dir, sample.type)

    out_log = open('/tmp/bipype.out', 'w')
    err_log = open('/tmp/bipype.err', 'w')

    command = ' '.join(
        [os.path.join(paths.PATH_METAMOS_DIR, 'initPipeline'),
         '-1',
         sample.real_path,
         '-d',
         work_dir]
    )
    print command
    init_ps = subprocess.Popen(command, env=SUBPROCESS_ENV, shell=True, stdout=out_log, stderr=err_log)
    init_ps.wait()

    update_progress(job, 30)

    skip = 'FindORFS,MapReads,Validate,Abundance,Annotate,Scaffold,Propagate,Classify'

    command = ' '.join(
        [os.path.join(paths.PATH_METAMOS_DIR, 'runPipeline'),
         '-n',
         skip,
         # hack
         '-a',
         'bipype_' + sample.type,
         '-d',
         work_dir]
    )
    print command
    ps_run = subprocess.Popen(command, env=SUBPROCESS_ENV, shell=True, stdout=out_log, stderr=err_log)
    ps_run.wait()

    out_log.close()
    err_log.close()

    update_progress(job, 90)

    path_name = os.path.join(work_dir, 'Assemble/out/out2/*.html')
    krona_html = glob.glob(path_name)

    # there should be exactly one krona *.html file in Assemble/out/out2/
    assert len(krona_html) == 1

    shutil.copyfile(krona_html[0], sample.html_path)

    update_progress(job, 100)


def run_metatranscriptomics(job, results_object):

    update_progress(job, 5)

    # create output_type argument
    output_type = ['both']

    # TODO:

    # create tmp file with settings
    config_file_path = os.path.join(results_object.real_path, 'meta.config')

    with open(config_file_path, 'w') as f:
        f.write(results_object.reference_condition + '\n')

        import re

        without_r = re.compile('_R\d_')

        base = (without_r.sub('', x) for x in results_object.files)
        R1 = filter(lambda x: re.match('_R1_', x), results_object.files)
        R2 = filter(lambda x: re.match('_R2_', x), results_object.files)

        print base
        print R1
        print R2

        cond_counter = {}

        for base_name in base:
            r1_file = filter(lambda x: without_r.sub('', x) == base_name, R1)[0]
            r2_file = filter(lambda x: without_r.sub('', x) == base_name, R2)[0]

            try:
                condition = results_object.conditions[r1_file]
            except KeyError:
                condition = results_object.conditions[r2_file]

            cond_counter[condition] = cond_counter.get(condition, -1) + 1
            line_id = condition + '_' + cond_counter[condition]

            line = line_id + '\t' + ' '.join([r1_file, r2_file, condition])

            f.write(line)

    # for debug only:
    with open(config_file_path, 'r') as f:
        print f.read()

    # feed bipype by subprocess with tmp file
    commands = [
        paths.PATH_BIPYPE,
        '--metatr_config',
        config_file_path,
        '--metatr_output_type',
        output_type,
        '--out_dir',
        results_object.real_path
    ]

    command = ' '.join(commands)

    out_log = open('/tmp/bipype.out', 'w')
    err_log = open('/tmp/bipype.err', 'w')

    process = subprocess.Popen(
        command,
        env=SUBPROCESS_ENV,
        shell=True,
        stdout=out_log,
        stderr=err_log
    )

    process.wait()

    # TODO:
    # seek for information about progress
    # be happy if job finished successfully

    update_progress(job, 100)


if __name__ == '__main__':

    job_manager = JobManager()
    job_manager.add_callback(run_metatranscriptomics, 'metatranscriptomics')
    job_manager.add_callback(run_metamos, 'default')

    while True:

        performed = job_manager.run_queued()

        if performed:
            sleep(1)
        else:
            # let's be more friendly for server if the queue was empty last time
            sleep(10)
