
import os
from readline import backend
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avis_agent.settings')

application = get_wsgi_application()
