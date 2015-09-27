import os
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from metadata import MetadataManager
import job_manager
import forms
import results
from paths import encode, decode


def index(request):
    return render(request, 'index.html')


def new(request):

    form = forms.SelectSampleForm(request.POST or None)

    if form.is_valid():

        from models import SampleResults

        library_id = form.cleaned_data['library_id']
        type_of_analysis = form.cleaned_data['type_of_analysis']

        data = {
            'type': type_of_analysis,
            'library_ids': [library_id]
        }

        results_object = results.get_or_create(SampleResults, data)
        return result_redirect(results_object)

    else:

        messages = forms.errors_to_messages(form.errors)

        data = {'messages': messages,
                'form': form}

        return render(request, 'new_job.html', data)


def new_meta(request):

    form = forms.MetatranscriptomicsForm(request.POST or None)

    if form.is_valid():

        from models import MetaResults

        raw_data = request.POST
        conditions = {}

        for library_id in form.cleaned_data['library_ids']:
            conditions[library_id] = raw_data.get('conditions[%s]' % library_id)

        data = {'type': 'metatranscriptomics',
                'library_ids': form.cleaned_data['library_ids'],
                'conditions': conditions,
                'reference_condition': form.cleaned_data['reference_condition']}

        results_object = results.get_or_create(MetaResults, data)

        return result_redirect(results_object)

    else:

        messages = forms.errors_to_messages(form.errors)

        data = {'messages': messages,
                'form': form}

        return render(request, 'metatranscriptomics.html', data)


def remove(request):

    messages = []

    form = forms.RemoveResultsForm(request.POST or None)

    if form.is_valid():

        selected = form.cleaned_data['results_to_remove']

        if not selected:
            messages.append({
                'contents': 'Your have to select at least one sample',
                'type': 'info'
            })

        metadata = MetadataManager.from_file()

        for library_id in selected:

            success = results.remove_by_library_id(library_id)

            library = metadata.explain_row(metadata.get_row(library_id))

            name = library['library_name'] + ' (id: {0})'.format(library_id)

            if success:
                messages.append({
                    'title': 'Success!',
                    'contents': 'Results associated with {0} '
                                'have been removed'.format(name),
                    'type': 'success'
                })
            elif success is None:
                messages.append({
                    'title': 'Nothing to do!',
                    'contents': 'There are no results associated with '
                                '{0} in the database'.format(name),
                    'type': 'info'
                })
            else:
                messages.append({
                    'title': 'Operation failed',
                    'contents': 'Unable to remove results '
                                'associated with: {0}'.format(name),
                    'type': 'danger'
                })
    else:
        messages += forms.errors_to_messages(form.errors)

    data = {'messages': messages,
            'form': form}

    return render(request, 'remove.html', data)


def result_redirect(results_object):

    destination = '/biogaz/result/{path}/{type}'.format(
        path=encode(results_object.path),
        type=results_object.type)

    return HttpResponseRedirect(destination)


def get_status(request, path, type_of_analysis):
    import json
    path = decode(path)
    results_object = results.get_object(type=type_of_analysis, path=path)
    to_json = {'progress': job_manager.get_progress(results_object.job),
               'state': job_manager.get_job_state(results_object.job),
               'error': results_object.job.error}
    return HttpResponse(json.dumps(to_json), mimetype='application/json')


def show_html(file_path):
    with open(file_path) as f:
        html_source = f.read()
    return HttpResponse(html_source, content_type='text/html')


def result_html(request, path, type_of_analysis, file_path):
    results_object = results.get_object(type=type_of_analysis, path=path)
    absolute_path = os.path.join(results_object.output_dir, file_path)
    return show_html(absolute_path)


def result_download(request, path, type_of_analysis, file_path):
    import mimetypes
    results_object = results.get_object(type=type_of_analysis, path=path)
    absolute_path = os.path.join(results_object.output_dir, file_path)
    mime = mimetypes.guess_type(absolute_path)
    fsock = open(absolute_path, 'r')
    response = HttpResponse(fsock, mimetype=mime)

    return response


def wait(request, data):
    return render(request, 'wait.html', data)


def result_metatranscriptomics(request, results_object, data):

    file_list = results.get_list(
        results_object,
        skip=['meta.config', '.meta_tmp_results']
    )
    config = results.get_without_paths(results_object, 'meta.config')

    data['files'] = file_list
    data['config'] = config
    data['reference_condition'] = results_object.reference_condition

    return render(request, 'results_meta.html', data)


def result_bipype(request, results_object, data):

    results_metadata = MetadataManager.from_dict(results_object.libraries)

    data['krona_path'] = os.path.basename(results_object.html_path)
    data['library_name'] = results_metadata.get_column('library_name')[0]
    data['library_id'] = results_metadata.get_column('library_id')[0]

    return render(request, 'results_krona.html', data)


def result(request, path, type_of_analysis):

    path = decode(path)

    try:
        results_object = results.get_object(type=type_of_analysis, path=path)
    except ObjectDoesNotExist:
        # this case is possible if someone has deleted results related to given
        # sample, whereas another one tried then to refresh this view.
        # for this case, redirect to home
        return HttpResponseRedirect('/biogaz/')

    messages = []

    # generally, checks whether library information is up-to-data
    libraries_warnings = results.get_libraries_warnings(results_object)
    if libraries_warnings:
        messages += libraries_warnings

    data_table = results.create_meta_table(results_object)

    data = {
        'type_of_analysis': type_of_analysis,
        'analysis_name': forms.pretty_analysis_name(type_of_analysis),
        'data_table': data_table.render('', ''),
        'path': path,
        'messages': messages
    }

    state = job_manager.get_job_state(results_object.job)

    if state == 'done':

        if results_object.type == 'metatranscriptomics':
            return result_metatranscriptomics(request, results_object, data)
        else:
            return result_bipype(request, results_object, data)

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

        data['progress'] = progress
        data['state'] = state

        return wait(request, data)
