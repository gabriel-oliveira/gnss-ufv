from __future__ import absolute_import, unicode_literals
from celery import shared_task
from bernese.core.process_line import run_next

@shared_task
def task_run_next(process):
    run_next(process)