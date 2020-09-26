from __future__ import absolute_import, unicode_literals
from celery import shared_task
from bernese.core.process_line import run_next

@shared_task(bind=True)
def task_run_next(self):
    status, result = run_next(int(self.request.id))
    if not status:
        raise Exception(result)
        
