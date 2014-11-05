from flask.ext.testing import TestCase
from rankomatic import app, db
from rankomatic.config import test_config


class OTOrderBaseCase(TestCase):

    def create_app(self):
        app.config.from_object(test_config)
        self.db = db
        return app
