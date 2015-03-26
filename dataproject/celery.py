from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

from datetime import timedelta

#from traffic import tasks

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dataproject.settings')

app = Celery('dataproject')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(
    #CELERY_IMPORTS = ("traffic.tasks", ),
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
        'task': 'traffic.tasks.add',
        'schedule': timedelta(seconds=5),
        'args': (16, 16)
    },
}
)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))