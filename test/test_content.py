from flask import url_for
from test import OTOrderBaseCase


class TestContent(OTOrderBaseCase):

    render_templates = False

    def test_landing(self):
        response = self.client.get(url_for('content.landing'))
        self.assert_status(response, 200)
        self.assert_template_used('landing.html')

    def test_about(self):
        response = self.client.get(url_for('content.about'))
        self.assert_status(response, 200)
        self.assert_template_used('about.html')
