import os
import sys
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')

import daemon
import forms
import helpers


# main page
def index(request):
    return render(request, 'index.html')


# amplicon results
def new(request, messages=[]):
    form = forms.SelectSampleForm()
    data = {'messages': messages,
            'form': form}
    return render(request, 'new_job.html', data)


# view for testing
def test(request):
    form = forms.MetatranscriptomicsForm()
    return render(request, 'testing_template.html', {'form': form})


def remove(request):
    form = forms.RemoveSampleForm()

    messages = []

    if request.method == "POST":
        # take care of response

        # Since construction of our widgets is slightly different, than
        # construction of default ones** and validators are hardcoded for
        # default widgets without other way to replace them than by subclassing
        # *ChoiceField classes which would be redundant and ugly, validation
        # is performed here without use of form.is_valid() function.

        # ** in BootstrapTableWidgets there are multiple columns allowed (so,
        # items in .choices could be of any length) but the default widget
        # (Select) always uses items with at most 2 elements in .choices
        # and if there are 2 - they are treated as a group of options.

        choices = form.fields['samples_to_remove'].widget.get_valid_choices()
        selected = dict(request.POST).get('samples_to_remove', [])

        if not selected:
            messages.append({
                'contents': 'Your have to select at least one sample',
                'type': 'info'
            })

        for sample_name in selected:

            if sample_name in choices:

                # TODO: removing results by 'sample_name'
                # (following line is only a placeholder)
                success = True

                if success:
                    messages.append({
                        'title': 'Success!',
                        'contents': '{0} removed'.format(sample_name),
                        'type': 'success'
                    })
                else:
                    messages.append({
                        'contents': 'Unable to remove: {0}'.format(sample_name),
                        'type': 'danger'
                    })
            else:
                messages.append({
                    'contents': "Sample {0} doesn't exists".format(sample_name),
                    'type': 'warning'
                })

    data = {'messages': messages,
            'form': form}

    return render(request, 'remove.html', data)


def result_redirect(request):
    # if sample wasn't selected, show the form again, with warning this time
    if 'selected_sample' not in request.GET:
        warning = {
            'contents': 'Your have to select a sample',
            'type': 'info'
        }
        return new(request, messages=[warning])
    sample_source, sample_id = request.GET['selected_sample'].split('/')
    bipype_variant = 'bipype_' + request.GET['selected_bipype_variant'] + '_' + sample_source.lower()
    return HttpResponseRedirect('/biogaz/result/' + sample_id + '/' + bipype_variant)


def get_status(request, sample_id, type_of_analysis):
    import json
    progress = helpers.get_progress(sample=sample_id, variant=type_of_analysis)
    to_json = {'status': progress}
    return HttpResponse(json.dumps(to_json), mimetype='application/json')


def result(request, sample_id, type_of_analysis):

    progress = helpers.get_progress(sample=sample_id, variant=type_of_analysis)

    data = {'sample_id': sample_id,
            'type_of_analysis': type_of_analysis,
            'progress': progress}

    output_dir = helpers.get_output_dir(sample_id, type_of_analysis)
    krona_xml_path, krona_html_path = helpers.get_krona_paths(output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        daemon.check_and_add_sample(sample_id, type_of_analysis)
        return render(request, 'wait.html', data)
    else:
        if not os.path.exists(krona_xml_path):
            daemon.check_and_add_sample(sample_id, type_of_analysis)
            return render(request, 'wait.html', data)
        else:
            if not os.path.exists(krona_html_path):
                helpers.create_krona_html(krona_xml_path, krona_html_path)
            with open(krona_html_path) as f:
                html_source = f.read()
        return HttpResponse(html_source, content_type='text/html')
