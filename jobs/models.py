import uuid
from django.db import models


class Job(models.Model):

    STATUS_CHOICES = [
        ("SCHEDULED", "Scheduled"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    SCHEDULE_TYPE_CHOICES = [
        ("one_time", "One Time"),
        ("interval", "Interval"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    payload = models.JSONField()

    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPE_CHOICES)
    run_at = models.DateTimeField(null=True, blank=True)
    interval_seconds = models.IntegerField(null=True, blank=True)

    max_retries = models.IntegerField(default=3)
    retry_count = models.IntegerField(default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="SCHEDULED")

    next_run_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "next_run_at"]),
        ]


# Job execution model

class JobExecution(models.Model):

    STATUS_CHOICES = [
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="executions")

    attempt_number = models.IntegerField()

    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(null=True, blank=True)
