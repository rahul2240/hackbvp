from app import app
import os
from celery import Celery

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
celery.conf.result_backend = app.config['CELERY_RESULT_BACKEND']
celery.conf.broker_transport_options = {
	'max_retries': 3,
	'interval_start': 0,
	'interval_step': 0.2,
	'interval_max': 0.2,
}