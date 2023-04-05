import csv
from io import StringIO
from django.test import TestCase
from .models import Report


class ApiTest(TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def test_get_report(self):
        fp = StringIO()
        writer = csv.writer(fp)
        writer.writerow(["test", "test"])
        writer.writerow(["test1", "test1"])
        writer.writerow(["test2", "test2"])
        fp.seek(0)
        report = Report.objects.create(csv=fp.read(), generated=True)
        res = self.client.post("/get_report/", data={
            'report_id': report.id
        }, content_type='application/json')
        fp.seek(0)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content.decode(), fp.read())