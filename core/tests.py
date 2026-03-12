import json
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from .models import Application, Membership, Project, Task

class ProjectModelTests(TestCase):
    def test_skill_list_splits_and_trims(self):
        user = User.objects.create_user(username='alice', password='pass12345')
        project = Project.objects.create(creator=user, title='AI Planner', description='x', required_skills='Python,  UX , SQL', recruitment_status='open')
        self.assertEqual(project.skill_list(), ['Python', 'UX', 'SQL'])

    def test_membership_unique_constraint(self):
        user = User.objects.create_user(username='bob', password='pass12345')
        project = Project.objects.create(creator=user, title='Systems Design', description='x', required_skills='Django', recruitment_status='open')
        Membership.objects.create(user=user, project=project, role='leader')
        with self.assertRaises(Exception):
            Membership.objects.create(user=user, project=project, role='member')

class ApplicationWorkflowTests(TestCase):
    def setUp(self):
        self.leader = User.objects.create_user(username='leader', password='pass12345')
        self.student = User.objects.create_user(username='student', password='pass12345')
        self.project = Project.objects.create(creator=self.leader, title='GroupMatch', description='demo', required_skills='Django, JS', recruitment_status='open')
        Membership.objects.create(user=self.leader, project=self.project, role='leader')

    def test_accepting_application_creates_membership(self):
        app = Application.objects.create(applicant=self.student, project=self.project, message='I can help with frontend.')
        self.client.login(username='leader', password='pass12345')
        response = self.client.post(reverse('application_decision', args=[app.pk]), {'decision': 'accept'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Membership.objects.filter(user=self.student, project=self.project).exists())
        app.refresh_from_db()
        self.assertEqual(app.status, 'accepted')

class TaskStatusAjaxTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='member', password='pass12345')
        self.project = Project.objects.create(creator=self.user, title='PM Tool', description='demo', required_skills='Planning', recruitment_status='open')
        Membership.objects.create(user=self.user, project=self.project, role='leader')
        self.task = Task.objects.create(project=self.project, title='Draft report', description='Finish PDF', created_by=self.user)

    def test_status_update_endpoint(self):
        self.client.login(username='member', password='pass12345')
        response = self.client.post(reverse('update_task_status', args=[self.task.pk]), data=json.dumps({'status': 'doing'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'doing')
