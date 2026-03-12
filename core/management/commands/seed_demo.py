from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from core.models import Application, Comment, Membership, Project, Task

class Command(BaseCommand):
    help = 'Populate a small demo dataset for GroupMatch.'

    def handle(self, *args, **options):
        Application.objects.all().delete()
        Comment.objects.all().delete()
        Task.objects.all().delete()
        Membership.objects.all().delete()
        Project.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        leader = User.objects.create_user(username='leader', email='leader@example.com', password='pass12345')
        student = User.objects.create_user(username='student', email='student@example.com', password='pass12345')
        designer = User.objects.create_user(username='designer', email='designer@example.com', password='pass12345')

        p1 = Project.objects.create(creator=leader, title='AI Study Buddy', description='Build a coursework support tool that recommends revision tasks and group milestones.', required_skills='Django, JavaScript, UX Research', recruitment_status='open')
        p2 = Project.objects.create(creator=leader, title='Campus Sustainability Dashboard', description='Create a small analytics web app for coursework teams analysing campus energy data.', required_skills='Python, Data Visualisation, Report Writing', recruitment_status='open')

        Membership.objects.create(user=leader, project=p1, role='leader')
        Membership.objects.create(user=leader, project=p2, role='leader')
        Membership.objects.create(user=designer, project=p1, role='member')

        Application.objects.create(applicant=student, project=p1, message='I can support frontend implementation and testing.')

        t1 = Task.objects.create(project=p1, title='Prepare wireframes', description='Draft task board and application approval wireframes for the report.', status='todo', created_by=leader)
        t1.assignees.add(designer)
        t2 = Task.objects.create(project=p1, title='Implement AJAX task move', description='Update task status asynchronously for a smoother board interaction.', status='doing', created_by=leader)
        t2.assignees.add(leader, designer)
        t3 = Task.objects.create(project=p1, title='Write accessibility notes', description='Document keyboard support, live region messaging and labels.', status='done', created_by=leader)
        t3.assignees.add(leader)

        Comment.objects.create(task=t2, author=leader, body='Remember to announce the status change to screen readers.')
        Comment.objects.create(task=t3, author=designer, body='Included focus-ring screenshots for the report.')

        self.stdout.write(self.style.SUCCESS('Demo data created.'))
