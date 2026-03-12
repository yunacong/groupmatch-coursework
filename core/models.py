from django.conf import settings
from django.db import models
from django.utils import timezone

class Project(models.Model):
    STATUS_CHOICES = [('open', 'Open'), ('closed', 'Closed')]

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_projects')
    title = models.CharField(max_length=120)
    description = models.TextField()
    required_skills = models.CharField(max_length=250, help_text='Comma-separated skills, e.g. Python, UI Design, Report Writing')
    recruitment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def skill_list(self):
        return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]

    def is_leader(self, user):
        return self.memberships.filter(user=user, role='leader').exists()

    def is_member(self, user):
        return self.memberships.filter(user=user).exists()

class Membership(models.Model):
    ROLE_CHOICES = [('leader', 'Leader'), ('member', 'Member')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')
        ordering = ['joined_at']

    def __str__(self):
        return f'{self.user.username} - {self.project.title} ({self.role})'

class Application(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')]

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='applications')
    message = models.TextField(max_length=500)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    apply_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('applicant', 'project')
        ordering = ['-apply_date']

    def __str__(self):
        return f'{self.applicant.username} → {self.project.title} ({self.status})'

class Task(models.Model):
    STATUS_CHOICES = [('todo', 'To Do'), ('doing', 'In Progress'), ('done', 'Completed')]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=120)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='todo')
    due_date = models.DateField(null=True, blank=True)
    assignees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='tasks', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'title']

    def __str__(self):
        return f'{self.project.title}: {self.title}'

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.task.title}'
