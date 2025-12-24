import os
from celery import Celery

#Set default django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogging_platform_api.settings')

app = Celery('blogginh_platform_api')

#Read config from Django settings, using a 'CELERY_' prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

#Look for tasks.py in all installed apps
app.autodiscover_tasks()