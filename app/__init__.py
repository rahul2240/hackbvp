from flask import Flask
import logging

app = Flask(__name__)
app.config.from_object("config")

from app import apis


if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)