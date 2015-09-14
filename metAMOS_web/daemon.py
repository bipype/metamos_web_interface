#!/usr/bin/env python
import os
import sys
import subprocess
from time import sleep

from paths import PATH_METAMOS_DIR


sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
os.environ['DJANGO_SETTINGS_MODULE'] = 'metAMOS_web_interface.settings'
from django.core.management import setup_environ
import metAMOS_web_interface.settings as settings
setup_environ(settings)
import helpers
import shutil
import glob

from job_manager import JobManager

SUBPROCESS_ENV = os.environ.copy()
SUBPROCESS_ENV['SHELL'] = '/bin/bash'


def get_any_fasta(directory):
    # TODO: this is wrong, or we need to rename all files to *.fasta
    return [i for i in os.listdir(directory) if i.endswith('fasta')][0]


def update_progress(job, value):
    print "Progress: " + str(value)
    job.progress = value
    job.save()


def run_metamos(job, results_object):

    sample_path = results_object.path
    type_of_analysis = results_object.type

    sample_dir = helpers.get_sample_dir(sample_path)
    output_dir = helpers.get_output_dir(sample_path, type_of_analysis)
    krona_xml_path, krona_html_path = helpers.get_krona_paths(output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    update_progress(job, 5)

    run_dir = os.path.join(sample_dir, 'rundirs')

    if not os.path.exists(run_dir):
        os.mkdir(run_dir)

    work_dir = os.path.join(run_dir, type_of_analysis)

    out_log = open('/tmp/bipype.out', 'w')
    err_log = open('/tmp/bipype.err', 'w')

    init_ps = subprocess.Popen(' '.join(
        [os.path.join(PATH_METAMOS_DIR, 'initPipeline'),
         '-1',
         os.path.join(sample_dir, get_any_fasta(sample_dir)),
         '-d',
         work_dir]
    ), env=SUBPROCESS_ENV, shell=True, stdout=out_log, stderr=err_log)
    init_ps.wait()

    update_progress(job, 30)

    skip = 'FindORFS,MapReads,Validate,Abundance,Annotate,Scaffold,Propagate,Classify'

    ps_run = subprocess.Popen(' '.join(
        [os.path.join(PATH_METAMOS_DIR, 'runPipeline'),
         '-n',
         skip,
         '-a',
         type_of_analysis,
         '-d',
         work_dir]
    ), env=SUBPROCESS_ENV, shell=True, stdout=out_log, stderr=err_log)
    ps_run.wait()

    out_log.close()
    err_log.close()

    update_progress(job, 90)

    krona_files = glob.glob(work_dir + '/Assemble/out/out2/*.krona')
    # there should be exactly one *.krona file in /Assemble/out/out2/
    assert len(krona_files) != 1

    shutil.copyfile(krona_files[0], krona_xml_path)

    update_progress(job, 95)

    if not os.path.exists(krona_html_path):
        helpers.create_krona_html(krona_xml_path, krona_html_path)

    update_progress(job, 100)


def run_metatranscriptomics(job, results_object):

    update_progress(job, 5)

    out_dir_path = results_object.path

    # create output_type argument
    output_type = ['new']
    if results_object.generate_csv:
        output_type.append('csv')

    # TODO:
    """
    # TODO: PATH_BIPYPE

    # create tmp file with settings
    config_file_path = os.path.join(out_dir_path, 'meta.config')

    with open(config_file_path, 'w') as f:
        f.write(results_object.reference_condition + '\n')
        for the_file in results_object.files:
            # TODO: add conditions (how?)
            condition =
            # TODO: add R1 R2
            path = get_real_path(the_file)
            f.write(path)


    # feed bipype by subprocess with tmp file
    commands = [
        os.path.join(PATH_BIPYPE),
        '-metatr_config',
        config_file_path,
        '-metatr_output_type',
        output_type
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

    # seek for information about progress

    # be happy if job finished successfully
    """

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
