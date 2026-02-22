from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Job


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = [
            "id",
            "name",
            "payload",
            "schedule_type",
            "run_at",
            "interval_seconds",
            "max_retries",
            "retry_count",
            "status",
            "next_run_at",
            "created_at",
        ]
        read_only_fields = (
            "id",
            "retry_count",
            "status",
            "next_run_at",
            "created_at",
        )

    def validate(self, attrs):
        schedule_type = attrs.get("schedule_type")

        if schedule_type not in ("one_time", "interval"):
            raise serializers.ValidationError(
                {"schedule_type": "Must be 'one_time' or 'interval'."}
            )

        # -----------------------------
        # One-Time Job
        # -----------------------------
        if schedule_type == "one_time":
            run_at = attrs.get("run_at")

            if not run_at:
                raise serializers.ValidationError(
                    {"run_at": "run_at is required for one_time jobs."}
                )

            if run_at <= timezone.now():
                raise serializers.ValidationError(
                    {"run_at": "run_at must be in the future."}
                )

            # System-calculated execution time
            attrs["next_run_at"] = run_at

            # Ensure interval field is empty
            attrs["interval_seconds"] = None

        # -----------------------------
        # Interval Job
        # -----------------------------
        elif schedule_type == "interval":
            interval = attrs.get("interval_seconds")

            if interval is None:
                raise serializers.ValidationError(
                    {"interval_seconds": "Required for interval jobs."}
                )

            if interval <= 0:
                raise serializers.ValidationError(
                    {"interval_seconds": "Must be greater than 0."}
                )

            attrs["next_run_at"] = timezone.now() + timedelta(seconds=interval)

            # Ensure run_at not used
            attrs["run_at"] = None

        return attrs
