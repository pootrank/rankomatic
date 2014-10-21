#! /usr/bin/env python

import sys
import bin.tasks

from rq import use_connection
from rq_scheduler import Scheduler
from datetime import datetime


if __name__ == '__main__':
    opt = sys.argv[-1]
    use_connection()
    scheduler = Scheduler()
    if opt == '--cancel':
        for job in scheduler.get_jobs():
            scheduler.cancel(job)
    else:
        scheduler.schedule(
            scheduled_time=datetime.now(),
            func=bin.tasks.remove_temp_datasets,
            args=[],
            kwargs={},
            interval=1800,
            result_ttl=500,
            repeat=None
        )
