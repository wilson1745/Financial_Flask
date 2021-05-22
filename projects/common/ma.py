import logging

from flask_marshmallow import Marshmallow

log = logging.getLogger("projects")

ma_marshmallow = Marshmallow()
log.info("Init ma Marshmallow() sucessful")
