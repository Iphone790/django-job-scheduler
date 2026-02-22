import time
import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from jobs.models import Job


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Runs background job worker"

    POLL_INTERVAL = 5
    BATCH_SIZE = 5

    def handle(self, *args, **options):
        self.recover_running_jobs()

        while True:
            try:
                self.process_jobs()
            except Exception as exc:
                logger.exception("Worker loop crashed: %s", exc)

            time.sleep(self.POLL_INTERVAL)

    # ----------------------------------------
    # Crash Recovery
    # ----------------------------------------

    def recover_running_jobs(self):
        updated = Job.objects.filter(status="RUNNING").update(
            status="SCHEDULED"
        )
        if updated:
            print(f"[{timezone.now()}] Recovered {updated} RUNNING job(s)")

    # ----------------------------------------
    # Job Processing
    # ----------------------------------------

    def process_jobs(self):
        jobs = self.fetch_due_jobs()

        for job in jobs:
            self.execute_job(job)

    def fetch_due_jobs(self):
        with transaction.atomic():
            jobs = (
                Job.objects
                .select_for_update(skip_locked=True)
                .filter(
                    status="SCHEDULED",
                    next_run_at__lte=timezone.now()
                )
                .order_by("next_run_at")[: self.BATCH_SIZE]
            )

            for job in jobs:
                print(
                    f"[{timezone.now()}] "
                    f"Job {job.id} | Task: {job.name} | "
                    f"Status: SCHEDULED | Received at: {job.next_run_at}"
                )

                job.status = "RUNNING"
                job.save(update_fields=["status"])

                print(
                    f"[{timezone.now()}] "
                    f"Job {job.id} | Task: {job.name} | "
                    f"Status changed → RUNNING"
                )

            return list(jobs)

    # ----------------------------------------
    # Execution Logic
    # ----------------------------------------

    def execute_job(self, job: Job):
        try:
            self.perform_job_logic(job)
            self.handle_success(job)

        except Exception:
            self.handle_failure(job)

    def perform_job_logic(self):
        time.sleep(2)

    # ----------------------------------------
    # Success / Failure Handling
    # ----------------------------------------

    def handle_success(self, job: Job):
        if job.schedule_type == "interval":
            job.status = "SCHEDULED"
            job.next_run_at = timezone.now() + timedelta(
                seconds=job.interval_seconds
            )
            job.retry_count = 0
        else:
            job.status = "COMPLETED"

        job.save(update_fields=["status", "next_run_at", "retry_count"])

        print(
            f"[{timezone.now()}] "
            f"Job {job.id} | Task: {job.name} | "
            f"Status changed → {job.status}"
        )

    def handle_failure(self, job: Job):
        job.retry_count += 1

        if job.retry_count >= job.max_retries:
            job.status = "FAILED"
        else:
            job.status = "SCHEDULED"
            delay = job.interval_seconds or 10
            job.next_run_at = timezone.now() + timedelta(seconds=delay)

        job.save(update_fields=["status", "retry_count", "next_run_at"])

        print(
            f"[{timezone.now()}] "
            f"Job {job.id} | Task: {job.name} | "
            f"Status changed → {job.status}"
        )
