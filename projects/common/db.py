import logging

from flask_sqlalchemy import SQLAlchemy

log = logging.getLogger("projects")

db_sqlalchemy = SQLAlchemy()
log.info("Init db SQLAlchemy() sucessful")
