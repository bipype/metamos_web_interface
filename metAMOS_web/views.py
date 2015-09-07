import os
import sys
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')

import daemon
from paths import SAMPLE_PATH, OUTPUT_ANALYSES_PATH
import forms

#with open('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web/krona-2.0.js') as f:
#    KRONA_JS_SRC = f.read()


KRONA_HTML_PREFIX = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
        <head>
                <meta charset="utf-8"/>
                <style>
                        body
                        {
                                margin:0;
                        }
                </style>
        </head>

        <body style="padding:0;position:relative">
                <div id="options" style="position:absolute;left:0;top:0">
                </div>

                <div id="details" style="position:absolute;top:1%;right:2%;text-align:right;">
                </div>

                <canvas id="canvas" width="100%" height="100%">
                        This browser does not support HTML5 (see
                        <a href="http://sourceforge.net/p/krona/wiki/Browser%20support/">
                                Krona browser support</a>).
                </canvas>

                <img id="hiddenImage" src="http://krona.sourceforge.net/img/hidden.png" visibility="hide"/>
                <script name="tree" src="http://krona.sourceforge.net/krona-1.1.js"></script>
        </body>

        <data>
"""

KRONA_HTML_POSTFIX = """
</body></data></html>
"""


# Create your views here.
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
            'contents': 'Your have to select at least one sample',
            'type': 'info'
        }
        return new(request, messages=[warning])
    sample_source, sample_id = request.GET['selected_sample'].split('/')
    bipype_variant = 'bipype_' + request.GET['selected_bipype_variant'] + '_' + sample_source.lower()
    return HttpResponseRedirect('/biogaz/result/' + sample_id + '/' + bipype_variant)

def result(request, sample_id, bipype_variant):
    sample_source = bipype_variant.split('_')[-1].upper()
    output_path = os.path.join(SAMPLE_PATH[sample_source], sample_id.rstrip('.fastq'), 'bipype_output', bipype_variant)
    krona_xml_path = os.path.join(SAMPLE_PATH[sample_source], sample_id, 'bipype_output', bipype_variant + '/krona.html')
    krona_html_path = os.path.join(SAMPLE_PATH[sample_source], sample_id, 'bipype_output', bipype_variant + '/krona.xml.html')
    if os.path.exists(krona_html_path):
        os.remove(krona_html_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        daemon.check_and_add_sample(sample_id, bipype_variant)
        return render(request, 'wait.html')
    else:
        if not os.path.exists(krona_xml_path):
            daemon.check_and_add_sample(sample_id, bipype_variant)
            return render(request, 'wait.html')
        else:
            os.system(
                    'PERL5LIB=/home/pszczesny/soft/metAMOS-1.5rc3/Utilities/krona /home/pszczesny/soft/metAMOS-1.5rc3/Utilities/krona/ImportXML.pl' + \
                            krona_xml_path + ' -o ' + krona_html_path
                    )
            with open(krona_html_path) as f:
                html_source = f.read()
        return HttpResponse(html_source, content_type='text/html')

# show files from output_analys
def show_krona_list(request):
    krona_list = [i for i in os.listdir(OUTPUT_ANALYSES_PATH) if 'krona' in i]
    return render(request, 'output_analyses.html', {'krona_list': krona_list})

def show_single_krona(request, krona_name):
    krona_xml_path = os.path.join(OUTPUT_ANALYSES_PATH, krona_name)
    krona_html_path = os.path.join(OUTPUT_ANALYSES_PATH, krona_name + '.xml.html')
    #if os.path.exists(krona_html_path):
    #    os.remove(krona_html_path)
    os.system(
            'PERL5LIB=/home/pszczesny/soft/metAMOS-1.5rc3/Utilities/krona /home/pszczesny/soft/metAMOS-1.5rc3/Utilities/krona/ImportXML.pl' + \
                    krona_xml_path + ' -o ' + krona_html_path
            )
    with open(krona_html_path) as f:
        html_source = f.readlines()
    return HttpResponse(html_source, content_type='text/html')

