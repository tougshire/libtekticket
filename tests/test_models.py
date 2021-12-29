from django.test import TestCase
from ..models import Project, StatusUpdate
from django.contrib.auth import get_user_model

class ProjectTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_one = get_user_model().objects.create(
            username="userone"
        )
        cls.project_one = Project.objects.create(
            name="project one"
        )
        cls.statusupdate_one = StatusUpdate.objects.create(
            project = cls.project_one,
            text = 'Update to Project One'
        )

    def test_project_str_is_name(self):
        self.assertEqual(self.project_one.__str__(), self.project_one.name)

    def test_statsupdate_str_is_project_name_and_date(self):
        self.assertEqual(self.statusupdate_one.__str__(), f'{self.project_one} / {self.statusupdate_one.when}')

    def test_statusupdate_is_in_project_statusupdate_set(self):
        self.assertEqual(self.project_one.statusupdate_set.count(), 1)
