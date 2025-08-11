from collections.abc import Sequence

from arq.cron import CronJob, cron
from arq.typing import WorkerCoroutine
from arq.worker import Function

from finnikacc_api.arqjobs.fetchrates import fetch_conv_rates_oex

arq_functions: Sequence[WorkerCoroutine | Function] = []

arq_cron_jobs: Sequence[CronJob] = [
    cron(fetch_conv_rates_oex, hour=set(range(24)), minute=4, run_at_startup=True, timeout=60),
]
