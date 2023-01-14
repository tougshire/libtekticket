from django.test import  SimpleTestCase, TestCase, Client
from ..forms import ProjectForm
from ..models import Project, StatusUpdate
from django.urls import reverse
from django.contrib.auth import get_user_model

class ViewTests(TestCase):

    fixtures=[]

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='admin', password='admin', is_superuser=True)

    def test_project_list_view(self):
        client = Client()
        response = client.get('/prosdib/projects/')
        self.assertEqual(response.status_code, 200)

    def test_project_detail_view(self):
        Project.objects.create()
        client = Client()
        response = client.get('/prosdib/project/1/')
        self.assertEqual(response.status_code, 200)

    def test_get_project_create_view_no_auth(self):
        client = Client()
        response = client.get('/prosdib/project/create/')
        self.assertEqual(response.status_code, 302)

    def test_get_project_create_view(self):
        client = Client()
        client.login(username='admin', password='admin')
        response = client.get('/prosdib/project/create/')
        self.assertEqual(response.status_code, 200)


    def test_get_project_detail_view(self):
        client = Client()
        project = Project.objects.create()
        ppk = project.pk
        response = client.get(f'/prosdib/project/{ppk}/')
        self.assertEqual(response.status_code, 200)

    def test_project_detail_name(self):
        client = Client()
        project = Project.objects.create()
        ppk = project.pk
        self.assertEqual(reverse('prosdib:project_detail', kwargs={'pk':ppk}), f'/prosdib/project/{ppk}/')


    def test_post_project_create_view_no_auth(self):
        client = Client()
        Project.objects.filter(name="Test Project").delete()
        response = client.post('/prosdib/project/create/', {'name': 'Test Project', 'start': '1/1/2021'})
        project_count = Project.objects.filter(name="Test Project").count()
        self.assertEqual(project_count, 0)

    def test_post_project_create_view(self):
        client = Client()
        client.login(username='admin', password='admin')
        Project.objects.filter(name="Test Project").delete()
        response = client.post('/prosdib/project/create/', {'name': 'Test Project', 'start': '1/1/2021'})
        project_count = Project.objects.filter(name="Test Project").count()
        self.assertEqual(project_count, 1)

    def test_get_project_update_view_no_auth(self):
        client = Client()
        project = Project.objects.create( name='Test Project' )
        response = client.get(f'/prosdib/project/{project.pk}/update/')
        self.assertEqual(response.status_code, 302)

    def test_get_project_update_view(self):
        client = Client()
        client.login(username='admin', password='admin')
        project = Project.objects.create( name='Test Project' )
        response = client.get(f'/prosdib/project/{project.pk}/update/')
        self.assertEqual(response.status_code, 200)


    def test_post_project_update_view_no_auth(self):
        client = Client()
        project = Project.objects.create( name='Project before post' )
        ppk = project.pk
        response = client.post(f'/prosdib/project/{ ppk }/update/', {'name': 'Project after post', 'start': '1/2/2021'})
        project = Project.objects.get( pk=ppk )
        self.assertEqual(project.name, 'Project before post')

    def test_post_project_update_view_auth(self):
        client = Client()
        client.login(username='admin', password='admin')
        project = Project.objects.create( name='Project before post' )
        ppk = project.pk
        response = client.post(f'/prosdib/project/{ ppk }/update/', {'name': 'Project after post', 'start': '1/2/2021'})
        project = Project.objects.get( pk=ppk )
        self.assertEqual(project.name, 'Project after post')

    def test_post_project_created_by(self):
        client = Client()
        client.login(username='admin', password='admin')
        response = client.post(f'/prosdib/project/create/', {'name': 'New Project', 'start': '1/2/2021'})
        self.assertEqual(Project.objects.get(name='New Project').created_by, get_user_model().objects.get(username="admin") )

class ProjectCreatestatusupdateFormsetTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.superuser = get_user_model().objects.create_user(
            username = "superone",
            password = "TestSuper#1",
            is_superuser = True
        )

    def test_project_post_with_statusupdate_create_with_superuser(self):
        c = Client()
        c.login(username = "superone", password="TestSuper#1")
        response = c.post('/prosdib/project/create/', {
            'name':'Project One',
            'start':'1/1/2021',
            'statusupdate_set-TOTAL_FORMS':3,
            'statusupdate_set-INITIAL_FORMS':0,
            'statusupdate_set-MIN_NUM_FORMS':0,
            'statusupdate_set-MAX_NUM_FORMS':0,
            'statusupdate_set-0-when':'2021-11-19',
            'initial-statusupdate_set-0-when':'2021-11-19',
            'statusupdate_set-0-maintext':'Project Update One',
            'statusupdate_set-1-when':'2021-11-19',
            'initial-statusupdate_set-1-when':'2021-11-19',
            'statusupdate_set-1-maintext':'',
            'statusupdate_set-2-when':'2021-11-19',
            'initial-statusupdate_set-2-when':'2021-11-19',
            'statusupdate_set-2-maintext':'',
        })
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(StatusUpdate.objects.count(), 1)
        self.assertEqual(StatusUpdate.objects.first().project.pk, Project.objects.first().pk)

class ProjectUpdatestatusupdateFormsetTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.superuser = get_user_model().objects.create_user(
            username = "superone",
            password = "TestSuper#1",
            is_superuser = True
        )
        cls.project_one = Project.objects.create(
            name = 'Project one'
        )
        cls.statusupdate_one = StatusUpdate.objects.create(
            project = cls.project_one,
            maintext = 'Project Note One',
        )

    def test_project_post_with_statusupdate_update_with_superuser(self):
        c = Client()
        c.login(username = "superone", password="TestSuper#1")
        response = c.post('/prosdib/project/' + str(self.project_one.pk) + '/update/', {
            'name':'Project One Updated',
            'start':'1/1/2001',
            'statusupdate_set-TOTAL_FORMS':4,
            'statusupdate_set-INITIAL_FORMS':1,
            'statusupdate_set-MIN_NUM_FORMS':0,
            'statusupdate_set-MAX_NUM_FORMS':0,
            'statusupdate_set-0-id':self.statusupdate_one.pk,
            'statusupdate_set-0-project':self.project_one.pk,
            'statusupdate_set-0-when':'2021-11-19',
            'initial-statusupdate_set-0-when':'2021-11-19',
            'statusupdate_set-0-maintext':'Project Note One Updated',

            'statusupdate_set-1-Project':self.project_one.pk,
            'statusupdate_set-1-when':'2021-11-19',
            'initial-statusupdate_set-1-when':'2021-11-19',
            'statusupdate_set-1-maintext':'Project Note Two',

            'statusupdate_set-2-Project':self.project_one.pk,
            'statusupdate_set-2-when':'2021-11-19',
            'initial-statusupdate_set-2-when':'2021-11-19',
            'statusupdate_set-2-maintext':'',
            'statusupdate_set-3-when':'2021-11-19',
            'initial-statusupdate_set-3-when':'2021-11-19',
            'statusupdate_set-3-maintext':'',
        })
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(StatusUpdate.objects.count(), 2)
        self.assertEqual(StatusUpdate.objects.first().project.pk, Project.objects.first().pk)
        self.assertEqual(StatusUpdate.objects.all()[1].project.pk, Project.objects.first().pk)
