#!/usr/bin/env python
import os
import sys
import subprocess
from time import sleep
from paths import app_paths

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
from glob import glob
import gzip
from job_manager import JobManager
import re
from metadata import MetadataManager

SUBPROCESS_ENV = os.environ.copy()
SUBPROCESS_ENV['SHELL'] = '/bin/bash'


def update_progress(job, value):
    print "Progress: " + str(value)
    job.progress = value
    job.save()


def run_command(commands, job):

    base = os.path.basename(commands[0])
    tmp_base_path = os.path.join(app_paths.tmp, 'bipype_' + base)

    out_log = open(tmp_base_path + '.out', 'w')
    err_log = open(tmp_base_path + '.err', 'w')

    command = ' '.join(commands)

    if settings.DEBUG:
        print 'Running {0}:'.format(base)
        print '['
        print '\n'.join(commands)
        print ']'
    else:
        print command

    process = subprocess.Popen(
        command,
        env=SUBPROCESS_ENV,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=err_log
    )

    for line in iter(process.stdout.readline, ''):
        out_log.write(line)
        matched_progress = re.match('progress=(\d+)', line)
        if matched_progress:
            progress = matched_progress.group(1)
            update_progress(job, int(progress))

    return_code = process.poll()

    out_log.close()
    err_log.close()

    if return_code is None:
        print 'No return code for {0}. It might indicates unfinished ' \
              'execution, and broken standard output pipe'.format(base)
    elif return_code == 0:
        print '{0} finished with {1} return code'.format(base, return_code)
    else:
        print ('{0} finished with {1} return code;\n'
               'It probably indicates some errors.\n'
               'For more information, check following files:\n'
               '{2}\n{3}'.format(
                    base, return_code,
                    tmp_base_path + '.err',
                    tmp_base_path + '.out')
               )

    return return_code


def unpack_gz(source, destination):
    """
    Unpacks .gz file from source into destination 'in flight'.
    """
    with gzip.open(source, 'rb') as f_in, open(destination, 'w') as f_out:
        shutil.copyfileobj(f_in, f_out)


def unpack_libraries(libraries_paths, destination):
    """
    Extracts .gz files from 'libraries_paths' list into
    destination folder (without copying original .gz files to local).
    """

    unpacked_paths = []

    for packed_path in libraries_paths:

        packed_name = os.path.basename(packed_path)

        unpacked_name = packed_name[:-3]    # remove .gz from name
        unpacked_path = os.path.join(destination, unpacked_name)

        unpack_gz(packed_path, unpacked_path)

        unpacked_paths += [unpacked_path]

    return unpacked_paths


def get_paired_paths(sample_list):
    """
    Complies list of paths to samples, where elements are tuples containing
    pairs of reads. To match reads from given sample_list, this function looks
    for presence of _R1_ and _R2_ substrings in filenames.
    If the pair couldn't be created because there is missing
    complementary read - the existing one will be skipped.
    """
    catch_r = re.compile('_R\d_')

    bases = set(catch_r.sub('', x) for x in sample_list)
    r1 = filter(lambda x: '_R1_' in x, sample_list)
    r2 = filter(lambda x: '_R2_' in x, sample_list)

    r1_list = []
    r2_list = []

    for base in bases:

        try:
            r1_file = filter(lambda x: catch_r.sub('', x) == base, r1)[0]
            r2_file = filter(lambda x: catch_r.sub('', x) == base, r2)[0]

            r1_list.append(r1_file)
            r2_list.append(r2_file)

        except IndexError:
            # there is a missing read (R1 or R2) for the base, so skip this one.
            print 'Warning: missing read R1 or R2 for {0} base'.format(base)

    return r1_list, r2_list


def prepare_results_dirs(results_object):

    try:
        os.makedirs(results_object.input_dir)
        os.makedirs(results_object.output_dir)
        os.makedirs(results_object.run_dir)
    except OSError:

        name = results_object.path
        print 'Warning: Directories for {0} already exist'.format(name)


def prepare_metadata(results_object):
    metadata = MetadataManager()
    metadata.from_dict(results_object.libraries)
    metadata.discover_paths()
    return metadata


