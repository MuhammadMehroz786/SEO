import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seobot.settings")

app = Celery("seobot")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    from django.conf import settings
    config = getattr(settings, "CELERY_BEAT_SCHEDULE_CONFIG", {})
    beat_schedule = {}
    for name, entry in config.items():
        cron_kwargs = {k: v for k, v in entry.items() if k != "task"}
        beat_schedule[name] = {
            "task": entry["task"],
            "schedule": crontab(**cron_kwargs),
        }
    app.conf.beat_schedule = beat_schedule
