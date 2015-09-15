import sys
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')

import job_manager
import forms
import helpers


def index(request):
    return render(request, 'index.html')


def new(request):

    form = forms.SelectSampleForm(request.POST or None)

    if form.is_valid():

        from models import SampleResults

        data = {'type': form.cleaned_data['type_of_analysis'],
                'path': form.cleaned_data['selected_sample']}

        try:
            results_object = SampleResults.objects.get(**data)
        except ObjectDoesNotExist:
            results_object = SampleResults.objects.create(**data)

        return result_redirect(request, results_object)

    else:

        messages = helpers.errors_to_messages(form.errors)

        data = {'messages': messages,
                'form': form}

        return render(request, 'new_job.html', data)


def new_meta(request):

    form = forms.MetatranscriptomicsForm(request.POST or None)

    if form.is_valid():

        from paths import PATH_METATR_OUT_DIR
        from models import MetaResults

        raw_data = dict(request.POST)
        conditions = {}

        for meta_file in form.cleaned_data['selected_files']:
            conditions[meta_file] = raw_data['conditions[%s]' % meta_file]

        data = {'type': 'metatranscriptomics',
                'files': form.cleaned_data['selected_files'],
                'conditions': conditions,
                'reference_condition': form.cleaned_data['reference_condition']}

        try:
            results_object = MetaResults.objects.get(**data)

        except ObjectDoesNotExist:
            # let's create unique but not so long name dir for our output
            data['path'] = helpers.make_unique_dir(PATH_METATR_OUT_DIR)
            results_object = MetaResults.objects.create(**data)

        return result_redirect(request, results_object)

    else:

        messages = helpers.errors_to_messages(form.errors)

        data = {'messages': messages,
                'form': form}

        return render(request, 'metatranscriptomics.html', data)


def remove(request):

    messages = []

    form = forms.RemoveSampleForm(request.POST or None)

    if form.is_valid():

        selected = form.cleaned_data['samples_to_remove']

        if not selected:
            messages.append({
                'contents': 'Your have to select at least one sample',
                'type': 'info'
            })

        for sample_name in selected:

            results_data = {'path': sample_name}
            success = helpers.remove_results_by_data(**results_data)

            if success:
                messages.append({
                    'title': 'Success!',
                    'contents': 'Results associated with {0} '
                                'have been removed'.format(sample_name),
                    'type': 'success'
                })
            elif success is None:
                messages.append({
                    'title': 'Nothing to do!',
                    'contents': 'There are no results associated with '
                                '{0} in the database'.format(sample_name),
                    'type': 'info'
                })
            else:
                messages.append({
                    'title': 'Operation failed',
                    'contents': 'Unable to remove results '
                                'associated with: {0}'.format(sample_name),
                    'type': 'danger'
                })
    else:
        messages += helpers.errors_to_messages(form.errors)

    data = {'messages': messages,
            'form': form}

    return render(request, 'remove.html', data)


def result_redirect(request, results_object):

    destination = '/biogaz/result/{path}/{type}'.format(
        path=helpers.encode_path(results_object.path),
        type=results_object.type)

    return HttpResponseRedirect(destination)


def get_status(request, path, type_of_analysis):
    import json
    path = helpers.decode_path(path)
    results_object = helpers.get_results_object(type=type_of_analysis, path=path)
    to_json = {'progress': job_manager.get_progress(results_object.job),
               'state': job_manager.get_job_state(results_object.job),
               'error': results_object.job.error}
    return HttpResponse(json.dumps(to_json), mimetype='application/json')


def show_html(file_path):
    with open(file_path) as f:
        html_source = f.read()
    return HttpResponse(html_source, content_type='text/html')


def wait(request, data):
    return render(request, 'wait.html', data)


def result(request, path, type_of_analysis):

    path = helpers.decode_path(path)

    try:
        results_object = helpers.get_results_object(type=type_of_analysis,
                                                    path=path)
    except ObjectDoesNotExist:
        # this case is possible if someone has deleted results related to given
        # sample, whereas another one tried then to refresh this view.
        # for this case, redirect to home
        return HttpResponseRedirect('/biogaz/')

    state = job_manager.get_job_state(results_object.job)

    if state == 'done':

        return show_html(results_object.html_path)

    else:

        if state == 'not in database':

            results_object.job = job_manager.create_job()
            results_object.save()
            state = 'queued'

        elif state == 'failed':

            job_manager.remove_job(results_object.job)
            results_object.job = job_manager.create_job()
            results_object.save()
            state = 'requeued'

        progress = job_manager.get_progress(results_object.job)

        data = {'path': helpers.encode_path(path),
                'type_of_analysis': type_of_analysis,
                'progress': progress,
                'state': state}

        return wait(request, data)