def run_metamos(job, results_object):
    """
    Args:
        results_object - an instance of SampleResults object
    """
    prepare_results_dirs(results_object)
    metadata = prepare_metadata(results_object)

    sample = results_object

    libraries_paths = metadata.get_column('paths')[0]

    paths_for_read_1, paths_for_read_2 = get_paired_paths(libraries_paths)

    assert len(paths_for_read_1) == len(paths_for_read_2)
    count = len(paths_for_read_1)

    update_progress(job, 5)

    project_dir = os.path.join(sample.run_dir, 'metAMOS')

    """
    In the first version we were initialising metAMOS with use of a list of
    FASTA files (something like '-1 file_1.fasta,file_2.fasta'); use of only
    '-1' parameter indicated that it were served as 'non-paired files of reads'.

    After rewriting daemon to use 'fastq' files as input, we changed this
    behaviour, so there are two lists of files, split by reads, in order defined
    by rule: file [x] on list one is complementary to file [x] on list two.

    This change forced us to introduce parameter '-i', which means 'insert size'
    which is needed to go through metAMOS initialization without error,
    since '-i' is obligatory when we are passing libraries with mated reads.

    Because we are using currently only 'Preprocess' step in metAMOS, we
    inspected what behaviour is this parameter responsible for in this step:

    In 'Preprocess', values derived from 'insert size' (it est mean and standard
    deviation) are used only with libraries in 'stff' format and this is not our
    case (currently we are using 'fastq'), hence we don't have to take care of
    this parameter - we only need to pass it. So let's pass list of 0:0,
    elements of length equal to the count of libraries.
    """
    commands = [
        os.path.join(app_paths.metAMOS, 'initPipeline'),
        '-1',
        ','.join(paths_for_read_1),
        '-2',
        ','.join(paths_for_read_2),
        '-d',
        project_dir,
        '-i',
        ','.join(['0:0'] * count)
    ]

    run_command(commands, job)

    update_progress(job, 30)

    skip = 'FindORFS,MapReads,Validate,Abundance,Annotate,Scaffold,Propagate,Classify'

    commands = [
        os.path.join(app_paths.metAMOS, 'runPipeline'),
        '-n',
        skip,
        # following two lines forces metAMOS to use our commands from .spec
        # files in place of an assembler, despite it really isn't an assembler
        '-a',
        'bipype_' + sample.type,
        '-d',
        project_dir
    ]

    run_command(commands, job)

    update_progress(job, 90)

    path_name = os.path.join(sample.run_dir, 'Assemble/out/*.html')
    krona_html = glob(path_name)

    # there should be exactly one krona *.html file in Assemble/out/
    assert len(krona_html) == 1

    shutil.copyfile(krona_html[0], sample.html_path)

    update_progress(job, 100)


def run_metatranscriptomics(job, results_object):
    """
    Args:
        results_object - an instance of MetaResults object
    """
    prepare_results_dirs(results_object)
    metadata = prepare_metadata(results_object)

    update_progress(job, 1)

    # create file with settings
    config_file_path = os.path.join(results_object.input_dir, 'meta.config')

    with open(config_file_path, 'w') as f:
        f.write(results_object.reference_condition)

        for library_row in metadata.rows:

            library = metadata.explain_row(library_row)

            # the same as: = library[metadata.column_index('library_id')]
            library_id = library['library_id']
            condition = results_object.conditions[library_id]

            library_paths = library['paths']

            r1_paths, r2_paths = get_paired_paths(library_paths)

            # if there are more than one pair of reads for library, its wrong
            assert len(r1_paths) == 1 and len(r2_paths) == 1

            source_pair = [r1_paths[0], r2_paths[0]]

            local_pair = unpack_libraries(source_pair, results_object.input_dir)

            # whitespaces are used as separators in metatranscriptomics
            # bipype config so they are not allowed as parts of filenames/paths.
            assert not filter(bool, map(re.compile('\s').match, local_pair))

            line = ' '.join(local_pair + [condition])
            f.write('\n' + line)

    update_progress(job, 4)

    output_type = 'both'

    # feed bipype by subprocess with tmp file
    commands = [
        app_paths.bipype,
        '--metatr_config',
        config_file_path,
        '--metatr_output_type',
        output_type,
        '--out_dir',
        results_object.output_dir
    ]

    update_progress(job, 5)

    run_command(commands, job)

    update_progress(job, 100)


if __name__ == '__main__':

    job_manager = JobManager(debug_mode=settings.DEBUG)
    job_manager.add_callback(run_metatranscriptomics, 'metatranscriptomics')
    job_manager.add_callback(run_metamos, 'default')

    while True:

        performed = job_manager.run_queued()

        if performed:
            sleep(1)
        else:
            # let's be more friendly for server if the queue was empty last time
            sleep(5)
