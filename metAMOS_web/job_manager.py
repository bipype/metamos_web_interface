from metAMOS_web.models import Job
import traceback


def refresh_job_object(job):
    """
    Refresh instance of Job object from database.

    In future (after update to Django 1.8, this should be replaced by better
    job.refresh_from_db(), but in Django 1.4 this method is unavailable)
    """
    return Job.objects.get(id=job.id)


def get_progress(job):
    """
    Return progress of given job or 0 if job object is not initialized yet.
    """

    try:
        progress = job.progress
    except AttributeError:
        progress = 0

    return progress


def create_job():
    """
    Create and save a Job object. Since argument 'started' is by default set to
    False, created job becomes immediately a part of the queue which is nothing
    more, than a result of filter(started=False) imposed on all job objects.
    """
    job = Job.objects.create()
    return job


def remove_job(job):
    """
    Remove job object from database (if it exists).
    """
    job.delete()


def get_job_state(job):
    """
    Checks state of a job and returns nice, readable feedback.

    Args:
        job - A Job object

    Returns:
        A string with information about state of job, one of following:
        done, waiting, running, not in database, failed
    """

    if job:

        job = refresh_job_object(job)

        if job.error:
            state = 'failed'

        elif job.completed:
            state = 'done'

        elif job.started:
            state = 'running'

        else:
            state = 'waiting'

    else:
        state = 'not in database'

    return state


class JobManager(object):

    lack_cb_template = 'Job manager has neither generic ("default"), ' \
                       'nor specific callback for {0} job type.'

    def __init__(self):
        self.callbacks = {}

    def add_callback(self, callback_function, results_type='default'):
        self.callbacks[results_type] = callback_function

    def run(self, job):
        """
        Runs function which will perform task appropriate to given job.

        In case of any exception, adds information about it to 'error' field in
        job object, and reverts all changes to state which was on the beginning
        (on level which is guaranteed by try... except construction).
        """
        try:
            job.started = True
            job.save()

            results = job.results.cast()

            if results.type in self.callbacks:
                callback = self.callbacks[results.type]
            else:
                callback = self.callbacks.get('default', None)

                if not callback:
                    raise KeyError(self.lack_cb_template.format(results.type))

            callback(job=job, results_object=results)

            job.completed = True
            job.save()

        except SystemExit:

            job.error = "Daemon execution terminated by system exit"

        except Exception as error:

            feedback = error.message + '\n\n'
            feedback += traceback.format_exc()

            print feedback
            job.error = feedback

        job.save()

    def run_queued(self):
        """
        Checks whether there are Job objects in database, which are not started yet
        (aka: in queue) and runs execution of first job from these objects.

        Returns True if a job has been started and False otherwise
        (to indicate, that currently there are no jobs queued).
        """
        job_queue = Job.objects.filter(started=False)

        if job_queue:

            job = job_queue[0]
            self.run(job)

            return True
        else:
            return False
