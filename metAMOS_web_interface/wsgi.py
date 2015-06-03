"""
WSGI config for metAMOS_web_interface project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os, sys
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web')
sys.path.append('/home/pszczesny/soft/metAMOS_web_interface/metAMOS_web_interface')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metAMOS_web_interface.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
