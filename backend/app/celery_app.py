from celery import Celery
from celery.schedules import crontab
import os

# Configuration Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

app = Celery(
    'voiture_search',
    broker=REDIS_URL,
    backend=REDIS_URL
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Paris',
    enable_utc=True,
    beat_schedule={
        'scrape-leboncoin-every-6h': {
            'task': 'app.tasks.scrape_leboncoin',
            'schedule': crontab(minute=0, hour='*/6'),  # Toutes les 6h
        },
        'scrape-lacentrale-every-6h': {
            'task': 'app.tasks.scrape_lacentrale',
            'schedule': crontab(minute=30, hour='*/6'),
        },
        'scrape-autoscout-every-6h': {
            'task': 'app.tasks.scrape_autoscout',
            'schedule': crontab(minute=0, hour='*/12'),  # Toutes les 12h
        },
    }
)